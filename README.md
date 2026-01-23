# Platelet Pooling Digital Twin

A comprehensive digital twin simulation platform for optimizing platelet pooling lab processes. This system simulates 12 interconnected lab devices to enable data-driven operational decisions, capacity planning, and process optimization.

## Overview

This project provides **two complementary approaches** to simulating the platelet pooling process:

1. **SimPy Discrete-Event Simulation** (for process analysis and optimization)
2. **Azure Cloud Digital Twin** (for real-time monitoring and integration)

### Key Features

- **12 Device Simulators**: Complete workflow simulation from centrifuge to final release
- **SimPy-based Process Simulation**: Fast discrete-event simulation for capacity planning and bottleneck analysis
- **Real-time Visualization**: Interactive 2D dashboard and 3D lab environment view
- **Scenario Modeling**: Configure device counts, staff levels, and process parameters
- **Predictive Analytics**: Forecast capacity, throughput, and resource utilization
- **Azure Integration**: IoT Hub, Digital Twins, Data Explorer, and Functions

## Problem Being Solved

Lab operations currently lack a holistic, real-time view of the platelet pooling workflow. This platform enables:

- Testing operational changes without disrupting the real lab
- Identifying bottlenecks and inefficiencies in process flow
- Forecasting capacity and productivity for demand changes
- Optimizing staff allocation and device utilization

## Architecture

### SimPy Discrete-Event Simulation (Local)
```
Batch Generator → 12 SimPy Device Simulators → Metrics & Analysis
   (Process-based discrete-event simulation)
   - Fast execution (simulated time)
   - Queue modeling
   - Resource contention
   - Statistical analysis
```

### Azure Cloud Digital Twin (Production)
```
Device Simulators (Python)
        ↓
   Azure IoT Hub
        ↓
  Azure Functions (Event Processors)
        ↓
  Azure Digital Twins
        ↓
   ┌────────┴────────┐
   ↓                 ↓
Frontend (React)  Azure Data Explorer
                  (Historical Data)
```

## Project Structure

```
platelet-pooling-digital-twin/
├── simulators/          # Device simulators
│   ├── simpy_core/      # SimPy base classes
│   ├── simpy_devices/   # 12 SimPy device simulators
│   ├── devices/         # Azure IoT device implementations
│   ├── core/            # Shared simulator logic
│   └── tests/           # Simulator tests
├── infra/               # Azure infrastructure
│   └── bicep/           # Bicep IaC templates
├── functions/           # Azure Functions
│   ├── telemetry/       # IoT Hub processors
│   ├── api/             # REST API endpoints
│   └── tests/           # Function tests
├── frontend/            # React dashboard
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API clients
│   │   └── views/       # Dashboard & 3D views
│   └── public/          # Static assets
├── data/                # Schemas and test data
│   ├── schemas/         # Telemetry schemas
│   ├── dtdl/            # Digital Twin models
│   └── samples/         # Sample data
└── docs/                # Documentation
    ├── architecture.md  # System architecture
    ├── setup.md         # Setup instructions
    └── user-guide.md    # User documentation
```

## Quick Start

### SimPy Simulation (Recommended for Analysis)

**Fast, local simulation for capacity planning and optimization**

1. **Install dependencies**
   ```bash
   cd simulators
   pip install -r requirements.txt
   ```

2. **Run interactive demo**
   ```bash
   python simpy_demo.py
   ```
   
   Or run specific scenarios:
   ```bash
   python simpy_demo.py basic        # Basic 1-hour simulation
   python simpy_demo.py stress       # High-volume stress test
   python simpy_demo.py capacity     # Compare device configurations
   ```

3. **Analyze results**
   - View device utilization
   - Identify bottlenecks
   - Test "what-if" scenarios
   - No Azure account required!

📖 **See [GETTING_STARTED_SIMPY.md](simulators/GETTING_STARTED_SIMPY.md) for detailed guide**

### Azure Deployment (For Production Monitoring)

### Prerequisites

- Python 3.11+
- Node.js 18+
- Azure CLI
- Azure subscription with appropriate permissions

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd platelet-pooling-digital-twin
   ```

2. **Setup Python environment**
   ```bash
   cd simulators
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Configure Azure connection**
   - Copy `simulators\.env.example` to `simulators\.env`
   - Add your Azure IoT Hub connection string
   - Copy `functions\local.settings.example.json` to `functions\local.settings.json`

5. **Run simulators locally**
   ```bash
   cd simulators
   python -m core.runner
   ```

6. **Run frontend**
   ```bash
   cd frontend
   npm run dev
   ```

### Azure Deployment

1. **Deploy infrastructure**
   ```powershell
   cd infra\bicep
   az deployment sub create `
     --location eastus `
     --template-file main.bicep `
     --parameters main.parameters.json
   ```

2. **Deploy Azure Functions**
   ```powershell
   cd functions
   func azure functionapp publish <function-app-name>
   ```

3. **Deploy frontend** (instructions TBD based on hosting choice)

## Usage

### Running a Simulation

1. Access the dashboard at `http://localhost:3000`
2. Configure scenario parameters:
   - Number of devices per type
   - Staff allocation
   - Supply input rate
3. Click "Start Simulation"
4. Monitor KPIs and 3D visualization in real-time

### Key Performance Indicators

- **Throughput**: Products released per hour
- **Cycle Time**: Average end-to-end processing time
- **Device Utilization**: % time devices are active
- **Staff Utilization**: % time staff are engaged
- **Queue Times**: Wait time between process steps

## Development

### Running Tests

```powershell
# Python tests
cd simulators
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```powershell
# Python linting
cd simulators
flake8
mypy .

# Frontend linting
cd frontend
npm run lint
```

## Documentation

- [Architecture Overview](docs/architecture.md)
- [Setup Guide](docs/setup.md)
- [User Guide](docs/user-guide.md)
- [API Reference](docs/api-reference.md)
- [Device Specifications](docs/device-specs.md)

## Contributing

1. Create a feature branch
2. Make your changes with tests
3. Ensure all tests pass
4. Submit a pull request

## License

[To be determined]

## Support

For questions or issues, please create a GitHub issue or contact the BMAD AI agent team.
