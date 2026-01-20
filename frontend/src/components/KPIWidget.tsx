import './KPIWidget.css'

interface KPIWidgetProps {
  title: string
  value: string | number
  icon: string
  color: 'primary' | 'success' | 'error' | 'warning' | 'idle'
  subtitle?: string
}

function KPIWidget({ title, value, icon, color, subtitle }: KPIWidgetProps) {
  return (
    <div className={`kpi-widget kpi-${color}`}>
      <div className="kpi-icon">{icon}</div>
      <div className="kpi-content">
        <div className="kpi-title">{title}</div>
        <div className="kpi-value">{value}</div>
        {subtitle && <div className="kpi-subtitle">{subtitle}</div>}
      </div>
    </div>
  )
}

export default KPIWidget
