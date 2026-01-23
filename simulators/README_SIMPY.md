# SimPy-based Platelet Pooling Simulators

## Overview

This directory contains a complete discrete-event simulation implementation of the platelet pooling process using **SimPy**, a Python library for process-based discrete-event simulation.

## What is SimPy?

SimPy is a process-based discrete-event simulation framework that allows you to model complex systems with:
- **Resources**: Devices with limited capacity that processes compete for
- **Processes**: Sequences of events that unfold over simulated time
- **Queues**: Automatic queue management when resources are busy
- **Events**: Time-based and condition-based event scheduling

This makes it ideal for modeling lab processes with multiple devices, queuing, and resource constraints.

## Architecture

### Core Components

1. **SimPy Base Classes** (`simpy_core/`)
   - `simpy_base.py`: Base simulator class with resource management, telemetry, and failure modeling
   - `BatchItem`: Data class representing a platelet batch flowing through the system

2. **Device Simulators** (`simpy_devices/`)
   - 12 device simulators, one for each step in the platelet pooling process
   - Each inherits from `SimPyDeviceSimulator` base class
   - Implements device-specific processing logic and telemetry

3. **Simulation Environment** (`platelet_pooling_simulation.py`)
   - Orchestrates the complete workflow
   - Manages batch arrival and routing
   - Collects metrics and generates reports

## The 12 Device Simulators

| Device | Purpose | Default Process Time | Capacity |
|--------|---------|---------------------|----------|
| **Blood Bag Scanner** | Barcode scanning and tracking | 5s | 1 |
| **Centrifuge** | Blood component separation | 180s (3 min) | 4 |
| **Plasma Extractor** | Plasma removal | 90s | 2 |
| **Macopress** | Platelet expression | 120s (2 min) | 1 |
| **Platelet Agitator** | Continuous agitation | 3600s (1 hour) | 8 |
| **Sterile Connector** | Bag connection | 45s | 1 |
| **Pooling Station** | Multi-unit pooling | 300s (5 min) | 1 |
| **Quality Control** | Automated testing | 240s (4 min) | 2 |
| **Labeling Station** | Product labeling | 60s (1 min) | 1 |
| **Storage Refrigerator** | Temperature-controlled storage | 7200s (2 hours) | 20 |
| **Barcode Reader** | Final verification | 8s | 1 |
| **Shipping Prep** | Packaging and documentation | 180s (3 min) | 2 |

## Installation

### Prerequisites

```bash
# Python 3.11 or higher
python --version

# Install required packages
cd simulators
pip install -r requirements.txt
```

The `requirements.txt` includes:
- `simpy==4.1.1` - Discrete-event simulation framework
- Other dependencies (azure-iot-device, etc.)

## Quick Start

### Running the Demo

```bash
# Interactive menu
cd simulators
python simpy_demo.py

# Or run specific simulations directly
python simpy_demo.py basic        # Basic 1-hour simulation
python simpy_demo.py stress       # High-volume stress test
python simpy_demo.py reliability  # With device failures
python simpy_demo.py capacity     # Compare scenarios
```

### Basic Usage in Code

```python
from platelet_pooling_simulation import PlateletPoolingSimulation, SimulationConfig

# Create configuration
config = SimulationConfig(
    simulation_duration=3600.0,  # 1 hour in seconds
    batch_arrival_rate=300.0,    # New batch every 5 minutes
    num_centrifuges=2,           # Use 2 centrifuges
    enable_failures=False        # No random failures
)

# Run simulation
sim = PlateletPoolingSimulation(config)
sim.run()

# Get detailed metrics
metrics = sim.get_all_metrics()
print(metrics)
```

## Key Features

### 1. Resource Management
Each device is modeled as a SimPy Resource with configurable capacity:
```python
# Centrifuge can process 4 bags simultaneously
centrifuge = Centrifuge(env, capacity=4)

# Storage refrigerator can hold 20 products
fridge = StorageRefrigerator(env, capacity=20)
```

### 2. Automatic Queue Management
SimPy automatically manages queues when devices are busy:
- Batches wait in queue when device is at capacity
- FIFO (First-In-First-Out) queue discipline
- Queue length tracked in telemetry

### 3. Realistic Process Times
Process times have variation to model real-world uncertainty:
```python
# Normal distribution around mean time
process_time = random.normalvariate(mean_time, std_dev)
```

### 4. Device Failures and Repairs (Optional)
Enable random failures to test resilience:
```python
config = SimulationConfig(
    enable_failures=True,
    mtbf=7200.0,  # Mean Time Between Failures (2 hours)
    mttr=600.0    # Mean Time To Repair (10 minutes)
)
```

### 5. Comprehensive Telemetry
Each device generates detailed telemetry:
```python
telemetry = device.generate_telemetry()
# Returns:
# - state (idle/processing/error)
# - utilization percentage
# - queue length
# - total processed count
# - device-specific metrics (RPM, temperature, etc.)
```

### 6. Batch Tracking
Every batch maintains a complete process history:
```python
batch = BatchItem(batch_id="BATCH-00001", arrival_time=env.now)
# After processing, batch contains:
# - process_history: List of all processing steps
# - quality_metrics: Cumulative quality data
# - total cycle time
```

## Simulation Scenarios

### Scenario 1: Baseline Analysis
Understand current process performance:
```python
config = SimulationConfig(
    simulation_duration=28800.0,  # 8-hour shift
    batch_arrival_rate=300.0       # Batch every 5 minutes
)
sim = PlateletPoolingSimulation(config)
sim.run()
```

### Scenario 2: Capacity Planning
Test impact of adding devices:
```python
# Current setup
baseline_config = SimulationConfig(num_centrifuges=1)

# Proposed setup
proposed_config = SimulationConfig(num_centrifuges=2)

# Run both and compare metrics
```

### Scenario 3: Bottleneck Analysis
Identify which devices limit throughput:
```python
sim.run()
metrics = sim.get_all_metrics()

# Check utilization - devices at 100% are bottlenecks
for device_type, devices in metrics['devices'].items():
    for device in devices:
        if device['utilization'] > 0.90:
            print(f"Bottleneck: {device['device_id']}")
```

### Scenario 4: Reliability Testing
Understand impact of device failures:
```python
config = SimulationConfig(
    enable_failures=True,
    mtbf=14400.0,  # Failures every 4 hours average
    mttr=1800.0    # 30 min repair time
)
```

## Metrics and Analysis

### Simulation-Level Metrics
- **Throughput**: Batches completed per hour
- **Cycle Time**: Average time from arrival to completion
- **Completion Rate**: Percentage of batches successfully completed
- **Queue Times**: Time batches spend waiting

### Device-Level Metrics
- **Utilization**: Percentage of time device is processing
- **Processed Count**: Total items processed
- **Average Processing Time**: Mean time per item
- **Queue Length**: Current and average queue length
- **Failure Rate**: Failures per unit time (if enabled)
- **Downtime**: Total time in failed state

### Quality Metrics
Tracked throughout batch lifecycle:
- Separation quality (centrifuge)
- Platelet yield and viability
- QC test results
- Storage temperature stability

## Advantages of SimPy Approach

### Compared to Azure IoT-based Approach

| Aspect | SimPy | Azure IoT |
|--------|-------|-----------|
| **Purpose** | Process analysis & optimization | Cloud integration & monitoring |
| **Complexity** | Simpler, pure Python | Requires Azure infrastructure |
| **Speed** | Fast (simulated time) | Real-time only |
| **Scenarios** | Easy to run multiple scenarios | One configuration at a time |
| **Cost** | Free, runs locally | Azure service costs |
| **Queuing** | Automatic queue modeling | Manual implementation |
| **Statistics** | Built-in statistical analysis | Requires separate analytics |
| **Best For** | "What-if" analysis, capacity planning | Live monitoring, digital twin |

### When to Use SimPy
✅ Capacity planning and optimization  
✅ Bottleneck analysis  
✅ Process improvement experiments  
✅ Staff allocation optimization  
✅ Quick scenario comparison  
✅ Offline analysis and design  

### When to Use Azure IoT
✅ Real-time monitoring of actual devices  
✅ Live dashboard and visualization  
✅ Integration with enterprise systems  
✅ Historical data collection  
✅ Cloud-based collaboration  

## Advanced Usage

### Custom Device Configuration

```python
# Create custom centrifuge
from simpy_devices import Centrifuge

env = simpy.Environment()
centrifuge = Centrifuge(
    env=env,
    device_id="centrifuge_custom",
    capacity=6,              # 6 bags simultaneously
    mean_spin_time=150.0,    # Faster centrifuge
    target_rpm=4000,         # Higher RPM
    mtbf=18000.0,           # More reliable
    mttr=900.0              # Faster repairs
)
```

### Custom Workflow

```python
def custom_workflow(env, batch):
    """Custom processing workflow."""
    # Skip agitation for rush orders
    scanner = BloodBagScanner(env)
    yield from scanner.process_batch(batch)
    
    centrifuge = Centrifuge(env)
    yield from centrifuge.process_batch(batch)
    
    # Skip directly to QC
    qc = QualityControl(env)
    yield from qc.process_batch(batch)
```

### Extending Device Simulators

```python
from simpy_core.simpy_base import SimPyDeviceSimulator

class CustomDevice(SimPyDeviceSimulator):
    """Custom device with specialized logic."""
    
    def _perform_processing(self, batch):
        # Custom processing logic
        process_time = calculate_custom_time(batch)
        yield self.env.timeout(process_time)
        
        result = {
            'success': True,
            'custom_metric': calculate_metric(batch)
        }
        
        return process_time, result
```

## Testing

Run the included tests:
```bash
cd simulators
python -m pytest test_simpy_simulators.py -v
```

## Documentation Files

- **README_SIMPY.md** (this file): Complete guide to SimPy implementation
- **simpy_demo.py**: Interactive demo and examples
- **platelet_pooling_simulation.py**: Main simulation environment
- **simpy_core/simpy_base.py**: Base classes documentation
- **simpy_devices/*.py**: Individual device simulator documentation

## Integration with Existing Project

The SimPy implementation is **complementary** to the existing Azure-based digital twin:

1. **Design Phase**: Use SimPy for capacity planning and process optimization
2. **Implementation Phase**: Deploy Azure infrastructure based on SimPy insights
3. **Operations Phase**: Use Azure for real-time monitoring of actual devices
4. **Improvement Phase**: Use SimPy to model proposed changes before deployment

## Support and Contribution

For questions or issues:
1. Check the documentation in each module
2. Review the demo examples in `simpy_demo.py`
3. Examine the test suite for usage patterns
4. Create an issue in the GitHub repository

## Future Enhancements

Potential additions to the SimPy implementation:
- [ ] Staff resource modeling (technician availability)
- [ ] Shift scheduling and handoffs
- [ ] Batch priority and rush orders
- [ ] Multiple product types
- [ ] Cost modeling and optimization
- [ ] Real-time visualization during simulation
- [ ] Integration with Azure Digital Twins for hybrid approach

## References

- **SimPy Documentation**: https://simpy.readthedocs.io/
- **Discrete-Event Simulation**: https://en.wikipedia.org/wiki/Discrete-event_simulation
- **Queueing Theory**: https://en.wikipedia.org/wiki/Queueing_theory

---

**Version**: 1.0  
**Last Updated**: January 2026  
**Authors**: Platelet Pooling Digital Twin Team
