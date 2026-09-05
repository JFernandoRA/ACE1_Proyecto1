



import { SUBSCRIPTION_TOPICS, TOPICS } from '../config/topics.js'


export async function createBuildingMqtt({ onMessage, onStatus }) {
  const url = import.meta.env.VITE_MQTT_URL
  if (!url) {
    console.error('[MQTT] VITE_MQTT_URL no está definido en .env')
    onStatus('error')
    return null
  }


  const prefix = import.meta.env.VITE_MQTT_CLIENT_PREFIX || 'edif'
  const clientId = `${prefix}_${crypto.randomUUID().slice(0, 8)}`
  console.log('[MQTT] Intentando conectar', { url, clientId, longitud: clientId.length })


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


  // ---- AQUÍ VA EL CAMBIO TEMPORAL ----
  // client.on('connect', (connack) => {
  //   console.log('[MQTT] Conectado. CONNACK:', connack)
  //   onStatus('connected')


  //   // TEMPORAL: suscribe uno por uno para ver cuál falla
  //   SUBSCRIPTION_TOPICS.forEach((topic) => {
  //     client.subscribe(topic, { qos: 0 }, (error, granted) => {
  //       if (error) {
  //         console.error(`[MQTT] Falló suscripción a "${topic}":`, error.message)
  //       } else {
  //         console.log(`[MQTT] OK: "${topic}"`, granted)
  //       }
  //     })
  //   })
  // })



////------ prueba de depuración----------
//   client.on('connect', (connack) => {
//   console.log('[MQTT] Conectado. CONNACK:', connack)
//   onStatus('connected')


//   // PRUEBA: solo este tópico, solo
//   client.subscribe('edificio/arm64/resultados', { qos: 0 }, (error, granted) => {
//     if (error) {
//       console.error('[MQTT] Falló suscripción aislada:', error.message)
//     } else {
//       console.log('[MQTT] OK suscripción aislada:', granted)
//     }
//   })
// })

// client.on('connect', (connack) => {
//   console.log('[MQTT] Conectado. CONNACK:', connack)
//   onStatus('connected')


//   // Una sola llamada con el array completo de tópicos,
//   // en vez de 11 llamadas separadas (evita saturar al broker con ráfagas)
//   client.subscribe(SUBSCRIPTION_TOPICS, { qos: 0 }, (error, granted) => {
//     if (error) {
//       console.error('[MQTT] Error al suscribirse:', error.message, error)
//       onStatus('error')
//     } else {
//       console.log('[MQTT] Suscrito correctamente a todos los tópicos:', granted)
//     }
//   })
// })

client.on('connect', (connack) => {
  console.log('[MQTT] Conectado. CONNACK:', connack)
  onStatus('connected')


  client.subscribe(SUBSCRIPTION_TOPICS, { qos: 0 }, (error, granted) => {
    if (error) {
      console.error('[MQTT] Error al suscribirse:', error.message, error)
      onStatus('error')
    } else {
      console.log('[MQTT] Suscrito correctamente:', granted)
    }
  })
})





  // ---- FIN DEL CAMBIO TEMPORAL ----


  client.on('message', (topic, rawPayload) => {
    try {
      const payload = JSON.parse(rawPayload.toString())
      onMessage(topic, payload)
    } catch (error) {
      console.warn(`[MQTT] Mensaje inválido en ${topic}`, error)
    }
  })


  client.on('reconnect', () => {
    console.warn('[MQTT] Reintentando conexión...')
    onStatus('connecting')
  })


  client.on('offline', () => {
    console.warn('[MQTT] Cliente offline')
    onStatus('connecting')
  })


  client.on('close', () => {
    console.warn('[MQTT] Conexión cerrada')
  })


  client.on('error', (error) => {
    console.error('[MQTT] Error de conexión:', error?.message ?? error, error)
    onStatus('error')
  })


  return {
    publishCommand(command) {
      if (!client.connected) {
        console.warn('[MQTT] No conectado, comando descartado:', command)
        return false
      }
      client.publish(TOPICS.control_remoto, JSON.stringify(command), { qos: 1 })
      return true
    },
    disconnect() {
      client.end(true)
    },
  }
}


