import { useState, useEffect } from 'react'
import { useDigitalTwins } from '../hooks/useDigitalTwins'
import DeviceCard from '../components/DeviceCard'
import KPIWidget from '../components/KPIWidget'
import ProcessFlow from '../components/ProcessFlow'
import './Dashboard.css'

interface DeviceTwin {
  $dtId: string
  deviceType: string
  state: string
  isProcessing: boolean
  currentBatchId?: string
  errorState?: string
  lastTelemetryTime?: string
  // Device-specific properties
  rpm?: number
  temperature?: number
  vibration?: number
  pressure?: number
  flowRate?: number
}

function Dashboard() {
  const { twins, loading, error, refresh } = useDigitalTwins()
  const [kpis, setKpis] = useState({
    totalDevices: 0,
    activeDevices: 0,
    idleDevices: 0,
    errorDevices: 0,
    avgUtilization: 0,
    throughputPerHour: 0,
    avgCycleTime: 0
  })

  useEffect(() => {
    if (twins) {
      calculateKPIs(twins)
    }
  }, [twins])

  const calculateKPIs = (deviceTwins: DeviceTwin[]) => {
    const total = deviceTwins.length
    const active = deviceTwins.filter(d => d.isProcessing).length
    const idle = deviceTwins.filter(d => d.state === 'idle').length
    const errors = deviceTwins.filter(d => d.state === 'error').length
    const utilization = total > 0 ? (active / total) * 100 : 0

    setKpis({
      totalDevices: total,
      activeDevices: active,
      idleDevices: idle,
      errorDevices: errors,
      avgUtilization: utilization,
      throughputPerHour: active * 3.2, // Estimated based on cycle times
      avgCycleTime: 15 // Minutes - placeholder
    })
  }

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-state">
        <h2>Error Loading Dashboard</h2>
        <p>{error}</p>
        <button className="btn btn-primary" onClick={refresh}>Retry</button>
      </div>
    )
  }

  return (
    <div className="dashboard">
      <div className="page-header">
        <h2>Lab Operations Dashboard</h2>
        <p>Real-time monitoring of platelet pooling process</p>
        <div className="header-actions">
          <button className="btn btn-secondary" onClick={refresh}>
            🔄 Refresh
          </button>
          <span className="last-update">
            Last updated: {new Date().toLocaleTimeString()}
          </span>
        </div>
      </div>

      {/* KPI Overview */}
      <div className="kpi-grid">
        <KPIWidget
          title="Total Devices"
          value={kpis.totalDevices}
          icon="📦"
          color="primary"
        />
        <KPIWidget
          title="Active Devices"
          value={kpis.activeDevices}
          icon="⚙️"
          color="success"
          subtitle={`${kpis.avgUtilization.toFixed(1)}% utilization`}
        />
        <KPIWidget
          title="Idle Devices"
          value={kpis.idleDevices}
          icon="⏸️"
          color="idle"
        />
        <KPIWidget
          title="Error Devices"
          value={kpis.errorDevices}
          icon="⚠️"
          color="error"
        />
        <KPIWidget
          title="Throughput"
          value={`${kpis.throughputPerHour.toFixed(1)}/hr`}
          icon="📈"
          color="primary"
          subtitle="Units per hour"
        />
        <KPIWidget
          title="Avg Cycle Time"
          value={`${kpis.avgCycleTime} min`}
          icon="⏱️"
          color="primary"
        />
      </div>

      {/* Process Flow Visualization */}
      <div className="section">
        <ProcessFlow devices={twins || []} />
      </div>

      {/* Device Status Grid */}
      <div className="section">
        <div className="card">
          <div className="card-header">
            <h3>Device Status</h3>
            <div className="filter-buttons">
              <button className="filter-btn active">All</button>
              <button className="filter-btn">Processing</button>
              <button className="filter-btn">Idle</button>
              <button className="filter-btn">Errors</button>
            </div>
          </div>
          <div className="devices-grid">
            {twins?.map(device => (
              <DeviceCard key={device.$dtId} device={device} />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
