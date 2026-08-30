const timeLabel = (date) => new Intl.DateTimeFormat('es-GT', {
  hour: '2-digit',
  minute: '2-digit',
  second: '2-digit',
}).format(date)

const baseSeries = {
  temperatura: [23.5, 23.7, 24.1, 24.3, 24.2, 24.7, 25.0, 24.8, 25.1, 25.3, 25.0, 24.9],
  humedad: [54, 53, 53, 52, 51, 52, 50, 49, 50, 51, 50, 49],
  gas: [106, 112, 109, 118, 121, 116, 124, 119, 127, 120, 115, 122],
  distancia: [82, 78, 76, 90, 88, 92, 70, 74, 81, 79, 76, 72],
  luz: [428, 415, 402, 390, 376, 365, 350, 341, 330, 322, 315, 308],
}

export function createInitialHistory() {
  const now = Date.now()
  const labels = Array.from({ length: 12 }, (_, index) => (
    timeLabel(new Date(now - (11 - index) * 3000))
  ))

  return Object.fromEntries(
    Object.entries(baseSeries).map(([sensor, values]) => [
      sensor,
      values.map((value, index) => ({ label: labels[index], value })),
    ]),
  )
}

export function createInitialBuilding() {
  return {
    status: 'NORMAL',
    sensors: {
      temperatura: 24.9,
      humedad: 49,
      gas: 122,
      distancia: 72,
      luz: 308,
    },
    actuators: {
      puerta: 'CERRADA',
      luces: false,
      modo_iluminacion: 'AUTOMATICO',
      ventilador: false,
      alarma: false,
    },
    arm64: {
      max: 29,
      min: 21,
      avg: 25,
      count: 20,
    },
  }
}

const now = Date.now()

export const initialEvents = [
  {
    id: 'event-1',
    type: 'cambio_estado',
    description: 'Estado global actualizado a NORMAL',
    timestamp: new Date(now - 55_000).toISOString(),
  },
  {
    id: 'event-2',
    type: 'iluminacion',
    description: 'Iluminación automática desactivada por nivel suficiente',
    timestamp: new Date(now - 122_000).toISOString(),
  },
  {
    id: 'event-3',
    type: 'acceso',
    description: 'Puerta cerrada después del tiempo configurado',
    timestamp: new Date(now - 196_000).toISOString(),
  },
]

export const initialCommands = [
  {
    id: 'command-1',
    source: 'dashboard',
    action: 'set_modo_iluminacion',
    label: 'Modo de iluminación: AUTOMÁTICO',
    timestamp: new Date(now - 245_000).toISOString(),
  },
  {
    id: 'command-2',
    source: 'dashboard',
    action: 'cerrar_puerta',
    label: 'Cerrar puerta principal',
    timestamp: new Date(now - 310_000).toISOString(),
  },
]

export { timeLabel }
