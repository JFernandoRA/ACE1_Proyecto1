import { useCallback, useEffect, useRef, useState } from 'react'
import { SENSOR_BY_TOPIC, TOPICS } from '../config/topics.js'
import {
  createInitialBuilding,
  createInitialHistory,
  initialCommands,
  initialEvents,
  timeLabel,
} from '../data/mockData.js'
import { createBuildingMqtt } from '../services/mqttClient.js'

const useMockData = (import.meta.env.VITE_USE_MOCK_DATA ?? 'true').toLowerCase() === 'true'

const commandLabels = {
  abrir_puerta: 'Abrir puerta principal',
  cerrar_puerta: 'Cerrar puerta principal',
  toggle_luces: 'Cambiar estado de iluminación',
  set_modo_iluminacion: 'Cambiar modo de iluminación',
  toggle_ventilador: 'Cambiar estado de ventilación',
  silenciar_alarma: 'Silenciar alarma',
  resetear_alerta: 'Restablecer estado de alerta',
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value))
}

function walk(value, variation, min, max, decimals = 0) {
  const next = clamp(value + (Math.random() - 0.5) * variation, min, max)
  return Number(next.toFixed(decimals))
}

function appendHistory(history, sensor, value) {
  const nextPoint = { label: timeLabel(new Date()), value }
  return {
    ...history,
    [sensor]: [...(history[sensor] ?? []), nextPoint].slice(-20),
  }
}

function calculateStatus(sensors) {
  if (sensors.gas > 400) return 'EMERGENCIA'
  if (sensors.temperatura > 30 || sensors.humedad < 30 || sensors.humedad > 70) {
    return 'ADVERTENCIA'
  }
  return 'NORMAL'
}

function applyMockCommand(building, action, value) {
  const actuators = { ...building.actuators }
  let status = building.status

  if (action === 'abrir_puerta') actuators.puerta = 'ABIERTA'
  if (action === 'cerrar_puerta') actuators.puerta = 'CERRADA'
  if (action === 'toggle_luces') actuators.luces = Boolean(value)
  if (action === 'set_modo_iluminacion') actuators.modo_iluminacion = value
  if (action === 'toggle_ventilador') actuators.ventilador = Boolean(value)
  if (action === 'silenciar_alarma') actuators.alarma = false
  if (action === 'resetear_alerta' && building.sensors.gas <= 400) status = 'NORMAL'

  return { ...building, status, actuators }
}

export function useBuildingData() {
  const [building, setBuilding] = useState(createInitialBuilding)
  const [history, setHistory] = useState(createInitialHistory)
  const [events, setEvents] = useState(initialEvents)
  const [commands, setCommands] = useState(initialCommands)
  const [connection, setConnection] = useState(useMockData ? 'simulated' : 'connecting')
  const [lastUpdate, setLastUpdate] = useState(new Date())
  const mqttController = useRef(null)

  const handleMqttMessage = useCallback((topic, payload) => {
    const sensor = SENSOR_BY_TOPIC[topic]
    const receivedAt = new Date()

    if (sensor && typeof payload.value === 'number') {
      setBuilding((current) => ({
        ...current,
        sensors: { ...current.sensors, [sensor]: payload.value },
      }))
      setHistory((current) => appendHistory(current, sensor, payload.value))
    } else if (topic === TOPICS.estado_global) {
      setBuilding((current) => ({ ...current, status: payload.estado ?? current.status }))
    } else if (topic === TOPICS.puerta) {
      setBuilding((current) => ({
        ...current,
        actuators: { ...current.actuators, puerta: payload.estado ?? current.actuators.puerta },
      }))
    } else if (topic === TOPICS.luces) {
      setBuilding((current) => ({
        ...current,
        actuators: {
          ...current.actuators,
          luces: payload.encendidas ?? current.actuators.luces,
          modo_iluminacion: payload.modo ?? current.actuators.modo_iluminacion,
        },
      }))
    } else if (topic === TOPICS.ventilador) {
      setBuilding((current) => ({
        ...current,
        actuators: {
          ...current.actuators,
          ventilador: payload.encendido ?? current.actuators.ventilador,
        },
      }))
    } else if (topic === TOPICS.alarma) {
      setBuilding((current) => ({
        ...current,
        actuators: { ...current.actuators, alarma: payload.activa ?? current.actuators.alarma },
      }))
    } else if (topic === TOPICS.arm64_resultados) {
      setBuilding((current) => ({ ...current, arm64: { ...current.arm64, ...payload } }))
    }

    setLastUpdate(receivedAt)
  }, [])

  useEffect(() => {
  if (!useMockData) {
    let cancelled = false
    let controller = null


    // Retrasamos la creación real del cliente MQTT un tick. En desarrollo,
    // React StrictMode monta este efecto, lo desmonta y lo vuelve a montar
    // de inmediato para detectar efectos mal limpiados. Ese "montaje
    // fantasma" cancela su propio timer antes de que llegue a disparar,
    // así que solo el montaje real crea la conexión WebSocket -- evitando
    // el doble cliente MQTT que veíamos en consola.
    const timer = window.setTimeout(() => {
      createBuildingMqtt({
        onMessage: handleMqttMessage,
        onStatus: setConnection,
      }).then((created) => {
        if (cancelled) {
          created?.disconnect()
          return
        }
        controller = created
        mqttController.current = created
      }).catch((error) => {
        console.error('No se pudo iniciar el cliente MQTT', error)
        if (!cancelled) setConnection('error')
      })
    }, 0)


    return () => {
      cancelled = true
      window.clearTimeout(timer)
      controller?.disconnect()
      mqttController.current = null
    }
  }


  const interval = window.setInterval(() => {
    setBuilding((current) => {
      const sensors = {
        temperatura: walk(current.sensors.temperatura, 1.1, 20, 34, 1),
        humedad: walk(current.sensors.humedad, 3, 28, 74, 1),
        gas: Math.random() < 0.025 ? Math.round(420 + Math.random() * 90) : walk(current.sensors.gas, 28, 70, 260),
        distancia: walk(current.sensors.distancia, 20, 18, 180, 1),
        luz: walk(current.sensors.luz, 65, 60, 900),
      }
      const status = calculateStatus(sensors)
      const actuators = { ...current.actuators }


      if (actuators.modo_iluminacion === 'AUTOMATICO') actuators.luces = sensors.luz < 200
      actuators.ventilador = sensors.temperatura > 30
      actuators.alarma = status === 'EMERGENCIA'
      if (status === 'EMERGENCIA') actuators.puerta = 'ABIERTA'


      Object.entries(sensors).forEach(([sensor, value]) => {
        setHistory((currentHistory) => appendHistory(currentHistory, sensor, value))
      })


      if (status !== current.status) {
        setEvents((currentEvents) => [{
          id: crypto.randomUUID(),
          type: 'cambio_estado',
          description: `Estado global actualizado a ${status}`,
          timestamp: new Date().toISOString(),
        }, ...currentEvents].slice(0, 20))
      }


      return { ...current, sensors, status, actuators }
    })
    setLastUpdate(new Date())
  }, 3000)


  return () => window.clearInterval(interval)
}, [handleMqttMessage])




  const sendCommand = useCallback((action, value) => {
    const payload = { action }
    if (value !== undefined) payload.value = value

    if (useMockData) {
      setBuilding((current) => applyMockCommand(current, action, value))
    } else {
      mqttController.current?.publishCommand(payload)
    }

    setCommands((current) => [{
      id: crypto.randomUUID(),
      source: 'dashboard',
      action,
      label: value === undefined
        ? commandLabels[action] ?? action
        : `${commandLabels[action] ?? action}: ${String(value)}`,
      timestamp: new Date().toISOString(),
    }, ...current].slice(0, 20))
    setLastUpdate(new Date())
  }, [])

  return {
    building,
    history,
    events,
    commands,
    connection,
    lastUpdate,
    sendCommand,
  }
}
