# POC Requirements - Based on Client Presentation

## Target Objectives (From Presentation)

### 1. Optimization of Staff Allocation
**Goal**: Determine optimal number of technicians/scientists for efficient processing.

**Implementation Needed**:
- [ ] Staff simulator with labor hours tracking
- [ ] UI controls to adjust staff count (sliders)
- [ ] Calculate: process time with different staff levels
- [ ] Visualize: staff utilization %, idle time
- [ ] Compare: scenarios with 2, 3, 4, 5 technicians

**Calculation**:
```
Total Process Time = Sum(device_processing_times) / staff_efficiency_factor
Staff Utilization % = (active_time / (total_time * staff_count)) * 100
```

---

### 2. Optimization of Device Utilization
**Goal**: Find optimal number of devices to maximize throughput without over-investing.

**Implementation Needed**:
- [x] Device simulators (DONE)
- [ ] UI controls to adjust device count
- [ ] Calculate: throughput with different device configurations
- [ ] Identify: bottleneck devices (highest utilization %)
- [ ] Suggest: which devices to add/remove

**Calculation**:
```
Device Utilization % = (processing_time / total_time) * 100
Throughput = batches_completed / time_period
Bottleneck = device with highest utilization %
```

---

### 3. Supply Variation Analysis
**Goal**: Understand impact of platelet supply fluctuations on process efficiency.

**Implementation Needed**:
- [ ] UI controls to adjust input supply (platelets per day)
- [ ] Calculate: how supply affects downstream devices
- [ ] Visualize: device wait times, queue lengths
- [ ] Identify: dependencies between machines

**Calculation**:
```
Queue Time = arrival_rate > processing_rate ? (arrival - processing) : 0
Dependency Impact = upstream_delay * downstream_dependency_factor
```

---

### 4. Process Order Adjustment
**Goal**: Suggest process flow changes to improve efficiency.

**Implementation Needed**:
- [ ] Process orchestrator to model flow
- [ ] UI to reorder process steps
- [ ] Calculate: total time with different orderings
- [ ] Suggest: optimal process sequence

**Note**: POC does NOT auto-optimize (no ML/AI), just manual comparison.

---

### 5. Product Release Measurement
**Goal**: Measure how many products are released in a given timeframe.

**Implementation Needed**:
- [x] Track batch completion (DONE)
- [ ] Aggregate by time window (daily, weekly, monthly)
- [ ] Dashboard widget showing: "Products Released Today"
- [ ] Trend chart: releases over time

**Calculation**:
```
Products Released = count(batches where status='complete' AND completion_time in window)
Average per Day = total_products / days_in_period
```

---

### 6. Constraint Modeling
**Goal**: Model real-world limitations (floor space, max devices, budget).

**Implementation Needed**:
- [ ] Constraint configuration UI
  - Max devices per type
  - Floor space per device
  - Total floor space available
  - Budget per device
  - Total budget
- [ ] Validation logic
- [ ] Visual warnings when constraints exceeded

**Constraints**:
```python
constraints = {
    "max_floor_space_sqft": 500,
    "max_devices_total": 20,
    "max_budget": 500000,
    "device_costs": {
        "centrifuge": 50000,
        "pooling_station": 30000,
        # ... etc
    },
    "device_footprints": {
        "centrifuge": 25,  # sqft
        "pooling_station": 15,
        # ... etc
    }
}
```

---

### 7. Outcome Forecasting
**Goal**: Forecast outcomes based on changes to devices, staff, or process.

**Implementation Needed**:
- [ ] Scenario engine to store configurations
- [ ] Run simulation with different parameters
- [ ] Calculate outcomes:
  - Total process time
  - Throughput (units/day)
  - Staff utilization %
  - Device utilization %
  - Cost per unit
  - Products per day
- [ ] Compare: Baseline vs Modified scenario

**Scenarios to Support**:
- Add 2nd centrifuge: how does throughput change?
- Add 1 more technician: how does process time change?
- Increase supply by 20%: what happens to bottlenecks?

---

### 8. Productivity and Capacity Forecasting
**Goal**: Plan for capacity changes (e.g., 10% donation increase from marketing campaign).

**Implementation Needed**:
- [ ] "What-if" scenario builder
- [ ] Input: expected supply increase %
- [ ] Calculate: required capacity adjustments
  - How many more devices?
  - How many more staff?
  - What's the new throughput?
- [ ] Visualize: before/after comparison

**Example Scenario**:
```
Current State:
- Supply: 100 donations/day
- Throughput: 25 pooled products/day
- Staff: 3 technicians
- Devices: 1 of each

Marketing campaign increases donations by 10%:
- New supply: 110 donations/day
- Can current capacity handle it?
  - If NO: recommend adding X devices, Y staff
  - If YES: show new utilization %
```

---

## POC Assumptions (From Presentation)

### Manual Adjustments (Not AI)
> "The process and device simulators will allow for manual adjustments to the number of technicians and machines, as well as the delays and processing times at each stage."

**Implementation**:
- Sliders/inputs for all adjustable parameters
- No automated optimization
- User manually tries different configurations
- System calculates and displays results

### Device Errors and Maintenance
> "The simulators will also support simulating device errors and maintenance situations."

**Implementation**:
- [x] Fault injection in simulators (DONE)
- [ ] UI to trigger device failures
- [ ] Show impact on throughput when device down
- [ ] Calculate: cost of downtime

### Manual Digital Twins Updates
> "Additional devices must be manually added to the Digital Twins graph and 3D model."

**Implementation**:
- Not auto-scaling
- Admin UI to add/remove devices
- Update twin graph
- Update 3D scene

### No Advanced Analytics
> "Note that this POC does not include machine learning, AI, or advanced analytics for automated analysis of the Digital Twins data."

**Implementation**:
- Simple calculations only
- Manual scenario comparison
- No predictive ML models
- No auto-optimization algorithms

---

## Deliverables Checklist

### POC Development Phase

- [ ] **3D visualization with visual indicators**
  - [x] 3D scene (we have Babylon.js)
  - [ ] Device status indicators (red/green/yellow dots on 3D models)
  - [ ] Real-time updates from Digital Twins

- [ ] **Digital Twin Graph development**
  - [ ] Complete DTDL models (1/12 done)
  - [ ] Create twin instances in Azure
  - [ ] Define relationships between twins

- [x] **Device simulator development** ✅ DONE
  - [x] 12 device simulators
  - [x] Realistic telemetry
  - [x] Fault injection

- [ ] **Azure IoT Hub POC deployment**
  - [ ] Deploy Bicep infrastructure
  - [ ] Create device identities
  - [ ] Connect simulators to IoT Hub

- [x] **NBMS data feed simulator** ✅ DONE
  - [x] Batch tracking
  - [x] Product records
  - [x] Quality tests
  - [x] Inventory

- [ ] **POC web app development**
  - [x] Dashboard UI (we have this)
  - [x] 3D visualization (we have this)
  - [ ] **MISSING: Scenario configuration UI**
  - [ ] **MISSING: Parameter adjustment controls**
  - [ ] **MISSING: Scenario comparison view**
  - [ ] **MISSING: Constraint modeling UI**

---

## Priority Implementation Plan

### Phase 1: Scenario Modeling Engine (HIGHEST PRIORITY)
Build the core "what-if" capability:
1. Scenario manager (save/load scenarios)
2. Parameter adjustment engine
3. Outcome calculator
4. Comparison view

### Phase 2: Staff & Constraint Modeling
Add missing business logic:
1. Staff simulator
2. Constraint validation
3. Floor space calculations
4. Budget tracking

### Phase 3: UI Enhancements
Make it usable for manual scenario testing:
1. Parameter sliders/inputs
2. Scenario comparison dashboard
3. Constraint warnings
4. Forecasting results display

### Phase 4: Azure Deployment
Deploy everything to Azure:
1. Complete DTDL models
2. IoT Hub setup
3. Digital Twins deployment
4. Logic Apps for NBMS
5. 3D Scenes Studio integration
