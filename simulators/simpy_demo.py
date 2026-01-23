"""
SimPy-based Platelet Pooling Simulation - Demo Script

This script demonstrates how to run the complete platelet pooling
simulation using SimPy with all 12 devices.
"""
import sys
import os

# Add simulators directory to path
sys.path.insert(0, os.path.dirname(__file__))

from platelet_pooling_simulation import PlateletPoolingSimulation, SimulationConfig


def run_basic_simulation():
    """Run a basic simulation with default settings."""
    print("\n" + "=" * 80)
    print("PLATELET POOLING DIGITAL TWIN - SimPy Simulation")
    print("=" * 80)
    print("\nRunning basic simulation with default configuration...")
    
    # Create configuration
    config = SimulationConfig(
        simulation_duration=3600.0,  # 1 hour
        batch_arrival_rate=180.0,    # New batch every 3 minutes
        random_seed=42,              # For reproducibility
        num_centrifuges=2,           # 2 centrifuges
        enable_failures=False        # No failures for this demo
    )
    
    # Create and run simulation
    sim = PlateletPoolingSimulation(config)
    sim.run()
    
    return sim


def run_stress_test_simulation():
    """Run a stress test with high batch arrival rate."""
    print("\n" + "=" * 80)
    print("STRESS TEST SIMULATION - High Volume")
    print("=" * 80)
    print("\nRunning stress test with high batch arrival rate...")
    
    config = SimulationConfig(
        simulation_duration=7200.0,  # 2 hours
        batch_arrival_rate=120.0,    # New batch every 2 minutes (high volume)
        random_seed=42,
        num_scanners=2,              # Extra devices
        num_centrifuges=3,
        num_qc_devices=2,
        enable_failures=False
    )
    
    sim = PlateletPoolingSimulation(config)
    sim.run()
    
    return sim


def run_reliability_simulation():
    """Run simulation with device failures enabled."""
    print("\n" + "=" * 80)
    print("RELIABILITY SIMULATION - With Device Failures")
    print("=" * 80)
    print("\nRunning simulation with random device failures...")
    
    config = SimulationConfig(
        simulation_duration=14400.0,  # 4 hours
        batch_arrival_rate=300.0,     # New batch every 5 minutes
        random_seed=42,
        num_centrifuges=2,
        enable_failures=True,         # Enable random failures
        mtbf=7200.0,                  # Failure every 2 hours on average
        mttr=600.0                    # 10 minute repair time
    )
    
    sim = PlateletPoolingSimulation(config)
    sim.run()
    
    return sim


def run_capacity_planning_simulation():
    """Run simulation to test different capacity scenarios."""
    print("\n" + "=" * 80)
    print("CAPACITY PLANNING - Comparing Scenarios")
    print("=" * 80)
    
    scenarios = [
        {
            'name': 'Baseline (1 of each device)',
            'config': SimulationConfig(
                simulation_duration=3600.0,
                batch_arrival_rate=300.0,
                random_seed=42
            )
        },
        {
            'name': 'Scenario 2: Double Centrifuges',
            'config': SimulationConfig(
                simulation_duration=3600.0,
                batch_arrival_rate=300.0,
                random_seed=42,
                num_centrifuges=2
            )
        },
        {
            'name': 'Scenario 3: High Capacity Setup',
            'config': SimulationConfig(
                simulation_duration=3600.0,
                batch_arrival_rate=180.0,  # More frequent batches
                random_seed=42,
                num_scanners=2,
                num_centrifuges=3,
                num_plasma_extractors=2,
                num_qc_devices=2
            )
        }
    ]
    
    results = []
    for scenario in scenarios:
        print(f"\n{'=' * 80}")
        print(f"Running: {scenario['name']}")
        print('=' * 80)
        
        sim = PlateletPoolingSimulation(scenario['config'])
        sim.run()
        
        metrics = sim.get_all_metrics()
        results.append({
            'name': scenario['name'],
            'metrics': metrics
        })
    
    # Compare results
    print("\n" + "=" * 80)
    print("SCENARIO COMPARISON")
    print("=" * 80)
    print(f"{'Scenario':<35} | {'Completed':<10} | {'Completion Rate':<15} | {'Avg Cycle Time'}")
    print("-" * 80)
    
    for result in results:
        sim_metrics = result['metrics']['simulation']
        scenario_name = result['name']
        completed = sim_metrics['batches_completed']
        rate = sim_metrics['completion_rate'] * 100
        
        print(f"{scenario_name:<35} | {completed:<10} | {rate:<14.1f}% | N/A")
    
    print("=" * 80)


def interactive_menu():
    """Interactive menu for running different simulations."""
    while True:
        print("\n" + "=" * 80)
        print("PLATELET POOLING SIMULATION - SimPy Demo")
        print("=" * 80)
        print("\nSelect a simulation to run:")
        print("  1. Basic Simulation (1 hour, default settings)")
        print("  2. Stress Test (high batch volume)")
        print("  3. Reliability Test (with device failures)")
        print("  4. Capacity Planning (compare scenarios)")
        print("  5. Exit")
        print()
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == '1':
            run_basic_simulation()
        elif choice == '2':
            run_stress_test_simulation()
        elif choice == '3':
            run_reliability_simulation()
        elif choice == '4':
            run_capacity_planning_simulation()
        elif choice == '5':
            print("\nExiting. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == 'basic':
            run_basic_simulation()
        elif mode == 'stress':
            run_stress_test_simulation()
        elif mode == 'reliability':
            run_reliability_simulation()
        elif mode == 'capacity':
            run_capacity_planning_simulation()
        else:
            print(f"Unknown mode: {mode}")
            print("Usage: python simpy_demo.py [basic|stress|reliability|capacity]")
    else:
        # Run interactive menu
        interactive_menu()
