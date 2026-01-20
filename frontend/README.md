# Frontend - Platelet Pooling Digital Twin

React-based dashboard for monitoring and controlling the platelet pooling simulation.

## Features

### 📊 Dashboard (2D KPIs)
- **Real-time metrics**: Total devices, active/idle counts, utilization rates
- **Device cards**: Live status of all 12 devices with telemetry
- **Process flow**: Visual representation of the 3-stage workflow
- **Auto-refresh**: Updates every 5 seconds from Azure Digital Twins

### 🎮 3D Visualization
- **Interactive 3D lab**: Babylon.js-powered view of device layout
- **Device states**: Color-coded by status (idle=gray, processing=blue, error=red)
- **Click for details**: Interactive device information panels
- **Camera controls**: Rotate, pan, and zoom the view

### 📈 Reports & Analytics
- **Performance metrics**: Throughput, utilization, cycle time over time
- **Quality analysis**: Separation quality and platelet yield by device
- **Device health**: Uptime, error rates, temperature, vibration trends
- **Capacity planning**: "What-if" scenario predictions

### ⚙️ Simulation Configuration
- **Scenario templates**: Pre-built configurations (supply increase, device down, etc.)
- **Device configuration**: Adjust number of each device type
- **Staffing**: Configure scientists, technicians, shift duration
- **Supply parameters**: Daily donations, batch size, variance
- **Predicted outcomes**: Real-time impact estimation

## Technology Stack

- **Framework**: React 18 + TypeScript
- **Build**: Vite
- **3D**: Babylon.js
- **Charts**: Recharts
- **Routing**: React Router
- **Data**: Azure Digital Twins API
- **Real-time**: SignalR (future)

## Quick Start

### Development Mode

```bash
# Install dependencies
cd frontend
npm install

# Start dev server
npm run dev
```

Visit http://localhost:3000

### Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── DeviceCard.tsx   # Device status card
│   │   ├── KPIWidget.tsx    # KPI metric widget
│   │   └── ProcessFlow.tsx  # Process flow visualization
│   ├── hooks/               # Custom React hooks
│   │   └── useDigitalTwins.ts # Azure Digital Twins data hook
│   ├── pages/               # Main views
│   │   ├── Dashboard.tsx    # 2D KPI dashboard
│   │   ├── Visualization3D.tsx # 3D lab view
│   │   ├── Reports.tsx      # Analytics & reports
│   │   └── SimulationConfig.tsx # Scenario configuration
│   ├── App.tsx              # Main app & routing
│   └── main.tsx             # Entry point
├── index.html
├── package.json
└── vite.config.ts
```

## API Integration

### Azure Digital Twins Hook

The `useDigitalTwins()` hook fetches live device data:

```typescript
const { twins, loading, error, refresh } = useDigitalTwins()
```

Currently uses mock data. To connect to Azure:

1. Create an Azure Function API endpoint
2. Update `hooks/useDigitalTwins.ts`:

```typescript
const response = await fetch('/api/twins')
const data = await response.json()
setTwins(data)
```

### Expected Data Format

```json
{
  "$dtId": "centrifuge-01",
  "deviceType": "centrifuge",
  "state": "processing",
  "isProcessing": true,
  "currentBatchId": "BATCH-001",
  "rpm": 2987,
  "temperature": 24.2,
  "vibration": 1.42,
  "remainingTimeSeconds": 540,
  "lastTelemetryTime": "2026-01-20T10:15:30Z"
}
```

## Environment Variables

Create `.env` in frontend directory:

```bash
VITE_API_BASE_URL=https://your-function-app.azurewebsites.net
VITE_SIGNALR_HUB_URL=https://your-function-app.azurewebsites.net/api
```

## Pages

### 1. Dashboard
- **Path**: `/`
- **Purpose**: Primary monitoring interface for Lab Ops Managers
- **Features**: Real-time KPIs, device grid, process flow

### 2. 3D View
- **Path**: `/3d`
- **Purpose**: Spatial visualization of lab layout
- **Features**: Interactive 3D models, device details panel

### 3. Reports
- **Path**: `/reports`
- **Purpose**: Historical data analysis
- **Features**: Charts, tables, trend analysis

### 4. Configuration
- **Path**: `/config`
- **Purpose**: Scenario modeling & "what-if" testing
- **Features**: Parameter adjustment, outcome prediction

## Styling

Uses CSS custom properties for theming (see `App.css`):

```css
--primary-color: #0078d4;      /* Azure blue */
--success-color: #107c10;      /* Green */
--error-color: #d13438;        /* Red */
--bg-dark: #1e1e1e;            /* Dark background */
--bg-light: #2d2d2d;           /* Card background */
```

## Next Steps

- [ ] Connect to real Azure Digital Twins API
- [ ] Implement SignalR for real-time updates (no polling)
- [ ] Add user authentication
- [ ] Create Azure Function API layer
- [ ] Add historical data queries to Azure Data Explorer
- [ ] Implement scenario save/load functionality
- [ ] Add export functionality for reports
- [ ] Create unit tests with Vitest
- [ ] Add E2E tests with Playwright

## Development Notes

### Mock Data
Currently all data is mocked in `useDigitalTwins.ts`. This allows frontend development without Azure backend.

### 3D Layout
Device positions are hardcoded in `Visualization3D.tsx`. Update the `devicePositions` array to match your lab layout.

### Charts
Uses Recharts for all visualizations. To add new charts, import components:

```typescript
import { LineChart, Line, XAxis, YAxis, ... } from 'recharts'
```

## Deployment

### Azure Static Web Apps

```bash
# Build
npm run build

# Deploy (using Azure CLI)
az staticwebapp create \
  --name platelet-pooling-frontend \
  --resource-group platelet-pooling-rg \
  --source ./dist
```

### Docker

```bash
# Build image
docker build -t platelet-pooling-frontend .

# Run
docker run -p 3000:80 platelet-pooling-frontend
```

## Troubleshooting

### Build Errors
If you see TypeScript errors, ensure all dependencies are installed:
```bash
npm install --legacy-peer-deps
```

### 3D Not Rendering
Check browser console for WebGL support:
```javascript
const canvas = document.createElement('canvas')
const gl = canvas.getContext('webgl')
console.log('WebGL supported:', !!gl)
```

### API Connection Issues
Check CORS configuration in Azure Function:
```json
{
  "cors": {
    "allowedOrigins": ["http://localhost:3000"]
  }
}
```
