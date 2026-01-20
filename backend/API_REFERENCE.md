# Platelet Pooling Digital Twin - API Reference

**Base URL**: `http://localhost:5000`

## Status: ✅ Running

---

## Quick Start

```bash
# Health check
curl http://localhost:5000/api/health

# Get baseline scenario
curl http://localhost:5000/api/baseline

# Get all scenarios
curl http://localhost:5000/api/scenarios
```

---

## Endpoints

### 🏠 Root
- **GET** `/`
- Returns API information and available endpoints

**Example Response**:
```json
{
  "name": "Platelet Pooling Digital Twin API",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {
    "scenarios": "/api/scenarios",
    "baseline": "/api/baseline",
    "staff": "/api/staff/summary",
    "health": "/api/health"
  }
}
```

---

### 💚 Health Check
- **GET** `/api/health`
- Check API server status

**Example Response**:
```json
{
  "status": "healthy",
  "scenarios_count": 1,
  "staff_count": 3
}
```

---

### 📊 Scenarios

#### List All Scenarios
- **GET** `/api/scenarios`
- Returns array of all scenarios

#### Create Scenario
- **POST** `/api/scenarios`
- Create a new scenario configuration

**Request Body**:
```json
{
  "name": "Increased Capacity",
  "description": "Add second centrifuge",
  "devices": [
    {
      "device_type": "centrifuge",
      "count": 2,
      "processing_time_minutes": 15,
      "cost_per_unit": 50000,
      "floor_space_sqft": 25,
      "failure_rate": 0.01
    }
  ],
  "staff": {
    "technician_count": 4,
    "shift_hours": 8,
    "avg_hourly_rate": 45
  },
  "supply": {
    "donations_per_day": 100,
    "avg_buffy_coats_per_donation": 1,
    "pooling_ratio": 5
  },
  "constraints": {
    "max_floor_space_sqft": 500,
    "max_total_budget": 500000,
    "max_staff": 10,
    "max_devices_total": 20
  }
}
```

**Response**:
```json
{
  "id": "uuid-here",
  "name": "Increased Capacity",
  "created_at": "2026-01-20T06:10:46.215658"
}
```

#### Get Scenario
- **GET** `/api/scenarios/<scenario_id>`
- Retrieve specific scenario details

#### Calculate Scenario Outcome
- **POST** `/api/scenarios/<scenario_id>/calculate`
- Run calculations and return predicted outcomes

**Example Response**:
```json
{
  "scenario_id": "uuid",
  "scenario_name": "Increased Capacity",
  "throughput_products_per_day": 25.5,
  "total_process_time_minutes": 60.2,
  "staff_utilization_percent": 85.3,
  "device_utilization": {
    "centrifuge": 45.2,
    "pooling_station": 67.8
  },
  "cost_per_product": 68.50,
  "bottleneck_device": "pooling_station",
  "is_feasible": true,
  "constraints_violated": []
}
```

#### Delete Scenario
- **DELETE** `/api/scenarios/<scenario_id>`
- Remove a scenario

#### Compare Scenarios
- **POST** `/api/scenarios/compare`
- Side-by-side comparison of multiple scenarios

**Request Body**:
```json
{
  "scenario_ids": ["baseline-id", "scenario-1-id", "scenario-2-id"]
}
```

**Response**:
```json
{
  "scenarios": [
    {
      "id": "baseline-id",
      "name": "Baseline",
      "throughput": 21.7,
      "cost": 72.04
    },
    {
      "id": "scenario-1-id",
      "name": "Added Centrifuge",
      "throughput": 21.7,
      "throughput_improvement": "0.0%",
      "cost": 78.34,
      "cost_change": "+8.7%"
    }
  ]
}
```

---

### 👥 Staff Management

#### Staff Summary
- **GET** `/api/staff/summary`
- Current staff allocation and utilization

**Example Response**:
```json
{
  "total_technicians": 3,
  "avg_utilization": 65.4,
  "total_daily_cost": 840.00,
  "technicians": [
    {
      "id": "tech-1",
      "skill_level": 1.0,
      "hourly_rate": 50,
      "current_utilization": 72.3
    }
  ]
}
```

#### Optimize Staffing
- **POST** `/api/staff/optimize`
- Get staffing recommendations for target throughput

**Request Body**:
```json
{
  "target_throughput": 25,
  "avg_process_time_minutes": 60
}
```

**Response**:
```json
{
  "recommended_staff": 4,
  "current_staff": 3,
  "estimated_utilization": 75.0,
  "estimated_cost_per_day": 1440.00
}
```

---

### 📈 Baseline Scenario
- **GET** `/api/baseline`
- Get default baseline scenario and calculated outcomes

**Example Response**:
```json
{
  "scenario": {
    "id": "baseline-id",
    "name": "Baseline",
    "description": "Current production configuration",
    "devices": [...],
    "staff": {...},
    "supply": {...}
  },
  "outcome": {
    "throughput_products_per_day": 21.74,
    "total_process_time_minutes": 66.24,
    "cost_per_product": 72.04,
    "bottleneck_device": "centrifuge",
    "is_feasible": true
  }
}
```

---

## Testing with curl

```bash
# Test all endpoints
curl http://localhost:5000/
curl http://localhost:5000/api/health
curl http://localhost:5000/api/baseline
curl http://localhost:5000/api/scenarios
curl http://localhost:5000/api/staff/summary

# Create a scenario
curl -X POST http://localhost:5000/api/scenarios \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Scenario",
    "description": "Testing API",
    "devices": [...],
    "staff": {...},
    "supply": {...}
  }'

# Calculate scenario outcome
curl -X POST http://localhost:5000/api/scenarios/<scenario-id>/calculate

# Compare scenarios
curl -X POST http://localhost:5000/api/scenarios/compare \
  -H "Content-Type: application/json" \
  -d '{"scenario_ids": ["id1", "id2"]}'
```

---

## Error Responses

All errors return appropriate HTTP status codes with JSON error messages:

```json
{
  "error": "Description of what went wrong"
}
```

**Common Status Codes**:
- `200` - Success
- `201` - Created
- `400` - Bad Request (invalid data)
- `404` - Not Found
- `500` - Server Error

---

## CORS

CORS is enabled for all origins to support frontend development.

---

## Notes

- This is a development server. Do not use in production.
- The server runs on port `5000` by default.
- All POST/PUT requests require `Content-Type: application/json` header.
- Scenario calculations use the platelet pooling process model with 12 device stages.
