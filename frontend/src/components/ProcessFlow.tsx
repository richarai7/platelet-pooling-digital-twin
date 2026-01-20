import './ProcessFlow.css'

interface ProcessFlowProps {
  devices: any[]
}

function ProcessFlow({ devices }: ProcessFlowProps) {
  const stages = [
    { name: 'Centrifugation', devices: devices.filter(d => d.deviceType === 'centrifuge') },
    { name: 'Pressing', devices: devices.filter(d => d.deviceType === 'macopress') },
    { name: 'Agitation', devices: devices.filter(d => d.deviceType === 'agitator') },
  ]

  return (
    <div className="card">
      <div className="card-header">
        <h3>Process Flow</h3>
      </div>
      <div className="process-flow">
        {stages.map((stage, idx) => (
          <div key={stage.name}>
            <div className="stage">
              <div className="stage-header">
                <h4>{stage.name}</h4>
                <span className="stage-count">
                  {stage.devices.filter(d => d.isProcessing).length}/{stage.devices.length} active
                </span>
              </div>
              <div className="stage-devices">
                {stage.devices.map(device => (
                  <div 
                    key={device.$dtId} 
                    className={`device-indicator ${device.state}`}
                    title={`${device.$dtId} - ${device.state}`}
                  >
                    <div className="indicator-dot"></div>
                  </div>
                ))}
              </div>
            </div>
            {idx < stages.length - 1 && (
              <div className="flow-arrow">→</div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default ProcessFlow
