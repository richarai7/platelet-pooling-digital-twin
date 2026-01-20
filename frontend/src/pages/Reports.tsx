import { useState } from 'react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import './Reports.css'

function Reports() {
  const [timeRange, setTimeRange] = useState('24h')
  const [reportType, setReportType] = useState('performance')

  // Mock data - will be replaced with real Azure Data Explorer queries
  const performanceData = [
    { time: '00:00', throughput: 12, utilization: 65, cycleTime: 15.2 },
    { time: '04:00', throughput: 8, utilization: 45, cycleTime: 16.1 },
    { time: '08:00', throughput: 18, utilization: 85, cycleTime: 14.8 },
    { time: '12:00', throughput: 20, utilization: 92, cycleTime: 14.5 },
    { time: '16:00', throughput: 22, utilization: 95, cycleTime: 14.2 },
    { time: '20:00', throughput: 15, utilization: 70, cycleTime: 15.5 },
  ]

  const qualityData = [
    { device: 'Centrifuge-01', separationQuality: 95, plateletYield: 92, avgScore: 93.5 },
    { device: 'Centrifuge-02', separationQuality: 93, plateletYield: 90, avgScore: 91.5 },
    { device: 'Centrifuge-03', separationQuality: 96, plateletYield: 94, avgScore: 95.0 },
    { device: 'Macopress-01', separationQuality: 94, plateletYield: 91, avgScore: 92.5 },
    { device: 'Macopress-02', separationQuality: 92, plateletYield: 89, avgScore: 90.5 },
  ]

  const deviceHealthData = [
    { device: 'Centrifuge-01', uptime: 98.5, errors: 2, avgTemp: 23.2, avgVibration: 1.4 },
    { device: 'Centrifuge-02', uptime: 99.2, errors: 1, avgTemp: 22.8, avgVibration: 1.2 },
    { device: 'Centrifuge-03', uptime: 97.8, errors: 3, avgTemp: 24.1, avgVibration: 1.8 },
    { device: 'Macopress-01', uptime: 99.5, errors: 0, avgTemp: 21.5, avgVibration: 0.8 },
    { device: 'Macopress-02', uptime: 96.2, errors: 5, avgTemp: 22.9, avgVibration: 1.1 },
  ]

  return (
    <div className="reports">
      <div className="page-header">
        <h2>Analytics & Reports</h2>
        <p>Historical data analysis and insights</p>
      </div>

      {/* Controls */}
      <div className="report-controls">
        <div className="control-group">
          <label>Report Type:</label>
          <select value={reportType} onChange={(e) => setReportType(e.target.value)}>
            <option value="performance">Performance Metrics</option>
            <option value="quality">Quality Analysis</option>
            <option value="health">Device Health</option>
            <option value="capacity">Capacity Planning</option>
          </select>
        </div>
        <div className="control-group">
          <label>Time Range:</label>
          <select value={timeRange} onChange={(e) => setTimeRange(e.target.value)}>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="custom">Custom Range</option>
          </select>
        </div>
        <button className="btn btn-primary">📥 Export Report</button>
      </div>

      {/* Performance Metrics */}
      {reportType === 'performance' && (
        <div className="report-section">
          <div className="card">
            <div className="card-header">
              <h3>Throughput Over Time</h3>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#3f3f3f" />
                <XAxis dataKey="time" stroke="#a0a0a0" />
                <YAxis stroke="#a0a0a0" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#2d2d2d', border: '1px solid #3f3f3f' }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="throughput" 
                  stroke="#0078d4" 
                  strokeWidth={2}
                  name="Units/Hour"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <div className="card-header">
              <h3>Device Utilization</h3>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#3f3f3f" />
                <XAxis dataKey="time" stroke="#a0a0a0" />
                <YAxis stroke="#a0a0a0" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#2d2d2d', border: '1px solid #3f3f3f' }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="utilization" 
                  stroke="#107c10" 
                  strokeWidth={2}
                  name="Utilization %"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <div className="card-header">
              <h3>Average Cycle Time</h3>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#3f3f3f" />
                <XAxis dataKey="time" stroke="#a0a0a0" />
                <YAxis stroke="#a0a0a0" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#2d2d2d', border: '1px solid #3f3f3f' }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="cycleTime" 
                  stroke="#f7630c" 
                  strokeWidth={2}
                  name="Minutes"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Quality Analysis */}
      {reportType === 'quality' && (
        <div className="report-section">
          <div className="card">
            <div className="card-header">
              <h3>Quality Metrics by Device</h3>
            </div>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={qualityData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#3f3f3f" />
                <XAxis dataKey="device" stroke="#a0a0a0" />
                <YAxis stroke="#a0a0a0" domain={[0, 100]} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#2d2d2d', border: '1px solid #3f3f3f' }}
                />
                <Legend />
                <Bar dataKey="separationQuality" fill="#0078d4" name="Separation Quality %" />
                <Bar dataKey="plateletYield" fill="#107c10" name="Platelet Yield %" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <div className="card-header">
              <h3>Quality Summary</h3>
            </div>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Device</th>
                  <th>Separation Quality</th>
                  <th>Platelet Yield</th>
                  <th>Average Score</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {qualityData.map((row) => (
                  <tr key={row.device}>
                    <td>{row.device}</td>
                    <td>{row.separationQuality}%</td>
                    <td>{row.plateletYield}%</td>
                    <td><strong>{row.avgScore}%</strong></td>
                    <td>
                      <span className={`status-badge ${row.avgScore >= 92 ? 'status-processing' : 'status-idle'}`}>
                        {row.avgScore >= 92 ? 'Excellent' : 'Good'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Device Health */}
      {reportType === 'health' && (
        <div className="report-section">
          <div className="card">
            <div className="card-header">
              <h3>Device Health Overview</h3>
            </div>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Device</th>
                  <th>Uptime %</th>
                  <th>Errors</th>
                  <th>Avg Temp (°C)</th>
                  <th>Avg Vibration</th>
                  <th>Health Status</th>
                </tr>
              </thead>
              <tbody>
                {deviceHealthData.map((row) => (
                  <tr key={row.device}>
                    <td>{row.device}</td>
                    <td>{row.uptime}%</td>
                    <td>{row.errors}</td>
                    <td>{row.avgTemp}</td>
                    <td>{row.avgVibration} mm/s</td>
                    <td>
                      <span className={`status-badge ${
                        row.uptime >= 99 && row.errors === 0 ? 'status-processing' : 
                        row.uptime >= 97 ? 'status-idle' : 'status-error'
                      }`}>
                        {row.uptime >= 99 && row.errors === 0 ? 'Excellent' : 
                         row.uptime >= 97 ? 'Good' : 'Attention Required'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="grid-2">
            <div className="card">
              <div className="card-header">
                <h3>Uptime Comparison</h3>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={deviceHealthData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#3f3f3f" />
                  <XAxis dataKey="device" stroke="#a0a0a0" />
                  <YAxis stroke="#a0a0a0" domain={[95, 100]} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#2d2d2d', border: '1px solid #3f3f3f' }}
                  />
                  <Bar dataKey="uptime" fill="#107c10" name="Uptime %" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="card">
              <div className="card-header">
                <h3>Error Count</h3>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={deviceHealthData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#3f3f3f" />
                  <XAxis dataKey="device" stroke="#a0a0a0" />
                  <YAxis stroke="#a0a0a0" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#2d2d2d', border: '1px solid #3f3f3f' }}
                  />
                  <Bar dataKey="errors" fill="#d13438" name="Errors" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* Capacity Planning */}
      {reportType === 'capacity' && (
        <div className="report-section">
          <div className="card">
            <div className="card-header">
              <h3>Capacity Planning Scenarios</h3>
            </div>
            <div className="scenario-grid">
              <div className="scenario-card">
                <h4>Current Capacity</h4>
                <div className="metric-large">18.5</div>
                <p>Units/Hour</p>
                <div className="scenario-details">
                  <p>9 Active Devices</p>
                  <p>85% Avg Utilization</p>
                </div>
              </div>

              <div className="scenario-card highlight">
                <h4>+10% Supply Increase</h4>
                <div className="metric-large">20.4</div>
                <p>Units/Hour Needed</p>
                <div className="scenario-details">
                  <p>Requires: +1 Device OR +2 Staff</p>
                  <p>Est. Investment: $50K</p>
                </div>
              </div>

              <div className="scenario-card">
                <h4>One Device Down</h4>
                <div className="metric-large">16.7</div>
                <p>Units/Hour</p>
                <div className="scenario-details">
                  <p>-9.7% Capacity</p>
                  <p>Mitigation: Extend shifts by 1hr</p>
                </div>
              </div>

              <div className="scenario-card">
                <h4>Optimized Schedule</h4>
                <div className="metric-large">21.2</div>
                <p>Units/Hour</p>
                <div className="scenario-details">
                  <p>+14.6% vs Current</p>
                  <p>No additional investment</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Reports
