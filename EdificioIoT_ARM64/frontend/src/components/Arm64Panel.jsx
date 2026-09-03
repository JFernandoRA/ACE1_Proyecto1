import { Binary } from 'lucide-react'

const statistics = [
  { key: 'max', label: 'Máximo', suffix: ' °C' },
  { key: 'min', label: 'Mínimo', suffix: ' °C' },
  { key: 'avg', label: 'Promedio', suffix: ' °C' },
  { key: 'count', label: 'Lecturas', suffix: '' },
]

function Arm64Panel({ result }) {
  return (
    <article className="panel arm64-panel">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">Procesamiento</span>
          <h3>Último resultado ARM64</h3>
        </div>
        <div className="panel-icon"><Binary size={21} /></div>
      </div>

      <div className="arm64-stats">
        {statistics.map(({ key, label, suffix }) => (
          <div className="arm64-stat" key={key}>
            <span>{label}</span>
            <strong>{result[key] ?? '--'}{result[key] == null ? '' : suffix}</strong>
          </div>
        ))}
      </div>
    </article>
  )
}

export default Arm64Panel
