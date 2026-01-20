import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Visualization3D from './pages/Visualization3D'
import Reports from './pages/Reports'
import SimulationConfig from './pages/SimulationConfig'
import ScenarioModeling from './pages/ScenarioModeling'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="nav-brand">
            <h1>🩸 Platelet Pooling Digital Twin</h1>
          </div>
          <div className="nav-links">
            <NavLink to="/" className={({ isActive }) => isActive ? 'active' : ''}>
              Dashboard
            </NavLink>
            <NavLink to="/3d" className={({ isActive }) => isActive ? 'active' : ''}>
              3D View
            </NavLink>
            <NavLink to="/scenarios" className={({ isActive }) => isActive ? 'active' : ''}>
              Scenarios
            </NavLink>
            <NavLink to="/reports" className={({ isActive }) => isActive ? 'active' : ''}>
              Reports
            </NavLink>
            <NavLink to="/config" className={({ isActive }) => isActive ? 'active' : ''}>
              Configuration
            </NavLink>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/3d" element={<Visualization3D />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/config" element={<SimulationConfig />} />              <Route path="/scenarios" element={<ScenarioModeling />} />          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
