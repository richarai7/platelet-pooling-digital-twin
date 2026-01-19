# Platelet Pooling Digital Twin - Copilot Instructions

## Project Context
This is an Azure-based digital twin simulation platform for platelet pooling lab processes. The system includes 12 device simulators, Azure IoT Hub integration, Azure Digital Twins, and real-time 3D visualization.

## Architecture Overview
- **Simulators**: 12 Python-based device simulators sending telemetry to Azure IoT Hub
- **Infrastructure**: Azure IoT Hub, Digital Twins, Functions, Data Explorer, Redis
- **Backend**: Python Azure Functions for event processing and API endpoints
- **Frontend**: React dashboard with 2D KPIs and 3D visualization
- **Data Storage**: Azure Digital Twins (live state), Azure Data Explorer (historical data)

## Development Guidelines

### Code Style
- Python: Follow PEP 8, use type hints, docstrings for all functions
- TypeScript/React: Use functional components, hooks, strict TypeScript
- Bicep: Use modules, parameterize all resources, include comments

### Naming Conventions
- Device simulators: lowercase with underscores (e.g., `centrifuge_simulator.py`)
- Azure Functions: lowercase with underscores (e.g., `process_telemetry`)
- React components: PascalCase (e.g., `DeviceDashboard.tsx`)
- Bicep files: lowercase with hyphens (e.g., `iot-hub.bicep`)

### File Organization
- Keep simulator logic separate from IoT communication
- Each device simulator should be independently testable
- Frontend components should be reusable
- Infrastructure modules should be composable

### Testing Requirements
- Unit tests for all simulator logic
- Integration tests for IoT Hub message flow
- Frontend component tests using React Testing Library
- Mock Azure services for local testing

### Security Best Practices
- Never commit connection strings or secrets
- Use Azure Key Vault references in configuration
- Implement least-privilege access for all Azure resources
- Validate all user inputs in API endpoints

### Performance Considerations
- Simulators should support configurable telemetry intervals
- Digital Twin updates should be batched when possible
- Frontend should use WebSocket connections for real-time updates
- Implement caching for frequently accessed data

## Common Tasks

### Adding a New Device Simulator
1. Create new Python module in `simulators/devices/`
2. Implement base simulator interface
3. Define telemetry schema in `data/schemas/`
4. Add corresponding DTDL model
5. Create unit tests
6. Update configuration examples

### Modifying Azure Infrastructure
1. Update Bicep modules in `infra/bicep/`
2. Update parameter files
3. Run bicep lint
4. Test deployment in dev environment
5. Update documentation

### Adding Frontend Features
1. Create component in appropriate folder
2. Add TypeScript interfaces for data
3. Implement component tests
4. Update routing if needed
5. Document props and usage
