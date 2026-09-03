import { useEffect, useRef, useState } from 'react'
import mqtt from 'mqtt'
import { TOPICS, SUBSCRIPTION_TOPICS, SENSOR_BY_TOPIC } from '../topics.js'

const USE_MOCK = String(import.meta.env.VITE_USE_MOCK_DATA).toLowerCase() === 'true'
const MQTT_URL = import.meta.env.VITE_MQTT_URL
const MQTT_USERNAME = import.meta.env.VITE_MQTT_USERNAME
const MQTT_PASSWORD = import.meta.env.VITE_MQTT_PASSWORD
const MQTT_CLIENT_PREFIX = import.meta.env.VITE_MQTT_CLIENT_PREFIX ?? 'edificio_dashboard'
const API_URL = import.meta.env.VITE_API_URL

const SENSOR_KEYS = ['temperatura', 'humedad', 'gas', 'distancia', 'luz']
const MAX_HISTORY_POINTS = 60

const emptyHistory = () =>
  SENSOR_KEYS.reduce((acc, key) => {
    acc[key] = []
    return acc
  }, {})

const initialBuilding = {
  sensors: { temperatura: null, humedad: null, gas: null, distancia: null, luz: null },
  actuators: {
    puerta: 'CERRADA',
    luces: false,
    modo_iluminacion: 'AUTOMATICO',
    ventilador: false,
    alarma: false,
  },
  status: 'NORMAL',
  arm64: { max: null, min: null, avg: null, count: null },
}

function formatLabel(date) {
  return new Intl.DateTimeFormat('es-GT', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(date)
}

function pushHistoryPoint(history, sensorKey, value) {
  const next = { ...history }
  const points = [...(next[sensorKey] ?? [])]
  points.push({ label: formatLabel(new Date()), value })
  if (points.length > MAX_HISTORY_POINTS) points.shift()
  next[sensorKey] = points
  return next
}

async function fetchJSON(url) {
  const res = await fetch(url)
  if (!res.ok) throw new Error(`${url} -> ${res.status}`)
  return res.json()
}

export function useBuildingData() {
  const [building, setBuilding] = useState(initialBuilding)
  const [history, setHistory] = useState(emptyHistory)
  const [events, setEvents] = useState([])
  const [commands, setCommands] = useState([])
  const [connection, setConnection] = useState(USE_MOCK ? 'simulated' : 'connecting')
  const [lastUpdate, setLastUpdate] = useState(new Date())
  const clientRef = useRef(null)

  // --- Carga inicial de historial / eventos / comandos desde la API REST ---
  // (la API lee MongoDB Atlas; ver backend/api.py). Si la API todavía no
  // está corriendo, el dashboard sigue funcionando solo con datos en vivo.
  useEffect(() => {
    if (!API_URL) return
    let cancelled = false

    ;(async () => {
      try {
        const [eventsData, commandsData, arm64Data] = await Promise.all([
          fetchJSON(`${API_URL}/events?limit=20`),
          fetchJSON(`${API_URL}/commands?limit=20`),
          fetchJSON(`${API_URL}/arm64/latest`),
        ])
        if (cancelled) return
        setEvents(eventsData)
        setCommands(commandsData)
        if (arm64Data) {
          setBuilding((prev) => ({ ...prev, arm64: arm64Data }))
        }

        const historyEntries = await Promise.all(
          SENSOR_KEYS.map((key) =>
            fetchJSON(`${API_URL}/readings/${key}?limit=${MAX_HISTORY_POINTS}`).catch(() => []),
          ),
        )
        if (cancelled) return
        setHistory((prev) => {
          const next = { ...prev }
          SENSOR_KEYS.forEach((key, i) => {
            next[key] = historyEntries[i].map((point) => ({
              label: formatLabel(new Date(point.timestamp)),
              value: point.value,
            }))
          })
          return next
        })
      } catch (err) {
        // No es crítico: el dashboard sigue funcionando solo con MQTT en vivo.
        console.warn('No se pudo cargar el historial desde la API:', err)
      }
    })()

    return () => {
      cancelled = true
    }
  }, [])

  // --- Conexión MQTT en vivo ---
  useEffect(() => {
    if (USE_MOCK) {
      // Modo simulación de UI, sin Raspberry Pi/MQTT/Mongo conectados.
      const interval = setInterval(() => {
        setBuilding((prev) => ({
          ...prev,
          sensors: {
            temperatura: +(20 + Math.random() * 15).toFixed(1),
            humedad: +(25 + Math.random() * 50).toFixed(1),
            gas: Math.round(50 + Math.random() * 200),
            distancia: +(5 + Math.random() * 195).toFixed(1),
            luz: Math.round(Math.random() * 1023),
          },
        }))
        setLastUpdate(new Date())
      }, 3000)
      return () => clearInterval(interval)
    }

    if (!MQTT_URL) {
      setConnection('error')
      return
    }

    const client = mqtt.connect(MQTT_URL, {
      username: MQTT_USERNAME,
      password: MQTT_PASSWORD,
      clientId: `${MQTT_CLIENT_PREFIX}_${Math.random().toString(16).slice(2, 10)}`,
      reconnectPeriod: 3000,
      connectTimeout: 10000,
    })
    clientRef.current = client

    client.on('connect', () => {
      setConnection('connected')
      client.subscribe(SUBSCRIPTION_TOPICS, (err) => {
        if (err) console.error('Error suscribiendo a topics MQTT:', err)
      })
    })

    client.on('reconnect', () => setConnection('connecting'))
    client.on('close', () => setConnection('connecting'))
    client.on('error', (err) => {
      console.error('Error MQTT:', err)
      setConnection('error')
    })

    client.on('message', (topic, payloadBuf) => {
      let payload
      try {
        payload = JSON.parse(payloadBuf.toString())
      } catch {
        return
      }

      setLastUpdate(new Date())

      const sensorKey = SENSOR_BY_TOPIC[topic]
      if (sensorKey) {
        setBuilding((prev) => ({
          ...prev,
          sensors: { ...prev.sensors, [sensorKey]: payload.value },
        }))
        setHistory((prev) => pushHistoryPoint(prev, sensorKey, payload.value))
        return
      }

      switch (topic) {
        case TOPICS.puerta:
          setBuilding((prev) => ({
            ...prev,
            actuators: { ...prev.actuators, puerta: payload.estado },
          }))
          break
        case TOPICS.luces:
          setBuilding((prev) => ({
            ...prev,
            actuators: {
              ...prev.actuators,
              luces: payload.encendidas,
              modo_iluminacion: payload.modo ?? prev.actuators.modo_iluminacion,
            },
          }))
          break
        case TOPICS.ventilador:
          setBuilding((prev) => ({
            ...prev,
            actuators: { ...prev.actuators, ventilador: payload.encendido },
          }))
          break
        case TOPICS.alarma:
          setBuilding((prev) => ({
            ...prev,
            actuators: { ...prev.actuators, alarma: payload.activa },
          }))
          break
        case TOPICS.estado_global:
          setBuilding((prev) => ({ ...prev, status: payload.estado }))
          break
        case TOPICS.arm64_resultados:
          setBuilding((prev) => ({
            ...prev,
            arm64: {
              max: payload.max,
              min: payload.min,
              avg: payload.avg,
              count: payload.count,
            },
          }))
          break
        default:
          break
      }
    })

    return () => {
      client.end(true)
      clientRef.current = null
    }
  }, [])

  const sendCommand = (action, value) => {
    const payload = { action, ...(value !== undefined ? { value } : {}) }

    // Optimista: refleja el comando en el historial local de inmediato,
    // aunque la copia "oficial" (con fecha del servidor) llegará luego vía API/Mongo.
    setCommands((prev) => [
      { id: `local-${Date.now()}`, label: action, source: 'dashboard', timestamp: new Date() },
      ...prev,
    ])

    if (USE_MOCK) return
    clientRef.current?.publish(TOPICS.control_remoto, JSON.stringify(payload))
  }

  return { building, history, events, commands, connection, lastUpdate, sendCommand }
}
