import { CheckCircle2, ShieldAlert, Siren } from 'lucide-react'

const statusInfo = {
  NORMAL: {
    className: 'normal',
    description: 'Todos los sensores se encuentran dentro de los rangos seguros definidos.',
    icon: CheckCircle2,
  },
  ADVERTENCIA: {
    className: 'warning',
    description: 'Existe una condición fuera del rango recomendado que requiere atención.',
    icon: ShieldAlert,
  },
  EMERGENCIA: {
    className: 'emergency',
    description: 'Se detectó gas o humo por encima del umbral. Protocolo de evacuación activo.',
    icon: Siren,
  },
}

function StatusPanel({ status, arm64, connection }) {
  const info = statusInfo[status] ?? statusInfo.NORMAL
  const Icon = info.icon

  return (
    <article className={`panel status-panel ${info.className}`}>
      <div className="status-content">
        <span className="eyebrow">Estado global del edificio</span>
        <h2 className="status-title">{status}</h2>
        <p className="status-description">{info.description}</p>
        <p className="status-description">
          Fuente: {connection === 'simulated' ? 'sensores simulados' : 'Raspberry Pi por MQTT'} ·
          Último promedio ARM64: {arm64.avg} °C
        </p>
      </div>
      <div className="status-orbit" aria-hidden="true">
        <Icon size={42} strokeWidth={1.5} />
      </div>
    </article>
  )
}

export default StatusPanel
