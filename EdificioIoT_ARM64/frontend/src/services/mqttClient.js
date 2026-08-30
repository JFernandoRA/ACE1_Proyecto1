import { SUBSCRIPTION_TOPICS, TOPICS } from '../config/topics.js'

export async function createBuildingMqtt({ onMessage, onStatus }) {
  const url = import.meta.env.VITE_MQTT_URL
  if (!url) {
    onStatus('error')
    return null
  }

  const prefix = import.meta.env.VITE_MQTT_CLIENT_PREFIX || 'edificio_dashboard'
  const clientId = `${prefix}_${crypto.randomUUID().slice(0, 8)}`
  onStatus('connecting')

  const mqttModule = await import('mqtt')
  const connect = mqttModule.connect ?? mqttModule.default?.connect
  const client = connect(url, {
    clientId,
    username: import.meta.env.VITE_MQTT_USERNAME || undefined,
    password: import.meta.env.VITE_MQTT_PASSWORD || undefined,
    clean: true,
    reconnectPeriod: 3000,
    connectTimeout: 10000,
    protocolVersion: 4,
  })

  client.on('connect', () => {
    onStatus('connected')
    client.subscribe(SUBSCRIPTION_TOPICS, { qos: 0 }, (error) => {
      if (error) onStatus('error')
    })
  })

  client.on('message', (topic, rawPayload) => {
    try {
      const payload = JSON.parse(rawPayload.toString())
      onMessage(topic, payload)
    } catch (error) {
      console.warn(`Mensaje MQTT inválido en ${topic}`, error)
    }
  })

  client.on('reconnect', () => onStatus('connecting'))
  client.on('offline', () => onStatus('connecting'))
  client.on('error', (error) => {
    console.error('Error de conexión MQTT', error)
    onStatus('error')
  })

  return {
    publishCommand(command) {
      if (!client.connected) return false
      client.publish(TOPICS.control_remoto, JSON.stringify(command), { qos: 1 })
      return true
    },
    disconnect() {
      client.end(true)
    },
  }
}
