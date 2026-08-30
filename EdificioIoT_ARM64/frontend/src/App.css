.app-shell {
  display: grid;
  grid-template-columns: 248px minmax(0, 1fr);
  min-height: 100vh;
}

.sidebar {
  position: sticky;
  top: 0;
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 28px 20px 22px;
  border-right: 1px solid var(--border);
  background: rgba(7, 16, 28, 0.88);
  backdrop-filter: blur(20px);
  z-index: 10;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 36px;
}

.brand-mark {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border: 1px solid rgba(40, 216, 208, 0.3);
  border-radius: 13px;
  color: var(--cyan);
  background: linear-gradient(145deg, rgba(40, 216, 208, 0.18), rgba(76, 156, 255, 0.08));
  box-shadow: inset 0 0 20px rgba(40, 216, 208, 0.05);
}

.brand strong,
.brand span {
  display: block;
}

.brand strong {
  color: var(--text);
  font-size: 0.96rem;
  letter-spacing: -0.02em;
}

.brand span {
  margin-top: 2px;
  color: var(--muted);
  font-size: 0.72rem;
}

.sidebar-nav {
  display: grid;
  gap: 7px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 11px;
  min-height: 44px;
  padding: 0 13px;
  border: 1px solid transparent;
  border-radius: 10px;
  color: #91a5bd;
  font-size: 0.86rem;
  font-weight: 600;
  text-decoration: none;
  transition: 160ms ease;
}

.nav-link:hover,
.nav-link.active {
  border-color: rgba(76, 156, 255, 0.18);
  color: var(--text);
  background: rgba(76, 156, 255, 0.09);
}

.nav-link.active svg {
  color: var(--blue);
}

.sidebar-status {
  margin-top: auto;
  padding: 14px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: rgba(17, 34, 57, 0.5);
}

.sidebar-status-label {
  display: block;
  margin-bottom: 9px;
  color: var(--muted);
  font-size: 0.7rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.sidebar-status-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.workspace {
  width: min(1500px, 100%);
  min-width: 0;
  margin: 0 auto;
  padding: 0 34px 36px;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 92px;
  gap: 24px;
}

.app-header h1 {
  margin: 0;
  color: var(--text);
  font-size: clamp(1.35rem, 2.2vw, 1.9rem);
  letter-spacing: -0.045em;
}

.app-header p {
  margin: 6px 0 0;
  color: var(--muted);
  font-size: 0.82rem;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 14px;
}

.connection-pill,
.status-chip,
.live-indicator {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  white-space: nowrap;
}

.connection-pill {
  min-height: 36px;
  padding: 0 12px;
  border: 1px solid var(--border);
  border-radius: 999px;
  color: #bdd0e5;
  background: rgba(12, 24, 39, 0.8);
  font-size: 0.75rem;
  font-weight: 700;
}

.connection-dot,
.live-indicator span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--green);
  box-shadow: 0 0 0 4px rgba(54, 213, 141, 0.1), 0 0 12px rgba(54, 213, 141, 0.5);
}

.connection-pill.connecting .connection-dot {
  background: var(--yellow);
  box-shadow: 0 0 0 4px rgba(247, 199, 93, 0.1);
}

.connection-pill.error .connection-dot {
  background: var(--red);
  box-shadow: 0 0 0 4px rgba(255, 95, 109, 0.1);
}

.overview-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) minmax(320px, 0.65fr);
  gap: 18px;
}

.panel,
.sensor-card,
.control-card,
.activity-card {
  border: 1px solid var(--border);
  background: linear-gradient(150deg, rgba(17, 34, 57, 0.86), rgba(9, 20, 33, 0.92));
  box-shadow: var(--shadow);
}

.status-panel {
  position: relative;
  display: grid;
  grid-template-columns: 1fr auto;
  min-height: 230px;
  padding: 28px;
  overflow: hidden;
  border-radius: 18px;
}

.status-panel::after {
  position: absolute;
  right: -70px;
  bottom: -110px;
  width: 280px;
  height: 280px;
  border: 1px solid rgba(54, 213, 141, 0.14);
  border-radius: 50%;
  box-shadow:
    0 0 0 34px rgba(54, 213, 141, 0.035),
    0 0 0 70px rgba(54, 213, 141, 0.025);
  content: '';
}

.status-panel.warning::after {
  border-color: rgba(247, 199, 93, 0.2);
  box-shadow: 0 0 0 34px rgba(247, 199, 93, 0.04), 0 0 0 70px rgba(247, 199, 93, 0.025);
}

.status-panel.emergency::after {
  border-color: rgba(255, 95, 109, 0.22);
  box-shadow: 0 0 0 34px rgba(255, 95, 109, 0.05), 0 0 0 70px rgba(255, 95, 109, 0.03);
}

.status-content {
  position: relative;
  z-index: 1;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: #78aeea;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.status-title {
  margin: 18px 0 8px;
  color: var(--green);
  font-size: clamp(2.1rem, 5vw, 4rem);
  letter-spacing: -0.07em;
  line-height: 0.95;
}

.status-panel.warning .status-title {
  color: var(--yellow);
}

.status-panel.emergency .status-title {
  color: var(--red);
}

.status-description {
  max-width: 520px;
  margin: 0;
  color: #a7bad0;
  font-size: 0.88rem;
  line-height: 1.6;
}

.status-orbit {
  position: relative;
  z-index: 1;
  display: grid;
  width: 116px;
  height: 116px;
  place-items: center;
  align-self: center;
  border: 1px solid rgba(54, 213, 141, 0.3);
  border-radius: 50%;
  color: var(--green);
  background: rgba(54, 213, 141, 0.07);
  box-shadow: inset 0 0 35px rgba(54, 213, 141, 0.06), 0 0 30px rgba(54, 213, 141, 0.08);
}

.status-orbit::before {
  position: absolute;
  inset: 10px;
  border: 1px dashed currentColor;
  border-radius: inherit;
  opacity: 0.35;
  content: '';
  animation: orbit 16s linear infinite;
}

.status-panel.warning .status-orbit {
  border-color: rgba(247, 199, 93, 0.35);
  color: var(--yellow);
  background: rgba(247, 199, 93, 0.07);
}

.status-panel.emergency .status-orbit {
  border-color: rgba(255, 95, 109, 0.4);
  color: var(--red);
  background: rgba(255, 95, 109, 0.08);
}

@keyframes orbit {
  to { transform: rotate(360deg); }
}

.arm64-panel {
  display: flex;
  flex-direction: column;
  min-height: 230px;
  padding: 24px;
  border-radius: 18px;
}

.panel-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.panel-heading h3 {
  margin: 8px 0 0;
  color: var(--text);
  font-size: 1rem;
}

.panel-icon {
  display: grid;
  width: 40px;
  height: 40px;
  place-items: center;
  border: 1px solid rgba(167, 139, 250, 0.28);
  border-radius: 11px;
  color: var(--violet);
  background: rgba(167, 139, 250, 0.09);
}

.arm64-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: auto;
}

.arm64-stat {
  padding: 12px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: rgba(4, 12, 21, 0.34);
}

.arm64-stat span,
.arm64-stat strong {
  display: block;
}

.arm64-stat span {
  color: var(--muted);
  font-size: 0.65rem;
  text-transform: uppercase;
}

.arm64-stat strong {
  margin-top: 5px;
  color: var(--text);
  font-size: 1.18rem;
}

.section-block {
  padding-top: 36px;
  scroll-margin-top: 20px;
}

.section-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 17px;
}

.section-heading h2 {
  margin: 7px 0 0;
  color: var(--text);
  font-size: 1.15rem;
  letter-spacing: -0.025em;
}

.section-copy {
  margin: 0;
  color: var(--muted);
  font-size: 0.75rem;
}

.live-indicator {
  color: #9bb0c7;
  font-size: 0.72rem;
  font-weight: 700;
}

.sensor-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(150px, 1fr));
  gap: 12px;
}

.sensor-card {
  position: relative;
  min-width: 0;
  min-height: 146px;
  padding: 16px;
  overflow: hidden;
  border-radius: 14px;
  color: var(--blue);
  text-align: left;
  cursor: pointer;
  transition: transform 160ms ease, border-color 160ms ease, background 160ms ease;
}

.sensor-card:hover,
.sensor-card.active {
  border-color: var(--border-strong);
  transform: translateY(-2px);
}

.sensor-card.active {
  background: linear-gradient(150deg, rgba(19, 45, 75, 0.95), rgba(9, 20, 33, 0.96));
}

.sensor-card::after {
  position: absolute;
  right: -25px;
  bottom: -30px;
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: currentColor;
  filter: blur(34px);
  opacity: 0.08;
  content: '';
}

.sensor-card.orange { color: var(--orange); }
.sensor-card.blue { color: #5eb8ff; }
.sensor-card.red { color: var(--red); }
.sensor-card.violet { color: var(--violet); }
.sensor-card.yellow { color: var(--yellow); }

.sensor-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sensor-icon {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  border: 1px solid currentColor;
  border-radius: 9px;
  background: color-mix(in srgb, currentColor 9%, transparent);
  opacity: 0.9;
}

.sensor-label {
  color: #9bb0c8;
  font-size: 0.7rem;
  font-weight: 700;
}

.sensor-reading {
  display: flex;
  align-items: baseline;
  gap: 5px;
  margin-top: 14px;
}

.sensor-reading strong {
  color: var(--text);
  font-size: 1.65rem;
  letter-spacing: -0.055em;
}

.sensor-reading span {
  color: var(--muted);
  font-size: 0.68rem;
}

.sensor-helper {
  display: block;
  margin-top: 8px;
  overflow: hidden;
  color: #6f859e;
  font-size: 0.62rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chart-panel {
  margin-top: 14px;
  padding: 20px;
  border-radius: 16px;
}

.chart-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 18px;
}

.chart-toolbar h3 {
  margin: 0;
  color: var(--text);
  font-size: 0.9rem;
}

.chart-toolbar p {
  margin: 5px 0 0;
  color: var(--muted);
  font-size: 0.67rem;
}

.chart-tabs {
  display: flex;
  gap: 5px;
  padding: 4px;
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: rgba(4, 12, 21, 0.32);
}

.chart-tab {
  padding: 7px 10px;
  border-radius: 7px;
  color: #8196ae;
  background: transparent;
  font-size: 0.66rem;
  font-weight: 700;
  cursor: pointer;
}

.chart-tab.active {
  color: #dcecff;
  background: rgba(76, 156, 255, 0.14);
}

.chart-wrap {
  height: 285px;
}

.controls-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.control-card {
  padding: 18px;
  border-radius: 14px;
}

.control-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.control-title {
  display: flex;
  align-items: center;
  gap: 9px;
  color: var(--text);
  font-size: 0.82rem;
  font-weight: 800;
}

.control-title svg {
  color: var(--blue);
}

.status-chip {
  min-height: 24px;
  padding: 0 8px;
  border: 1px solid var(--border);
  border-radius: 999px;
  color: #a8bbd0;
  background: rgba(4, 12, 21, 0.35);
  font-size: 0.58rem;
  font-weight: 800;
  letter-spacing: 0.04em;
}

.status-chip.normal,
.status-chip.on,
.status-chip.open {
  border-color: rgba(54, 213, 141, 0.24);
  color: #79e7b2;
  background: rgba(54, 213, 141, 0.07);
}

.status-chip.warning {
  border-color: rgba(247, 199, 93, 0.28);
  color: var(--yellow);
}

.status-chip.emergency,
.status-chip.alarm {
  border-color: rgba(255, 95, 109, 0.3);
  color: #ff8994;
}

.control-description {
  min-height: 34px;
  margin: 12px 0 15px;
  color: var(--muted);
  font-size: 0.66rem;
  line-height: 1.5;
}

.button-row,
.mode-row {
  display: flex;
  gap: 7px;
}

.action-button {
  display: inline-flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  min-height: 35px;
  padding: 0 10px;
  border: 1px solid var(--border);
  border-radius: 8px;
  color: #aabed4;
  background: rgba(4, 12, 21, 0.4);
  font-size: 0.65rem;
  font-weight: 800;
  cursor: pointer;
  transition: 150ms ease;
}

.action-button:hover,
.action-button.active {
  border-color: rgba(76, 156, 255, 0.38);
  color: #e7f2ff;
  background: rgba(76, 156, 255, 0.13);
}

.action-button.danger:hover {
  border-color: rgba(255, 95, 109, 0.4);
  color: #ffd9dc;
  background: rgba(255, 95, 109, 0.1);
}

.activity-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.activity-card {
  overflow: hidden;
  border-radius: 14px;
}

.activity-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 18px;
  border-bottom: 1px solid var(--border);
}

.activity-card-header h3 {
  margin: 0;
  color: var(--text);
  font-size: 0.82rem;
}

.activity-count {
  color: var(--muted);
  font-size: 0.65rem;
}

.activity-table {
  width: 100%;
  border-collapse: collapse;
}

.activity-table th,
.activity-table td {
  padding: 12px 18px;
  border-bottom: 1px solid rgba(151, 178, 211, 0.08);
  text-align: left;
  vertical-align: middle;
}

.activity-table tr:last-child td {
  border-bottom: 0;
}

.activity-table th {
  color: #687e97;
  font-size: 0.58rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.activity-table td {
  color: #a9bdd3;
  font-size: 0.68rem;
}

.activity-primary {
  display: block;
  color: #d8e7f8;
  font-weight: 700;
}

.activity-secondary {
  display: block;
  margin-top: 3px;
  color: #6f859d;
  font-size: 0.6rem;
}

.empty-row {
  padding: 28px !important;
  color: var(--muted) !important;
  text-align: center !important;
}

.app-footer {
  padding: 36px 0 8px;
  color: #60758e;
  font-size: 0.68rem;
  text-align: center;
}

@media (max-width: 1180px) {
  .sensor-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .controls-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: relative;
    display: grid;
    grid-template-columns: auto 1fr;
    height: auto;
    padding: 15px 20px;
    border-right: 0;
    border-bottom: 1px solid var(--border);
  }

  .brand {
    margin: 0;
  }

  .sidebar-nav {
    display: flex;
    justify-content: flex-end;
  }

  .nav-link {
    min-height: 40px;
  }

  .nav-link span {
    display: none;
  }

  .sidebar-status {
    display: none;
  }

  .overview-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 680px) {
  .workspace {
    padding: 0 16px 28px;
  }

  .app-header {
    align-items: flex-start;
    min-height: auto;
    padding: 24px 0;
  }

  .header-meta {
    align-items: flex-end;
    flex-direction: column;
    gap: 7px;
  }

  .header-meta time {
    font-size: 0.66rem;
  }

  .status-panel {
    grid-template-columns: 1fr;
    min-height: 260px;
    padding: 22px;
  }

  .status-orbit {
    position: absolute;
    right: 18px;
    bottom: 18px;
    width: 72px;
    height: 72px;
  }

  .sensor-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .section-heading,
  .chart-toolbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .chart-tabs {
    width: 100%;
  }

  .controls-grid,
  .activity-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 420px) {
  .sensor-grid {
    grid-template-columns: 1fr;
  }

  .sidebar {
    grid-template-columns: 1fr;
  }

  .sidebar-nav {
    justify-content: space-between;
    margin-top: 12px;
  }
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    scroll-behavior: auto !important;
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
