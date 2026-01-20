import './SimulationConfig.css'

function SimulationConfig() {
  return (
    <div className="simulation-config">
      <div className="page-header">
        <h2>Simulation Configuration</h2>
        <p>Configure "what-if" scenarios to test operational changes</p>
      </div>

      <div className="config-grid">
        {/* Scenario Selection */}
        <div className="card">
          <div className="card-header">
            <h3>Scenario Templates</h3>
          </div>
          <div className="scenario-templates">
            <button className="template-btn">
              📊 Current Production
            </button>
            <button className="template-btn">
              ⬆️ +10% Supply Increase
            </button>
            <button className="template-btn">
              🔧 One Device Maintenance
            </button>
            <button className="template-btn">
              👥 Staff Shortage (-2 people)
            </button>
            <button className="template-btn">
              ⚡ Peak Efficiency Test
            </button>
            <button className="template-btn active">
              ✨ Custom Scenario
            </button>
          </div>
        </div>

        {/* Device Configuration */}
        <div className="card">
          <div className="card-header">
            <h3>Device Configuration</h3>
          </div>
          <div className="device-config">
            <div className="config-row">
              <label>Centrifuges</label>
              <input type="number" min="0" max="10" defaultValue="3" />
              <span className="current-value">Current: 3</span>
            </div>
            <div className="config-row">
              <label>Macopress Units</label>
              <input type="number" min="0" max="10" defaultValue="3" />
              <span className="current-value">Current: 3</span>
            </div>
            <div className="config-row">
              <label>Platelet Agitators</label>
              <input type="number" min="0" max="10" defaultValue="3" />
              <span className="current-value">Current: 3</span>
            </div>
          </div>
        </div>

        {/* Staffing Configuration */}
        <div className="card">
          <div className="card-header">
            <h3>Staffing Configuration</h3>
          </div>
          <div className="device-config">
            <div className="config-row">
              <label>Scientists</label>
              <input type="number" min="1" max="20" defaultValue="5" />
              <span className="current-value">Current: 5</span>
            </div>
            <div className="config-row">
              <label>Technicians</label>
              <input type="number" min="1" max="20" defaultValue="8" />
              <span className="current-value">Current: 8</span>
            </div>
            <div className="config-row">
              <label>Shift Duration (hours)</label>
              <input type="number" min="4" max="12" defaultValue="8" />
              <span className="current-value">Current: 8</span>
            </div>
          </div>
        </div>

        {/* Supply Configuration */}
        <div className="card">
          <div className="card-header">
            <h3>Supply Configuration</h3>
          </div>
          <div className="device-config">
            <div className="config-row">
              <label>Daily Donations</label>
              <input type="number" min="50" max="500" defaultValue="200" />
              <span className="current-value">Current: 200</span>
            </div>
            <div className="config-row">
              <label>Batch Size</label>
              <input type="number" min="1" max="10" defaultValue="4" />
              <span className="current-value">Current: 4</span>
            </div>
            <div className="config-row">
              <label>Supply Variance (%)</label>
              <input type="number" min="0" max="50" defaultValue="10" />
              <span className="current-value">Current: 10</span>
            </div>
          </div>
        </div>

        {/* Simulation Parameters */}
        <div className="card">
          <div className="card-header">
            <h3>Simulation Parameters</h3>
          </div>
          <div className="device-config">
            <div className="config-row">
              <label>Simulation Duration</label>
              <select defaultValue="24h">
                <option value="8h">8 Hours</option>
                <option value="24h">24 Hours</option>
                <option value="7d">7 Days</option>
                <option value="30d">30 Days</option>
              </select>
            </div>
            <div className="config-row">
              <label>Time Acceleration</label>
              <select defaultValue="10x">
                <option value="1x">Real-time (1x)</option>
                <option value="10x">10x Speed</option>
                <option value="100x">100x Speed</option>
                <option value="1000x">1000x Speed</option>
              </select>
            </div>
            <div className="config-row">
              <label>Fault Injection</label>
              <select defaultValue="none">
                <option value="none">None</option>
                <option value="low">Low (1% chance)</option>
                <option value="medium">Medium (5% chance)</option>
                <option value="high">High (10% chance)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Predicted Outcomes */}
        <div className="card highlight-card">
          <div className="card-header">
            <h3>📊 Predicted Outcomes</h3>
          </div>
          <div className="outcomes-grid">
            <div className="outcome-metric">
              <div className="outcome-label">Est. Throughput</div>
              <div className="outcome-value">18.5 <span>units/hr</span></div>
              <div className="outcome-change positive">+5.2% vs current</div>
            </div>
            <div className="outcome-metric">
              <div className="outcome-label">Est. Utilization</div>
              <div className="outcome-value">87% <span></span></div>
              <div className="outcome-change positive">+3% vs current</div>
            </div>
            <div className="outcome-metric">
              <div className="outcome-label">Est. Cycle Time</div>
              <div className="outcome-value">14.2 <span>min</span></div>
              <div className="outcome-change negative">+0.5 min vs current</div>
            </div>
            <div className="outcome-metric">
              <div className="outcome-label">Est. Daily Output</div>
              <div className="outcome-value">296 <span>units</span></div>
              <div className="outcome-change positive">+8.4% vs current</div>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="action-bar">
        <button className="btn btn-secondary">💾 Save Scenario</button>
        <button className="btn btn-secondary">📋 Load Scenario</button>
        <button className="btn btn-secondary">🔄 Reset to Current</button>
        <button className="btn btn-primary">▶️ Run Simulation</button>
      </div>
    </div>
  )
}

export default SimulationConfig
