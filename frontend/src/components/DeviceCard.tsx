import './DeviceCard.css'

interface DeviceCardProps {
  device: {
    $dtId: string
    deviceType: string
    state: string
    isProcessing: boolean
    currentBatchId?: string
    errorState?: string
    [key: string]: any
  }
}

function DeviceCard({ device }: DeviceCardProps) {
  const getDeviceIcon = (type: string) => {
    switch (type) {
      case 'centrifuge': return '🌀'
      case 'macopress': return '⚙️'
      case 'agitator': return '🔄'
      default: return '📦'
    }
  }

  return (
    <div className={`device-card state-${device.state}`}>
      <div className="device-card-header">
        <span className="device-icon">{getDeviceIcon(device.deviceType)}</span>
        <div className="device-info">
          <h4>{device.$dtId}</h4>
          <span className="device-type">{device.deviceType}</span>
        </div>
        <span className={`status-badge status-${device.state}`}>
          {device.state}
        </span>
      </div>

      <div className="device-card-body">
        {device.isProcessing && (
          <div className="processing-info">
            <p className="batch-id">📋 {device.currentBatchId}</p>
            {device.remainingTimeSeconds !== undefined && (
              <p className="time-remaining">
                ⏱️ {Math.floor(device.remainingTimeSeconds / 60)}:{(device.remainingTimeSeconds % 60).toString().padStart(2, '0')} remaining
              </p>
            )}
          </div>
        )}

        {device.errorState && (
          <div className="error-info">
            ⚠️ {device.errorState}
          </div>
        )}

        <div className="device-metrics">
          {device.rpm !== undefined && (
            <div className="metric">
              <span className="metric-label">RPM</span>
              <span className="metric-value">{device.rpm.toFixed(0)}</span>
            </div>
          )}
          {device.temperature !== undefined && (
            <div className="metric">
              <span className="metric-label">Temp</span>
              <span className="metric-value">{device.temperature.toFixed(1)}°C</span>
            </div>
          )}
          {device.vibration !== undefined && (
            <div className="metric">
              <span className="metric-label">Vibration</span>
              <span className="metric-value">{device.vibration.toFixed(2)}</span>
            </div>
          )}
          {device.pressure !== undefined && (
            <div className="metric">
              <span className="metric-label">Pressure</span>
              <span className="metric-value">{device.pressure} PSI</span>
            </div>
          )}
          {device.flowRate !== undefined && (
            <div className="metric">
              <span className="metric-label">Flow</span>
              <span className="metric-value">{device.flowRate} L/m</span>
            </div>
          )}
        </div>
      </div>

      <div className="device-card-footer">
        <span className="last-update">
          Updated: {device.lastTelemetryTime ? new Date(device.lastTelemetryTime).toLocaleTimeString() : 'N/A'}
        </span>
      </div>
    </div>
  )
}

export default DeviceCard
