function formatTime(timestamp) {
  return new Intl.DateTimeFormat('es-GT', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(new Date(timestamp))
}

function ActivityTable({ title, rows, type }) {
  return (
    <article className="activity-card">
      <div className="activity-card-header">
        <h3>{title}</h3>
        <span className="activity-count">{rows.length} registros</span>
      </div>
      <table className="activity-table">
        <thead>
          <tr>
            <th>{type === 'events' ? 'Evento' : 'Comando'}</th>
            <th>Hora</th>
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr><td className="empty-row" colSpan="2">No hay registros recientes</td></tr>
          ) : rows.slice(0, 5).map((row) => (
            <tr key={row.id}>
              <td>
                <span className="activity-primary">
                  {type === 'events' ? row.description : row.label}
                </span>
                <span className="activity-secondary">
                  {type === 'events' ? row.type : row.source}
                </span>
              </td>
              <td>{formatTime(row.timestamp)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </article>
  )
}

function ActivityTables({ events, commands }) {
  return (
    <div className="activity-grid">
      <ActivityTable title="Últimos eventos" rows={events} type="events" />
      <ActivityTable title="Comandos remotos" rows={commands} type="commands" />
    </div>
  )
}

export default ActivityTables
