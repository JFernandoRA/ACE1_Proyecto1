import { Activity, Building2, Cpu, History, RadioTower, SlidersHorizontal } from 'lucide-react'

const navItems = [
  { href: '#resumen', label: 'Resumen', icon: Activity },
  { href: '#monitoreo', label: 'Monitoreo', icon: RadioTower },
  { href: '#controles', label: 'Controles', icon: SlidersHorizontal },
  { href: '#historial', label: 'Historial', icon: History },
]

const statusClasses = {
  NORMAL: 'normal',
  ADVERTENCIA: 'warning',
  EMERGENCIA: 'emergency',
}

function Sidebar({ status, connection }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark" aria-hidden="true"><Building2 size={22} /></div>
        <div>
          <strong>Edificio IoT</strong>
          <span>Centro de control</span>
        </div>
      </div>

      <nav className="sidebar-nav" aria-label="Navegación principal">
        {navItems.map(({ href, label, icon: Icon }, index) => (
          <a className={`nav-link ${index === 0 ? 'active' : ''}`} href={href} key={href}>
            <Icon size={17} aria-hidden="true" />
            <span>{label}</span>
          </a>
        ))}
      </nav>

      <div className="sidebar-status">
        <span className="sidebar-status-label">Sistema Raspberry Pi</span>
        <div className="sidebar-status-row">
          <span className={`status-chip ${statusClasses[status] ?? ''}`}>{status}</span>
          <Cpu size={18} color={connection === 'error' ? '#ff5f6d' : '#28d8d0'} />
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
