"""
Main simulator runner script.

Demonstrates a complete end-to-end cycle for a single device simulator:
1. Initialize device simulator
2. Connect to Azure IoT Hub
3. Run processing cycle
4. Send telemetry and events
"""
import asyncio
import logging
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from devices.centrifuge_simulator import CentrifugeSimulator
from core.iot_connector import IoTConnector


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SimulatorRunner")


async def run_centrifuge_cycle(device_id: str, connection_string: str, batch_id: str):
    """
    Run a complete processing cycle for the centrifuge simulator.
    
    This demonstrates the full end-to-end workflow:
    1. Create simulator instance
    2. Connect to IoT Hub
    3. Start processing a batch
    4. Send periodic telemetry during processing
    5. Complete processing and send results
    6. Disconnect
    
    Args:
        device_id: Unique device identifier
        connection_string: Azure IoT Hub connection string
        batch_id: Batch identifier to process
    """
    logger.info(f"=== Starting Centrifuge Cycle for {device_id} ===")
    
    # 1. Initialize simulator
    centrifuge = CentrifugeSimulator(device_id=device_id, telemetry_interval=5)
    centrifuge.start()
    logger.info(f"✓ Centrifuge simulator initialized")
    
    # 2. Connect to IoT Hub
    iot_connector = IoTConnector(connection_string, device_id)
    
    try:
        connected = await iot_connector.connect()
        if not connected:
            logger.error("Failed to connect to IoT Hub. Exiting.")
            return
        logger.info(f"✓ Connected to Azure IoT Hub")
        
        # 3. Send initial telemetry (idle state)
        initial_telemetry = centrifuge.generate_telemetry()
        await iot_connector.send_telemetry(initial_telemetry)
        logger.info(f"✓ Sent initial telemetry - State: {initial_telemetry['state']}")
        
        await asyncio.sleep(2)
        
        # 4. Start processing batch
        success = centrifuge.start_processing(batch_id)
        if success:
            # Send event: processing started
            event_data = centrifuge.get_base_telemetry()
            event_data.update({
                "batch_id": batch_id,
                "estimated_completion_seconds": centrifuge.cycle_time_minutes * 60
            })
            await iot_connector.send_event("processing_started", event_data)
            logger.info(f"✓ Started processing batch: {batch_id}")
        else:
            logger.error("Failed to start processing")
            return
        
        # 5. Simulate processing cycle with periodic telemetry
        # For demo purposes, we'll send telemetry every 5 seconds for 30 seconds
        # (In production, this would run for the full cycle time)
        cycle_duration = 30  # Demo: 30 seconds instead of 15 minutes
        elapsed = 0
        
        logger.info(f"⚙️  Processing batch (demo: {cycle_duration}s, real: {centrifuge.cycle_time_minutes}min)")
        
        while elapsed < cycle_duration:
            await asyncio.sleep(centrifuge.telemetry_interval)
            elapsed += centrifuge.telemetry_interval
            
            # Generate and send telemetry
            telemetry = centrifuge.generate_telemetry()
            await iot_connector.send_telemetry(telemetry)
            
            logger.info(
                f"  [{elapsed}s] RPM: {telemetry['rpm']}, "
                f"Temp: {telemetry['temperature_celsius']}°C, "
                f"Vibration: {telemetry['vibration_mm_s']} mm/s"
            )
        
        # 6. Complete processing
        result = centrifuge.complete_processing()
        await iot_connector.send_event("processing_complete", result)
        logger.info(f"✓ Processing complete - Quality: {result['quality_metrics']['separation_quality']:.2%}")
        
        # 7. Send final telemetry (back to idle)
        await asyncio.sleep(2)
        final_telemetry = centrifuge.generate_telemetry()
        await iot_connector.send_telemetry(final_telemetry)
        logger.info(f"✓ Sent final telemetry - State: {final_telemetry['state']}")
        
        # Summary
        logger.info(f"\n=== Cycle Summary ===")
        logger.info(f"Device: {device_id}")
        logger.info(f"Batch: {batch_id}")
        logger.info(f"Cycles Completed: {centrifuge.cycles_completed}")
        logger.info(f"Total Runtime: {centrifuge.total_runtime_hours:.2f} hours")
        logger.info(f"Separation Quality: {result['quality_metrics']['separation_quality']:.2%}")
        logger.info(f"Platelet Yield: {result['quality_metrics']['platelet_yield']:.2%}")
        
    except Exception as e:
        logger.error(f"Error during cycle: {e}", exc_info=True)
    finally:
        # 8. Disconnect from IoT Hub
        await iot_connector.disconnect()
        centrifuge.stop()
        logger.info(f"✓ Disconnected and stopped simulator")


async def demonstrate_fault_scenario(device_id: str, connection_string: str):
    """
    Demonstrate a fault scenario where the device encounters an error.
    
    Args:
        device_id: Unique device identifier
        connection_string: Azure IoT Hub connection string
    """
    logger.info(f"\n=== Demonstrating Fault Scenario ===")
    
    centrifuge = CentrifugeSimulator(device_id=device_id, telemetry_interval=5)
    centrifuge.start()
    
    async with IoTConnector(connection_string, device_id) as iot:
        # Normal operation
        centrifuge.start_processing("BATCH-FAULT-001")
        telemetry = centrifuge.generate_telemetry()
        await iot.send_telemetry(telemetry)
        logger.info(f"Normal operation: {telemetry['state']}")
        
        await asyncio.sleep(3)
        
        # Simulate fault
        centrifuge.simulate_fault("vibration")
        fault_telemetry = centrifuge.generate_telemetry()
        await iot.send_telemetry(fault_telemetry)
        
        # Send error event
        error_event = centrifuge.get_base_telemetry()
        await iot.send_event("device_error", error_event)
        logger.error(f"⚠️  Fault occurred: {fault_telemetry['error_state']}")
        
        await asyncio.sleep(2)
        
        # Clear error
        centrifuge.clear_error()
        recovered_telemetry = centrifuge.generate_telemetry()
        await iot.send_telemetry(recovered_telemetry)
        await iot.send_event("error_cleared", centrifuge.get_base_telemetry())
        logger.info(f"✓ Error cleared, device recovered")


async def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()
    
    # Get configuration from environment
    device_id = os.getenv("DEVICE_ID", "centrifuge-01")
    connection_string = os.getenv("IOT_HUB_DEVICE_CONNECTION_STRING")
    
    if not connection_string:
        logger.error(
            "Missing IOT_HUB_DEVICE_CONNECTION_STRING environment variable.\n"
            "Please set it in a .env file or environment."
        )
        sys.exit(1)
    
    # Generate batch ID
    batch_id = f"BATCH-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    
    try:
        # Run normal processing cycle
        await run_centrifuge_cycle(device_id, connection_string, batch_id)
        
        # Optional: Demonstrate fault scenario
        # await demonstrate_fault_scenario(device_id, connection_string)
        
    except KeyboardInterrupt:
        logger.info("\nSimulation interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
