export const TOPICS = Object.freeze({
  temperatura: 'edificio/sensores/temperatura',
  humedad: 'edificio/sensores/humedad',
  gas: 'edificio/sensores/gas',
  distancia: 'edificio/sensores/distancia',
  luz: 'edificio/sensores/luz',
  puerta: 'edificio/actuadores/puerta',
  luces: 'edificio/actuadores/luces',
  ventilador: 'edificio/actuadores/ventilador',
  alarma: 'edificio/actuadores/alarma',
  estado_global: 'edificio/estado/global',
  control_remoto: 'edificio/control/remoto',
  arm64_resultados: 'edificio/arm64/resultados',
})

// export const SUBSCRIPTION_TOPICS = [
//   TOPICS.temperatura,
//   TOPICS.humedad,
//   TOPICS.gas,
//   TOPICS.distancia,
//   TOPICS.luz,
//   TOPICS.puerta,
//   TOPICS.luces,
//   TOPICS.ventilador,
//   TOPICS.alarma,
//   TOPICS.estado_global,
//   TOPICS.arm64_resultados,
// ]
export const SUBSCRIPTION_TOPICS = [
  'edificio/sensores/#',
  'edificio/actuadores/#',
  TOPICS.estado_global,
  TOPICS.arm64_resultados,
]




export const SENSOR_BY_TOPIC = Object.freeze({
  [TOPICS.temperatura]: 'temperatura',
  [TOPICS.humedad]: 'humedad',
  [TOPICS.gas]: 'gas',
  [TOPICS.distancia]: 'distancia',
  [TOPICS.luz]: 'luz',
})
