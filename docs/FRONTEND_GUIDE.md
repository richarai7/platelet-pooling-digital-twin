# Frontend, Reports & 3D Visualization - Complete Guide

## 🎯 What We Built

A complete React-based dashboard with **4 main views** for monitoring and controlling the platelet pooling digital twin.

---

## 📱 Application Structure

```
┌─────────────────────────────────────────────────────────┐
│                    NAVIGATION BAR                        │
│  🩸 Platelet Pooling Digital Twin                       │
│  [Dashboard] [3D View] [Reports] [Configuration]        │
└─────────────────────────────────────────────────────────┘
          │              │           │            │
          ▼              ▼           ▼            ▼
    Dashboard Page   3D View    Reports Page   Config Page
```

---

## 1️⃣ Dashboard (2D KPIs) - Path: `/`

### Purpose
Real-time monitoring interface for Lab Operations Managers

### Features

**KPI Metrics Grid (Top)**
```
┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│ 📦 Total     │ ⚙️ Active    │ ⏸️ Idle      │ ⚠️ Error     │ 📈 Throughput│ ⏱️ Avg Cycle │
│ Devices      │ Devices      │ Devices      │ Devices      │              │ Time         │
│   9          │   3          │   5          │   1          │  18.5/hr     │  15 min      │
│              │ 85% util     │              │              │ Units/hour   │              │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
```

**Process Flow Visualization**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Centrifugation  │ →  │    Pressing     │ →  │   Agitation     │
│                 │    │                 │    │                 │
│ ● ● ●           │    │ ● ● ●           │    │ ● ● ●           │
│ 1/3 active      │    │ 1/3 active      │    │ 1/3 active      │
└─────────────────┘    └─────────────────┘    └─────────────────┘

Legend: ● Processing   ○ Idle   ⚠ Error
```

**Device Status Grid** (Scrollable)
```
┌──────────────────────────────────┐  ┌──────────────────────────────────┐
│ 🌀 Centrifuge-01                 │  │ 🌀 Centrifuge-02                 │
│ centrifuge                       │  │ centrifuge                       │
│                    [Processing]  │  │                    [Idle]        │
│                                  │  │                                  │
│ 📋 BATCH-20260120-001           │  │                                  │
│ ⏱️ 9:00 remaining                │  │                                  │
│                                  │  │                                  │
│ RPM: 2987   Temp: 24.2°C        │  │ RPM: 0      Temp: 22.1°C        │
│ Vibration: 1.42                  │  │ Vibration: 0.15                  │
│                                  │  │                                  │
│ Updated: 10:15:30                │  │ Updated: 10:15:30                │
└──────────────────────────────────┘  └──────────────────────────────────┘

... (9 total device cards)
```

### Data Flow
```
Azure Digital Twins
        ↓
useDigitalTwins() hook (polls every 5s)
        ↓
Dashboard Component
        ↓
    ┌───────┬──────────┬───────────┐
    │  KPIs │  Process │  Device   │
    │       │   Flow   │   Cards   │
    └───────┴──────────┴───────────┘
```

---

## 2️⃣ 3D Visualization - Path: `/3d`

### Purpose
Interactive spatial view of the lab layout using Babylon.js

### 3D Scene Layout
```
                    Lab Floor (40m x 40m)
        
   Centrifuges       Macopress       Agitators
   
      [🌀]              [⚙️]            [🔄]
      [🌀]              [⚙️]            [🔄]
      [🌀]              [⚙️]            [🔄]
    
  x: -8, z: 8        x: 0, z: 8      x: 8, z: 8
  x: -8, z: 4        x: 0, z: 4      x: 8, z: 4
  x: -8, z: 0        x: 0, z: 0      x: 8, z: 0
```

### Device Visual States
- **Idle**: Gray color, static
- **Processing**: Blue color, pulsing animation
- **Error**: Red color, blinking animation

### Camera Controls
```
🖱️ Left click + drag    → Rotate view
🖱️ Right click + drag   → Pan view
🖱️ Scroll wheel         → Zoom in/out
🖱️ Click device         → Show details panel
```

### Device Details Panel
```
┌─────────────────────────────────┐
│ Device Details              ✕   │
├─────────────────────────────────┤
│ ID: centrifuge-01               │
│ Type: centrifuge                │
│ Status: [Processing]            │
│ Batch: BATCH-20260120-001       │
│ RPM: 2987.0                     │
│ Temperature: 24.2°C             │
└─────────────────────────────────┘
```

### Controls Legend
```
┌──────────────────┐
│ Controls         │
├──────────────────┤
│ 🖱️ Mouse controls │
│                  │
│ Status Colors    │
│ ▪ Idle           │
│ ▪ Processing     │
│ ▪ Error          │
└──────────────────┘
```

---

## 3️⃣ Reports & Analytics - Path: `/reports`

### Report Types

#### A. Performance Metrics
**Throughput Over Time** (Line Chart)
```
Units/Hour
22 │         ●────●
20 │       ●/      
18 │     ●/        
16 │   ●/          
14 │ ●/            
   └─────────────────
   00:00  08:00  16:00
```

**Device Utilization** (Line Chart)
**Average Cycle Time** (Line Chart)

#### B. Quality Analysis
**Quality Metrics by Device** (Bar Chart)
```
Quality %
100│ ▓▓  ▓▓  ▓▓  ▓▓  ▓▓
 90│ ▓▓  ▓▓  ▓▓  ▓▓  ▓▓
 80│ ▓▓  ▓▓  ▓▓  ▓▓  ▓▓
   └───────────────────
    C-01 C-02 C-03 M-01 M-02
    
    ▓ Separation Quality   ▓ Platelet Yield
```

**Quality Summary Table**
```
┌──────────────┬─────────────┬──────────────┬─────────────┬────────────┐
│ Device       │ Separation  │ Platelet     │ Avg Score   │ Status     │
│              │ Quality     │ Yield        │             │            │
├──────────────┼─────────────┼──────────────┼─────────────┼────────────┤
│ Centrifuge-01│ 95%         │ 92%          │ 93.5%       │ Excellent  │
│ Centrifuge-02│ 93%         │ 90%          │ 91.5%       │ Good       │
│ Centrifuge-03│ 96%         │ 94%          │ 95.0%       │ Excellent  │
└──────────────┴─────────────┴──────────────┴─────────────┴────────────┘
```

#### C. Device Health
**Health Overview Table**
```
┌──────────────┬─────────┬────────┬──────────┬──────────────┬──────────────┐
│ Device       │ Uptime  │ Errors │ Avg Temp │ Avg Vibration│ Health Status│
├──────────────┼─────────┼────────┼──────────┼──────────────┼──────────────┤
│ Centrifuge-01│ 98.5%   │ 2      │ 23.2°C   │ 1.4 mm/s     │ Excellent    │
│ Centrifuge-02│ 99.2%   │ 1      │ 22.8°C   │ 1.2 mm/s     │ Excellent    │
│ Centrifuge-03│ 97.8%   │ 3      │ 24.1°C   │ 1.8 mm/s     │ Good         │
└──────────────┴─────────┴────────┴──────────┴──────────────┴──────────────┘
```

#### D. Capacity Planning
**Scenario Comparison**
```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Current         │  │ +10% Supply     │  │ One Device Down │  │ Optimized       │
│ Capacity        │  │ Increase        │  │                 │  │ Schedule        │
│                 │  │                 │  │                 │  │                 │
│    18.5         │  │    20.4         │  │    16.7         │  │    21.2         │
│ Units/Hour      │  │ Units/Hour      │  │ Units/Hour      │  │ Units/Hour      │
│                 │  │ Needed          │  │                 │  │                 │
│ 9 Active        │  │ Requires:       │  │ -9.7% Capacity  │  │ +14.6% vs       │
│ 85% Util        │  │ +1 Device OR    │  │ Mitigation:     │  │ Current         │
│                 │  │ +2 Staff        │  │ Extend shifts   │  │ No investment   │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘
```

### Controls
```
[Report Type: ▼ Performance] [Time Range: ▼ Last 24 Hours] [📥 Export Report]
```

---

## 4️⃣ Simulation Configuration - Path: `/config`

### Purpose
Configure "what-if" scenarios to test operational changes

### Scenario Templates
```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ 📊 Current       │  │ ⬆️ +10% Supply  │  │ 🔧 One Device    │
│ Production       │  │ Increase         │  │ Maintenance      │
└──────────────────┘  └──────────────────┘  └──────────────────┘

┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ 👥 Staff         │  │ ⚡ Peak          │  │ ✨ Custom        │
│ Shortage         │  │ Efficiency Test  │  │ Scenario (Active)│
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

### Configuration Panels

**Device Configuration**
```
Centrifuges       [3] ← → Current: 3
Macopress Units   [3] ← → Current: 3
Platelet Agitators[3] ← → Current: 3
```

**Staffing Configuration**
```
Scientists        [5] ← → Current: 5
Technicians       [8] ← → Current: 8
Shift Duration    [8] hours ← → Current: 8
```

**Supply Configuration**
```
Daily Donations   [200] ← → Current: 200
Batch Size        [4] ← → Current: 4
Supply Variance   [10]% ← → Current: 10
```

**Simulation Parameters**
```
Duration:      [24 Hours ▼]
Acceleration:  [10x Speed ▼]
Fault Injection: [None ▼]
```

### Predicted Outcomes
```
┌────────────────────────────────────────────────────────────┐
│ 📊 Predicted Outcomes                                      │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Est. Throughput           Est. Utilization               │
│      18.5 units/hr               87%                       │
│  +5.2% vs current            +3% vs current               │
│                                                            │
│  Est. Cycle Time           Est. Daily Output              │
│      14.2 min                   296 units                 │
│  +0.5 min vs current         +8.4% vs current             │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Action Buttons
```
[💾 Save Scenario] [📋 Load Scenario] [🔄 Reset to Current] [▶️ Run Simulation]
```

---

## 🎨 Visual Design

### Color Scheme (Dark Theme)
```
Background:       #1e1e1e (Dark)
Cards:            #2d2d2d (Lighter Dark)
Primary (Azure):  #0078d4 (Blue)
Success:          #107c10 (Green)
Error:            #d13438 (Red)
Warning:          #f7630c (Orange)
Idle:             #8a8886 (Gray)
Text Primary:     #ffffff (White)
Text Secondary:   #a0a0a0 (Light Gray)
```

### Status Badges
```
[Idle]        Gray background
[Processing]  Blue background, pulsing
[Error]       Red background, blinking
[Maintenance] Orange background
```

---

## 🔌 Data Integration

### Current: Mock Data
Located in `useDigitalTwins.ts` hook - simulates 9 devices with realistic data

### To Connect to Azure:

1. **Create Azure Function API**
```typescript
// backend/function_app.py - Add new function
@app.route(route="twins", methods=["GET"])
def get_twins(req: func.HttpRequest) -> func.HttpResponse:
    # Query Azure Digital Twins
    query = "SELECT * FROM DIGITALTWINS"
    twins = dt_client.query_twins(query)
    return func.HttpResponse(json.dumps(list(twins)))
```

2. **Update Frontend Hook**
```typescript
// frontend/src/hooks/useDigitalTwins.ts
const response = await fetch('/api/twins')
const data = await response.json()
setTwins(data)
```

3. **Configure Vite Proxy**
Already done in `vite.config.ts`:
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:7071',
    changeOrigin: true
  }
}
```

---

## 🚀 Running the Frontend

### Install Dependencies
```bash
cd frontend
npm install
```

### Start Development Server
```bash
npm run dev
```

Visit: **http://localhost:3000**

### Build for Production
```bash
npm run build
npm run preview
```

---

## 📁 File Structure Summary

```
frontend/
├── src/
│   ├── pages/
│   │   ├── Dashboard.tsx           # Main KPI dashboard
│   │   ├── Visualization3D.tsx     # Babylon.js 3D view
│   │   ├── Reports.tsx             # Charts & analytics
│   │   └── SimulationConfig.tsx    # Scenario configuration
│   ├── components/
│   │   ├── DeviceCard.tsx          # Device status card
│   │   ├── KPIWidget.tsx           # KPI metric display
│   │   └── ProcessFlow.tsx         # Process visualization
│   ├── hooks/
│   │   └── useDigitalTwins.ts      # Data fetching hook
│   ├── App.tsx                     # Router & navigation
│   ├── App.css                     # Global styles
│   └── main.tsx                    # Entry point
├── index.html
├── package.json
├── vite.config.ts
└── README.md
```

---

## ✅ What's Complete

- ✅ Full React application with routing
- ✅ 2D Dashboard with real-time KPIs
- ✅ 3D Visualization with Babylon.js
- ✅ Reports with multiple chart types
- ✅ Configuration interface for scenarios
- ✅ Mock data for development
- ✅ Responsive design
- ✅ Dark theme UI
- ✅ Component library (cards, widgets, etc.)

## 🔜 Next Steps

- [ ] Connect to real Azure Digital Twins API
- [ ] Implement SignalR for real-time updates
- [ ] Add user authentication
- [ ] Connect to Azure Data Explorer for historical data
- [ ] Implement scenario save/load to database
- [ ] Add export functionality (PDF/Excel reports)
- [ ] Create unit tests
- [ ] Deploy to Azure Static Web Apps

---

## 🎯 User Experience Flow

**Lab Operations Manager Daily Workflow:**

1. **Opens Dashboard** (`/`)
   - Sees 3 devices processing, 5 idle, 1 error
   - Checks KPIs: 85% utilization, 18.5 units/hr
   
2. **Clicks on error device**
   - Sees "Excessive vibration detected"
   - Notes device ID for maintenance team

3. **Switches to 3D View** (`/3d`)
   - Visually confirms device locations
   - Sees red blinking centrifuge-03
   - Checks surrounding devices are operational

4. **Opens Reports** (`/reports`)
   - Reviews last 24 hours performance
   - Exports report for shift handover

5. **Tests "What-If"** (`/config`)
   - Simulates one device down
   - Sees 9.7% capacity reduction
   - Plans mitigation: extend shifts 1 hour

**Result:** Data-driven decision made in 5 minutes vs. hours of manual analysis!
