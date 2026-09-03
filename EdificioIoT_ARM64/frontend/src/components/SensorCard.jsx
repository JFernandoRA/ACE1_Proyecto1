function SensorCard({ label, unit, icon: Icon, tone, helper, value, active, onSelect }) {
  const displayValue = value == null ? '--' : value

  return (
    <button
      className={`sensor-card ${tone} ${active ? 'active' : ''}`}
      type="button"
      onClick={onSelect}
      aria-pressed={active}
      aria-label={`Ver historial de ${label}`}
    >
      <div className="sensor-top">
        <div className="sensor-icon"><Icon size={17} aria-hidden="true" /></div>
        <span className="sensor-label">{label}</span>
      </div>
      <div className="sensor-reading">
        <strong>{displayValue}</strong>
        <span>{unit}</span>
      </div>
      <span className="sensor-helper">{helper}</span>
    </button>
  )
}

export default SensorCard
