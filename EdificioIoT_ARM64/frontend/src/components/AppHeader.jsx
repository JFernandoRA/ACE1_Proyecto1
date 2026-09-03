import { Wifi } from 'lucide-react'

const connectionLabels = {
  connected: 'EMQX conectado',
  connecting: 'Conectando a EMQX',
  simulated: 'Modo simulación',
  error: 'Sin conexión MQTT',
}

function AppHeader({ connection, lastUpdate }) {
  const updated = new Intl.DateTimeFormat('es-GT', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(lastUpdate)

  return (
    <header className="app-header">
      <div>
        <h1>Panel de supervisión</h1>
        <p>Lecturas, alertas y control remoto del edificio inteligente</p>
      </div>
      <div className="header-meta">
        <time dateTime={lastUpdate.toISOString()}>Actualizado {updated}</time>
        <div className={`connection-pill ${connection}`}>
          <span className="connection-dot" />
          <Wifi size={14} aria-hidden="true" />
          {connectionLabels[connection] ?? 'Estado desconocido'}
        </div>
      </div>
    </header>
  )
}

export default AppHeader
