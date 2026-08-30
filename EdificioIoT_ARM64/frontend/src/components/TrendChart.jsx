import { useMemo } from 'react'
import {
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler)

const colors = {
  orange: { line: '#ff8a5c', fill: 'rgba(255, 138, 92, 0.12)' },
  blue: { line: '#5eb8ff', fill: 'rgba(94, 184, 255, 0.12)' },
  red: { line: '#ff5f6d', fill: 'rgba(255, 95, 109, 0.12)' },
  violet: { line: '#a78bfa', fill: 'rgba(167, 139, 250, 0.12)' },
  yellow: { line: '#f7c75d', fill: 'rgba(247, 199, 93, 0.12)' },
}

function TrendChart({ history, sensor, definition, sensors, onSensorChange }) {
  const palette = colors[definition?.tone] ?? colors.blue
  const points = useMemo(() => history[sensor] ?? [], [history, sensor])
  const chartData = useMemo(() => ({
    labels: points.map((point) => point.label),
    datasets: [
      {
        label: `${definition?.label ?? sensor} (${definition?.unit ?? ''})`,
        data: points.map((point) => point.value),
        borderColor: palette.line,
        backgroundColor: palette.fill,
        borderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 4,
        pointHoverBackgroundColor: palette.line,
        tension: 0.38,
        fill: true,
      },
    ],
  }), [definition, palette, points, sensor])

  const options = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#07101c',
        borderColor: 'rgba(151, 178, 211, 0.2)',
        borderWidth: 1,
        titleColor: '#eef5ff',
        bodyColor: '#a9bdd3',
        padding: 11,
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: '#657d98', maxRotation: 0, autoSkip: true, maxTicksLimit: 8 },
        border: { color: 'rgba(151, 178, 211, 0.1)' },
      },
      y: {
        beginAtZero: sensor === 'gas' || sensor === 'luz',
        grid: { color: 'rgba(151, 178, 211, 0.07)' },
        ticks: { color: '#657d98' },
        border: { display: false },
      },
    },
  }), [sensor])

  return (
    <article className="panel chart-panel">
      <div className="chart-toolbar">
        <div>
          <h3>Historial de {definition?.label?.toLowerCase()}</h3>
          <p>Últimas {points.length} lecturas recibidas</p>
        </div>
        <div className="chart-tabs" role="tablist" aria-label="Seleccionar sensor">
          {sensors.map((item) => (
            <button
              className={`chart-tab ${sensor === item.key ? 'active' : ''}`}
              type="button"
              role="tab"
              aria-selected={sensor === item.key}
              onClick={() => onSensorChange(item.key)}
              key={item.key}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>
      <div className="chart-wrap">
        <Line data={chartData} options={options} />
      </div>
    </article>
  )
}

export default TrendChart
