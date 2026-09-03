import { useMemo, useState } from 'react'
import {
  Activity,
  CloudSun,
  Droplets,
  Gauge,
  Radio,
  Ruler,
  Sun,
  Thermometer,
} from 'lucide-react'
import ActivityTables from './components/ActivityTables.jsx'
import AppHeader from './components/AppHeader.jsx'
import Arm64Panel from './components/Arm64Panel.jsx'
import ControlPanel from './components/ControlPanel.jsx'
import SensorCard from './components/SensorCard.jsx'
import Sidebar from './components/Sidebar.jsx'
import StatusPanel from './components/StatusPanel.jsx'
import TrendChart from './components/TrendChart.jsx'
import { useBuildingData } from './hooks/useBuildingData.js'
import './App.css'

const sensorDefinitions = [
  {
    key: 'temperatura',
    label: 'Temperatura',
    unit: '°C',
    icon: Thermometer,
    tone: 'orange',
    helper: 'Umbral alto: 30 °C',
  },
  {
    key: 'humedad',
    label: 'Humedad',
    unit: '%',
    icon: Droplets,
    tone: 'blue',
    helper: 'Rango seguro: 30–70 %',
  },
  {
    key: 'gas',
    label: 'Gas / humo',
    unit: 'ADC',
    icon: Gauge,
    tone: 'red',
    helper: 'Emergencia: mayor a 400',
  },
  {
    key: 'distancia',
    label: 'Distancia',
    unit: 'cm',
    icon: Ruler,
    tone: 'violet',
    helper: 'Apertura: menor a 30 cm',
  },
  {
    key: 'luz',
    label: 'Nivel de luz',
    unit: 'ADC',
    icon: Sun,
    tone: 'yellow',
    helper: 'Luz baja: menor a 200',
  },
]

function App() {
  const {
    building,
    history,
    events,
    commands,
    connection,
    lastUpdate,
    sendCommand,
  } = useBuildingData()
  const [selectedSensor, setSelectedSensor] = useState('temperatura')

  const selectedDefinition = useMemo(
    () => sensorDefinitions.find((sensor) => sensor.key === selectedSensor),
    [selectedSensor],
  )

  return (
    <div className="app-shell">
      <Sidebar status={building.status} connection={connection} />

      <main className="workspace">
        <AppHeader connection={connection} lastUpdate={lastUpdate} />

        <section className="overview-grid" id="resumen" aria-label="Resumen del edificio">
          <StatusPanel
            status={building.status}
            arm64={building.arm64}
            connection={connection}
          />
          <Arm64Panel result={building.arm64} />
        </section>

        <section className="section-block" id="monitoreo">
          <div className="section-heading">
            <div>
              <span className="eyebrow"><Activity size={14} /> Sensores</span>
              <h2>Monitoreo en tiempo real</h2>
            </div>
            <div className="live-indicator" aria-label="Lecturas actualizándose">
              <span /> Lecturas activas
            </div>
          </div>

          <div className="sensor-grid">
            {sensorDefinitions.map((sensor) => (
              <SensorCard
                key={sensor.key}
                {...sensor}
                value={building.sensors[sensor.key]}
                active={selectedSensor === sensor.key}
                onSelect={() => setSelectedSensor(sensor.key)}
              />
            ))}
          </div>

          <TrendChart
            history={history}
            sensor={selectedSensor}
            definition={selectedDefinition}
            sensors={sensorDefinitions}
            onSensorChange={setSelectedSensor}
          />
        </section>

        <section className="section-block" id="controles">
          <div className="section-heading">
            <div>
              <span className="eyebrow"><Radio size={14} /> MQTT</span>
              <h2>Control remoto de actuadores</h2>
            </div>
            <p className="section-copy">
              Los comandos se publican en <code>edificio/control/remoto</code>.
            </p>
          </div>
          <ControlPanel actuators={building.actuators} onCommand={sendCommand} />
        </section>

        <section className="section-block" id="historial">
          <div className="section-heading">
            <div>
              <span className="eyebrow"><CloudSun size={14} /> Registro</span>
              <h2>Historial reciente</h2>
            </div>
          </div>
          <ActivityTables events={events} commands={commands} />
        </section>

        <footer className="app-footer">
          Edificio Inteligente IoT · Raspberry Pi ARM64 · USAC 2026
        </footer>
      </main>
    </div>
  )
}

export default App
