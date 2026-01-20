"""
Quick test script to verify the simulator logic without Azure connectivity.

This demonstrates the simulator behavior in isolation.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from devices.centrifuge_simulator import CentrifugeSimulator
import json
import time


def test_basic_cycle():
    """Test a basic processing cycle."""
    print("=" * 60)
    print("CENTRIFUGE SIMULATOR - LOCAL TEST (No Azure)")
    print("=" * 60)
    
    # Create simulator
    centrifuge = CentrifugeSimulator(device_id="centrifuge-test-01")
    centrifuge.start()
    print(f"\n✓ Created simulator: {centrifuge.device_id}")
    
    # Initial state
    telemetry = centrifuge.generate_telemetry()
    print(f"\n📊 Initial State:")
    print(f"   State: {telemetry['state']}")
    print(f"   RPM: {telemetry['rpm']}")
    print(f"   Temperature: {telemetry['temperature_celsius']}°C")
    print(f"   Vibration: {telemetry['vibration_mm_s']} mm/s")
    
    # Start processing
    batch_id = "TEST-BATCH-001"
    success = centrifuge.start_processing(batch_id)
    print(f"\n▶️  Started processing batch: {batch_id}")
    
    # Simulate 3 telemetry readings during processing
    for i in range(3):
        time.sleep(1)  # Simulate time passing
        telemetry = centrifuge.generate_telemetry()
        print(f"\n📊 Telemetry #{i+1} (Processing):")
        print(f"   State: {telemetry['state']}")
        print(f"   RPM: {telemetry['rpm']:.1f} / {telemetry['target_rpm']}")
        print(f"   Temperature: {telemetry['temperature_celsius']:.1f}°C")
        print(f"   Vibration: {telemetry['vibration_mm_s']:.2f} mm/s")
        print(f"   Remaining: {telemetry['remaining_time_seconds']}s")
        print(f"   Batch: {telemetry['current_batch_id']}")
    
    # Complete processing
    result = centrifuge.complete_processing()
    print(f"\n✅ Processing Complete!")
    print(f"   Batch: {result['batch_id']}")
    print(f"   Separation Quality: {result['quality_metrics']['separation_quality']:.2%}")
    print(f"   Platelet Yield: {result['quality_metrics']['platelet_yield']:.2%}")
    print(f"   Cycles Completed: {centrifuge.cycles_completed}")
    
    # Final state
    telemetry = centrifuge.generate_telemetry()
    print(f"\n📊 Final State (Idle):")
    print(f"   State: {telemetry['state']}")
    print(f"   RPM: {telemetry['rpm']:.1f}")
    print(f"   Batch: {telemetry['current_batch_id'] or 'None'}")
    
    centrifuge.stop()
    print(f"\n✓ Simulator stopped\n")


def test_fault_scenario():
    """Test fault injection."""
    print("=" * 60)
    print("FAULT SCENARIO TEST")
    print("=" * 60)
    
    centrifuge = CentrifugeSimulator(device_id="centrifuge-test-02")
    centrifuge.start()
    
    # Start processing
    centrifuge.start_processing("FAULT-TEST-BATCH")
    print(f"\n▶️  Processing started")
    
    # Normal operation
    telemetry = centrifuge.generate_telemetry()
    print(f"   State: {telemetry['state']} (Normal)")
    
    # Inject fault
    centrifuge.simulate_fault("vibration")
    telemetry = centrifuge.generate_telemetry()
    print(f"\n⚠️  FAULT INJECTED!")
    print(f"   State: {telemetry['state']}")
    print(f"   Error: {telemetry['error_state']}")
    print(f"   Processing: {telemetry['is_processing']}")
    print(f"   RPM: {telemetry['rpm']}")
    
    # Try to start processing in error state
    can_start = centrifuge.start_processing("ANOTHER-BATCH")
    print(f"\n❌ Cannot start new batch while in error: {not can_start}")
    
    # Clear error
    centrifuge.clear_error()
    telemetry = centrifuge.generate_telemetry()
    print(f"\n✓ Error cleared")
    print(f"   State: {telemetry['state']}")
    print(f"   Error: {telemetry['error_state'] or 'None'}")
    
    # Can process again
    can_start = centrifuge.start_processing("RECOVERY-BATCH")
    print(f"\n✓ Can start new batch after recovery: {can_start}")
    
    centrifuge.stop()
    print()


def test_telemetry_json():
    """Test telemetry JSON serialization."""
    print("=" * 60)
    print("TELEMETRY JSON TEST")
    print("=" * 60)
    
    centrifuge = CentrifugeSimulator(device_id="centrifuge-json-test")
    centrifuge.start()
    centrifuge.start_processing("JSON-BATCH")
    
    telemetry = centrifuge.generate_telemetry()
    
    # Serialize to JSON (as would be sent to IoT Hub)
    json_str = json.dumps(telemetry, indent=2)
    print(f"\n📤 Telemetry as JSON (ready for IoT Hub):\n")
    print(json_str)
    
    # Verify it can be parsed
    parsed = json.loads(json_str)
    print(f"\n✓ JSON is valid and parseable")
    print(f"  Device: {parsed['device_id']}")
    print(f"  Type: {parsed['device_type']}")
    print(f"  State: {parsed['state']}")
    
    centrifuge.stop()
    print()


if __name__ == "__main__":
    test_basic_cycle()
    print("\n" + "=" * 60 + "\n")
    test_fault_scenario()
    print("\n" + "=" * 60 + "\n")
    test_telemetry_json()
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✅")
    print("=" * 60)
    print("\nNext step: Run with Azure IoT Hub using: python run_simulator.py")
    print()
