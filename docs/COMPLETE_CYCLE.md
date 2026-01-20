# Platelet Pooling Digital Twin - Complete End-to-End Cycle

This document explains the complete data flow for a single device simulator (Centrifuge) through the entire Azure platform.

## 🔄 Complete Cycle Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    FULL END-TO-END CYCLE                        │
└─────────────────────────────────────────────────────────────────┘

1. SIMULATOR                    [Local/Container]
   └─ centrifuge_simulator.py   
      └─ Generates telemetry every 5 seconds
      └─ Simulates processing cycles
      └─ Models device physics (RPM, temp, vibration)

2. IOT CONNECTOR               [Local/Container]
   └─ iot_connector.py
      └─ Sends telemetry → Azure IoT Hub
      └─ Sends events (start, complete, error)

3. AZURE IOT HUB               [Azure Cloud]
   └─ Receives messages from devices
   └─ Routes to Event Hub endpoint
   └─ Device registry & authentication

4. EVENT HUB TRIGGER           [Azure Cloud]
   └─ Triggers Azure Function
   └─ Batches messages for processing

5. AZURE FUNCTION              [Azure Cloud]
   └─ function_app.py::process_telemetry()
      └─ Parses telemetry/events
      └─ Updates Digital Twin properties
      └─ Publishes telemetry events

6. AZURE DIGITAL TWINS         [Azure Cloud]
   └─ Maintains live state graph
   └─ Stores device properties (DTDL model)
   └─ Relationships between devices
   └─ Queries for frontend

7. FRONTEND DASHBOARD          [Browser]
   └─ Reads from Digital Twins API
   └─ Displays KPIs & 3D visualization
   └─ Real-time updates via SignalR
```

## 📋 Step-by-Step Cycle Example

### Phase 1: Initialization (0s)
```python
# Simulator starts
centrifuge = CentrifugeSimulator("centrifuge-01")
centrifuge.start()
→ State: "idle", RPM: 0, Temp: 22°C

# Connects to IoT Hub
iot = IoTConnector(connection_string, "centrifuge-01")
await iot.connect()
→ Device authenticated with IoT Hub

# Sends initial telemetry
telemetry = centrifuge.generate_telemetry()
await iot.send_telemetry(telemetry)
```

**Data sent to IoT Hub:**
```json
{
  "device_id": "centrifuge-01",
  "device_type": "centrifuge",
  "timestamp": "2026-01-20T10:00:00Z",
  "state": "idle",
  "is_processing": false,
  "rpm": 0,
  "temperature_celsius": 22.0,
  "vibration_mm_s": 0.1
}
```

**Azure Function receives:**
- Triggered by Event Hub
- Calls `update_twin_telemetry()`
- Updates Digital Twin properties

**Digital Twin updated:**
```json
{
  "$dtId": "centrifuge-01",
  "state": "idle",
  "isProcessing": false,
  "rpm": 0,
  "temperature": 22.0,
  "vibration": 0.1,
  "lastTelemetryTime": "2026-01-20T10:00:00Z"
}
```

---

### Phase 2: Processing Start (5s)
```python
# Start processing batch
centrifuge.start_processing("BATCH-20260120-001")
→ State: "processing", Remaining: 900s (15 min)

# Send event
await iot.send_event("processing_started", {
  "batch_id": "BATCH-20260120-001",
  "estimated_completion_seconds": 900
})
```

**Event sent to IoT Hub:**
```json
{
  "event_type": "processing_started",
  "device_id": "centrifuge-01",
  "batch_id": "BATCH-20260120-001",
  "timestamp": "2026-01-20T10:00:05Z"
}
```

**Azure Function handles event:**
- Calls `handle_device_event()`
- Publishes telemetry event to Digital Twin
- Event available for Time Series Insights / ADX

---

### Phase 3: Active Processing (10s - 900s)
```python
# Every 5 seconds during processing
while processing:
    telemetry = centrifuge.generate_telemetry()
    await iot.send_telemetry(telemetry)
    await asyncio.sleep(5)
```

**Telemetry during processing (example at 30s):**
```json
{
  "device_id": "centrifuge-01",
  "state": "processing",
  "is_processing": true,
  "current_batch_id": "BATCH-20260120-001",
  "rpm": 2987.3,              // Fluctuates around 3000
  "temperature_celsius": 24.7, // Rising due to friction
  "vibration_mm_s": 1.42,     // Increased during spin
  "remaining_time_seconds": 870,
  "cycles_completed": 12
}
```

**Azure Function updates Digital Twin every 5s:**
- Twin properties continuously updated
- Frontend sees near real-time state changes
- Historical data streamed to Azure Data Explorer

---

### Phase 4: Processing Complete (905s)
```python
# Processing finished
result = centrifuge.complete_processing()
→ State: "idle", Cycles: 13

# Send completion event
await iot.send_event("processing_complete", result)
```

**Completion event:**
```json
{
  "event_type": "processing_complete",
  "device_id": "centrifuge-01",
  "batch_id": "BATCH-20260120-001",
  "cycle_time_minutes": 15,
  "quality_metrics": {
    "separation_quality": 0.95,
    "platelet_yield": 0.92
  },
  "timestamp": "2026-01-20T10:15:05Z"
}
```

**Azure Function:**
- Publishes completion telemetry to Digital Twin
- Quality metrics available for analysis
- Batch can move to next device in process

---

### Phase 5: Return to Idle (910s)
```python
# Send final telemetry
telemetry = centrifuge.generate_telemetry()
await iot.send_telemetry(telemetry)
→ State: "idle", RPM: 0 (spun down)
```

**Digital Twin final state:**
```json
{
  "$dtId": "centrifuge-01",
  "state": "idle",
  "isProcessing": false,
  "currentBatchId": "",
  "rpm": 0,
  "temperature": 22.5,
  "vibration": 0.2,
  "cyclesCompleted": 13,
  "lastTelemetryTime": "2026-01-20T10:15:10Z"
}
```

---

## 🔧 Error Handling Example

### Fault Scenario (Excessive Vibration)
```python
# During processing, fault occurs
centrifuge.simulate_fault("vibration")
→ State: "error", Error: "Excessive vibration detected"

# Send error telemetry
telemetry = centrifuge.generate_telemetry()
await iot.send_telemetry(telemetry)

# Send error event
await iot.send_event("device_error", {
  "error_state": "Excessive vibration detected"
})
```

**Digital Twin in error state:**
```json
{
  "state": "error",
  "isProcessing": false,
  "errorState": "Excessive vibration detected",
  "rpm": 0
}
```

**Recovery:**
```python
# Operator clears error
centrifuge.clear_error()
await iot.send_event("error_cleared", {})
→ State: "idle"
```

---

## 📊 Data Destinations

### 1. Azure Digital Twins (Live State)
- **Purpose:** Current state of all devices
- **Queries:** "Show me all idle centrifuges"
- **Used by:** Frontend dashboard, 3D visualization

### 2. Azure Data Explorer (Historical)
- **Purpose:** Time-series analysis, trends
- **Queries:** "Average RPM over last week"
- **Used by:** Analytics, ML models, reports

### 3. Frontend Dashboard
- **Reads from:** Digital Twins API
- **Displays:** Real-time KPIs, device status, process flow
- **Updates:** WebSocket/SignalR for live updates

---

## 🚀 Running the Complete Cycle

### Prerequisites
```bash
# 1. Install dependencies
cd simulators
pip install -r requirements.txt

cd ../backend
pip install -r requirements.txt

# 2. Configure Azure resources (run once)
cd ../infra/bicep
az deployment sub create --location eastus --template-file main.bicep

# 3. Get connection strings from Azure Portal
# - IoT Hub device connection string
# - Event Hub connection string  
# - Digital Twins URL

# 4. Create .env file
cp .env.example .env
# Edit .env with your connection strings
```

### Run Simulator
```bash
cd simulators
python run_simulator.py
```

### Deploy Azure Function
```bash
cd backend
func azure functionapp publish <your-function-app-name>
```

### View Results
- **Azure Portal:** See Digital Twins graph
- **IoT Hub:** Monitor messages
- **Application Insights:** View function logs
- **Dashboard:** (Coming next phase)

---

## 🎯 Key Takeaways

1. **Decoupled Architecture:** Simulator doesn't know about Digital Twins
2. **Event-Driven:** Everything triggered by messages
3. **Scalable:** Can add 100 devices without code changes
4. **Testable:** Each component independently testable
5. **Real-time:** Sub-second latency from device to twin
6. **Observable:** Full logging and monitoring

---

## 📝 Next Steps

1. ✅ Complete one device cycle (this document)
2. ⏭️ Build remaining 11 device simulators
3. ⏭️ Create process orchestrator (batch flow between devices)
4. ⏭️ Build frontend dashboard
5. ⏭️ Add 3D visualization
6. ⏭️ Implement "what-if" scenario configuration
