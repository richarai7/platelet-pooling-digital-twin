# Getting Started with SimPy-based Platelet Pooling Simulators

This guide will help you quickly get up and running with the SimPy-based discrete-event simulation for the platelet pooling process.

## What You'll Learn

- How to install and run the SimPy simulators
- Understanding the simulation output
- Running different scenarios (baseline, stress test, reliability testing)
- Analyzing simulation results
- Customizing configurations

## Prerequisites

- Python 3.11 or higher
- Basic understanding of discrete-event simulation concepts (helpful but not required)

## Installation

### 1. Navigate to the simulators directory

```bash
cd /path/to/platelet-pooling-digital-twin/simulators
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `simpy==4.1.1` - Discrete-event simulation framework
- Other dependencies (azure-iot-device, pydantic, etc.)

### 3. Verify installation

```bash
python -c "import simpy; print(f'SimPy version: {simpy.__version__}')"
```

You should see: `SimPy version: 4.1.1`

## Quick Start - Your First Simulation

### Option 1: Interactive Demo

Run the interactive demo menu:

```bash
python simpy_demo.py
```

You'll see a menu with options:

```
1. Basic Simulation (1 hour, default settings)
2. Stress Test (high batch volume)
3. Reliability Test (with device failures)
4. Capacity Planning (compare scenarios)
5. Exit
```

Select option 1 to run a basic simulation.

### Option 2: Command Line

Run a specific simulation directly:

```bash
# Basic simulation
python simpy_demo.py basic

# Stress test
python simpy_demo.py stress

# Reliability test
python simpy_demo.py reliability

# Capacity planning
python simpy_demo.py capacity
```

## Understanding the Output

When you run a simulation, you'll see:

### 1. Real-time Log Messages

```
2026-01-23 02:11:30,566 - blood_bag_scanner.scanner_1 - INFO - Device scanner_1 started processing batch BATCH-00001 at 183.61 (waited 0.00s)
2026-01-23 02:11:30,566 - blood_bag_scanner.scanner_1 - INFO - Device scanner_1 completed batch BATCH-00001 at 188.36 (duration: 4.75s)
```

This shows each device processing batches through the system.

### 2. Simulation Summary

```
================================================================================
SIMULATION SUMMARY
================================================================================
Simulation Time: 3600.00s (1.00 hours)
Batches Created: 27
Batches Completed: 5
Batches Failed: 0
Completion Rate: 18.5%
Average Cycle Time: 6842.32s (114.04 min)
```

**Key Metrics:**
- **Batches Created**: Number of batches that entered the system
- **Batches Completed**: Number that finished all 12 processing steps
- **Completion Rate**: Percentage of batches that completed
- **Average Cycle Time**: Mean time from arrival to completion

### 3. Device Utilization

```
--------------------------------------------------------------------------------
DEVICE UTILIZATION
--------------------------------------------------------------------------------
scanner_1              - Util:   3.6% | Processed:   27 | Failures:  0
centrifuge_1           - Util:  93.8% | Processed:   15 | Failures:  0
centrifuge_2           - Util:  49.4% | Processed:    8 | Failures:  0
plasma_extractor_1     - Util:  56.0% | Processed:   22 | Failures:  0
```

**Understanding Utilization:**
- **< 50%**: Device has plenty of capacity
- **50-80%**: Moderate utilization
- **80-95%**: High utilization, approaching bottleneck
- **> 95%**: Bottleneck - limiting system throughput

## Running Your Own Scenarios

### Example 1: Baseline Analysis

Test the current process with default settings:

```python
from platelet_pooling_simulation import PlateletPoolingSimulation, SimulationConfig

config = SimulationConfig(
    simulation_duration=28800.0,  # 8-hour shift (in seconds)
    batch_arrival_rate=300.0,     # New batch every 5 minutes
    random_seed=42                # For reproducible results
)

sim = PlateletPoolingSimulation(config)
sim.run()
```

### Example 2: What-if Analysis - Add a Centrifuge

```python
# Test: What if we add a second centrifuge?
config = SimulationConfig(
    simulation_duration=28800.0,
    batch_arrival_rate=300.0,
    num_centrifuges=2,  # Changed from 1 to 2
    random_seed=42
)

sim = PlateletPoolingSimulation(config)
sim.run()

# Compare utilization and throughput
```

### Example 3: Test Higher Demand

```python
# Test: Can we handle 20% more batches?
config = SimulationConfig(
    simulation_duration=28800.0,
    batch_arrival_rate=240.0,  # 20% increase: batch every 4 minutes
    random_seed=42
)

sim = PlateletPoolingSimulation(config)
sim.run()
```

### Example 4: Reliability Testing

```python
# Test: Impact of device failures
config = SimulationConfig(
    simulation_duration=28800.0,
    batch_arrival_rate=300.0,
    enable_failures=True,
    mtbf=7200.0,  # Device fails every 2 hours on average
    mttr=1800.0   # Takes 30 minutes to repair
)

sim = PlateletPoolingSimulation(config)
sim.run()
```

## Analyzing Results

### Getting Detailed Metrics

```python
# After running simulation
metrics = sim.get_all_metrics()

# Simulation-level metrics
print(f"Throughput: {metrics['simulation']['batches_completed']} batches")
print(f"Completion Rate: {metrics['simulation']['completion_rate']*100:.1f}%")

# Device-level metrics
for device_type, devices in metrics['devices'].items():
    for device in devices:
        print(f"{device['device_id']}: {device['utilization']*100:.1f}% utilized")
```

### Identifying Bottlenecks

```python
# Find devices with highest utilization
for device_type, devices in metrics['devices'].items():
    for device in devices:
        if device['utilization'] > 0.90:
            print(f"Bottleneck identified: {device['device_id']}")
            print(f"  Utilization: {device['utilization']*100:.1f}%")
            print(f"  Suggestion: Add another {device_type}")
```

### Exporting Results

```python
import json

# Save metrics to file
with open('simulation_results.json', 'w') as f:
    json.dump(metrics, f, indent=2)
```

## Common Use Cases

### 1. Capacity Planning

**Question**: How many centrifuges do we need for expected demand?

```python
results = []

for num_centrifuges in [1, 2, 3]:
    config = SimulationConfig(
        simulation_duration=28800.0,
        batch_arrival_rate=300.0,
        num_centrifuges=num_centrifuges
    )
    
    sim = PlateletPoolingSimulation(config)
    sim.run()
    
    metrics = sim.get_all_metrics()
    results.append({
        'centrifuges': num_centrifuges,
        'completed': metrics['simulation']['batches_completed'],
        'utilization': metrics['devices']['centrifuges'][0]['utilization']
    })

# Analyze results to find optimal number
```

### 2. Process Improvement

**Question**: Which device upgrade would have the biggest impact?

Test improving processing time for each device:

```python
# Baseline
baseline_config = SimulationConfig(...)
baseline_sim = PlateletPoolingSimulation(baseline_config)
baseline_sim.run()
baseline_throughput = baseline_sim.batches_completed

# Test faster centrifuge
from simpy_devices import Centrifuge
# ... custom device configuration with faster processing time

# Compare throughput improvement
```

### 3. Demand Forecasting

**Question**: Can we handle a 30% increase in donations?

```python
# Current demand
current_config = SimulationConfig(
    batch_arrival_rate=300.0  # Current rate
)
current_sim = PlateletPoolingSimulation(current_config)
current_sim.run()

# Future demand (30% increase)
future_config = SimulationConfig(
    batch_arrival_rate=231.0  # 30% faster: 300 / 1.3 ≈ 231
)
future_sim = PlateletPoolingSimulation(future_config)
future_sim.run()

# Compare completion rates and identify needed changes
```

## Tips and Best Practices

### 1. Use Random Seeds for Reproducibility

Always use a `random_seed` when comparing scenarios:

```python
config = SimulationConfig(random_seed=42)
```

### 2. Run Long Enough to Reach Steady State

Short simulations may not show realistic patterns. For analysis, run at least:
- **Minimum**: 1 hour (3600s)
- **Recommended**: 8-hour shift (28800s)
- **Comprehensive**: 24 hours (86400s)

### 3. Warm-up Period

The first batches may not be representative. Consider:
- Run simulation longer than analysis period
- Discard first hour of data for analysis

### 4. Multiple Replications

For statistical confidence, run multiple replications:

```python
results = []
for seed in range(10):  # 10 replications
    config = SimulationConfig(random_seed=seed)
    sim = PlateletPoolingSimulation(config)
    sim.run()
    results.append(sim.batches_completed)

import statistics
print(f"Mean: {statistics.mean(results)}")
print(f"Std Dev: {statistics.stdev(results)}")
```

## Next Steps

- Read [README_SIMPY.md](README_SIMPY.md) for detailed documentation
- Explore device-specific configurations in `simpy_devices/`
- Review test examples in `test_simpy_simulators.py`
- Create custom scenarios based on your requirements

## Troubleshooting

### Issue: Simulation runs but 0 batches complete

**Cause**: Simulation time too short for batches to complete all 12 steps.

**Solution**: Increase `simulation_duration`:
```python
config = SimulationConfig(simulation_duration=14400.0)  # 4 hours
```

### Issue: Import errors

**Cause**: SimPy not installed or wrong directory.

**Solution**: 
```bash
pip install simpy==4.1.1
# Make sure you're in the simulators/ directory
```

### Issue: Want to see less logging

**Solution**: Reduce logging level:
```python
import logging
logging.basicConfig(level=logging.WARNING)  # Only show warnings and errors
```

## Support

- Documentation: See `README_SIMPY.md` for comprehensive guide
- Examples: Run `python simpy_demo.py` for interactive examples
- Tests: Check `test_simpy_simulators.py` for usage patterns
- Issues: Create a GitHub issue for bugs or questions

---

**Happy Simulating!** 🔬🩸
