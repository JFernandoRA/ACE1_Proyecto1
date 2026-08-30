import { BellOff, DoorOpen, Fan, Lightbulb, RotateCcw } from 'lucide-react'

function ControlCard({ icon: Icon, title, status, statusClass, description, children }) {
  return (
    <article className="control-card">
      <div className="control-title-row">
        <div className="control-title"><Icon size={17} /> {title}</div>
        <span className={`status-chip ${statusClass}`}>{status}</span>
      </div>
      <p className="control-description">{description}</p>
      {children}
    </article>
  )
}

function ControlPanel({ actuators, onCommand }) {
  const doorOpen = actuators.puerta === 'ABIERTA'
  const lightsOn = actuators.luces
  const fanOn = actuators.ventilador

  return (
    <div className="controls-grid">
      <ControlCard
        icon={DoorOpen}
        title="Puerta principal"
        status={actuators.puerta}
        statusClass={doorOpen ? 'open' : ''}
        description="Control manual del servomotor de acceso."
      >
        <div className="button-row">
          <button
            className={`action-button ${doorOpen ? 'active' : ''}`}
            type="button"
            onClick={() => onCommand('abrir_puerta')}
          >Abrir</button>
          <button
            className={`action-button ${!doorOpen ? 'active' : ''}`}
            type="button"
            onClick={() => onCommand('cerrar_puerta')}
          >Cerrar</button>
        </div>
      </ControlCard>

      <ControlCard
        icon={Lightbulb}
        title="Iluminación"
        status={lightsOn ? 'ENCENDIDAS' : 'APAGADAS'}
        statusClass={lightsOn ? 'on' : ''}
        description={`Modo actual: ${actuators.modo_iluminacion}`}
      >
        <div className="button-row">
          <button
            className={`action-button ${lightsOn ? 'active' : ''}`}
            type="button"
            onClick={() => onCommand('toggle_luces', true)}
          >Encender</button>
          <button
            className={`action-button ${!lightsOn ? 'active' : ''}`}
            type="button"
            onClick={() => onCommand('toggle_luces', false)}
          >Apagar</button>
        </div>
        <div className="mode-row" style={{ marginTop: 7 }}>
          {['AUTOMATICO', 'MANUAL'].map((mode) => (
            <button
              className={`action-button ${actuators.modo_iluminacion === mode ? 'active' : ''}`}
              type="button"
              onClick={() => onCommand('set_modo_iluminacion', mode)}
              key={mode}
            >{mode === 'AUTOMATICO' ? 'Automático' : 'Manual'}</button>
          ))}
        </div>
      </ControlCard>

      <ControlCard
        icon={Fan}
        title="Ventilación"
        status={fanOn ? 'ACTIVA' : 'INACTIVA'}
        statusClass={fanOn ? 'on' : ''}
        description="Respuesta automática o control remoto del ventilador."
      >
        <div className="button-row">
          <button
            className={`action-button ${fanOn ? 'active' : ''}`}
            type="button"
            onClick={() => onCommand('toggle_ventilador', true)}
          >Activar</button>
          <button
            className={`action-button ${!fanOn ? 'active' : ''}`}
            type="button"
            onClick={() => onCommand('toggle_ventilador', false)}
          >Desactivar</button>
        </div>
      </ControlCard>

      <ControlCard
        icon={BellOff}
        title="Alarma"
        status={actuators.alarma ? 'ACTIVA' : 'SILENCIADA'}
        statusClass={actuators.alarma ? 'alarm' : ''}
        description="Silencia el buzzer o solicita restablecer la alerta."
      >
        <div className="button-row">
          <button
            className="action-button danger"
            type="button"
            onClick={() => onCommand('silenciar_alarma')}
          ><BellOff size={13} />&nbsp; Silenciar</button>
          <button
            className="action-button"
            type="button"
            onClick={() => onCommand('resetear_alerta')}
          ><RotateCcw size={13} />&nbsp; Restablecer</button>
        </div>
      </ControlCard>
    </div>
  )
}

export default ControlPanel
