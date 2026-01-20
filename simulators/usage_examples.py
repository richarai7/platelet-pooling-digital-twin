"""
Quick reference examples for using each device simulator.

This file shows common usage patterns for all 12 devices.
"""
import asyncio
from devices import (
    BloodBagScannerSimulator,
    CentrifugeSimulator,
    PlasmaExtractorSimulator,
    MacopressSimulator,
    PlateletAgitatorSimulator,
    SterileConnectorSimulator,
    PoolingStationSimulator,
    QualityControlSimulator,
    LabelingStationSimulator,
    StorageRefrigeratorSimulator,
    BarcodeReaderSimulator,
    ShippingPrepSimulator
)


def example_blood_bag_scanner():
    """Example: Scan a blood bag."""
    scanner = BloodBagScannerSimulator("scanner-01")
    
    # Start scan
    scanner.start_processing("BATCH-001")
    
    # Get telemetry
    telemetry = scanner.generate_telemetry()
    print(f"Scan quality: {telemetry['barcode_quality']}")
    
    # Complete scan
    result = scanner.complete_processing()
    print(f"Donation ID: {result['barcode_data']['donation_id']}")
    print(f"Blood type: {result['barcode_data']['blood_type']}")


def example_centrifuge():
    """Example: Centrifuge blood."""
    centrifuge = CentrifugeSimulator("centrifuge-01")
    
    # Start centrifugation
    centrifuge.start_processing("BATCH-001")
    
    # Monitor during spin
    telemetry = centrifuge.generate_telemetry()
    print(f"RPM: {telemetry['rpm']}, Temp: {telemetry['temperature_celsius']}°C")
    
    # Complete
    result = centrifuge.complete_processing()
    print(f"Separation quality: {result['quality_metrics']['separation_quality']}")


def example_plasma_extractor():
    """Example: Extract plasma."""
    extractor = PlasmaExtractorSimulator("extractor-01")
    
    # Start extraction
    extractor.start_processing("BATCH-001")
    
    # Monitor extraction
    telemetry = extractor.generate_telemetry()
    print(f"Pressure: {telemetry['extraction_pressure_psi']} PSI")
    print(f"Flow: {telemetry['flow_rate_ml_per_min']} mL/min")
    
    # Complete
    result = extractor.complete_processing()
    print(f"Extracted: {result['quality_metrics']['extracted_volume_ml']} mL")


def example_pooling_station():
    """Example: Pool platelet units."""
    pooling = PoolingStationSimulator("pooling-01")
    
    # Start pooling
    pooling.start_processing("BATCH-001")
    
    # Monitor progress
    telemetry = pooling.generate_telemetry()
    print(f"Volume: {telemetry['current_volume_ml']} mL")
    print(f"Units pooled: {telemetry['units_pooled']}/{telemetry['target_units']}")
    
    # Complete
    result = pooling.complete_processing()
    print(f"Final volume: {result['final_volume_ml']} mL")
    print(f"Concentration: {result['quality_metrics']['platelet_concentration']}")


def example_quality_control():
    """Example: Run QC tests."""
    qc = QualityControlSimulator("qc-01")
    
    # Start testing
    qc.start_processing("BATCH-001")
    
    # Monitor tests
    telemetry = qc.generate_telemetry()
    print(f"Platelet count: {telemetry['platelet_count_x10_9_per_L']}")
    print(f"pH: {telemetry['ph_level']}")
    print(f"Glucose: {telemetry['glucose_level_mg_per_dL']} mg/dL")
    
    # Get results
    result = qc.complete_processing()
    print(f"QC Status: {'PASSED' if result['success'] else 'FAILED'}")
    print(f"Bacterial test: {result['test_results']['bacterial_test']}")


def example_labeling_station():
    """Example: Apply label."""
    labeler = LabelingStationSimulator("labeler-01")
    
    # Check consumables
    telemetry = labeler.generate_telemetry()
    print(f"Labels available: {telemetry['label_stock_count']}")
    print(f"Ribbon: {telemetry['ribbon_remaining_meters']} m")
    
    # Start labeling
    labeler.start_processing("BATCH-001")
    
    # Complete
    result = labeler.complete_processing()
    print(f"Product ID: {result['label_data']['product_id']}")
    print(f"Expires: {result['label_data']['expiration_date']}")


def example_storage_refrigerator():
    """Example: Store and retrieve product."""
    storage = StorageRefrigeratorSimulator("storage-01")
    
    # Store product
    storage.start_processing("BATCH-001")
    
    # Check inventory
    telemetry = storage.generate_telemetry()
    print(f"Inventory: {telemetry['current_inventory_count']}/{telemetry['max_capacity']}")
    print(f"Temperature: {telemetry['internal_temperature_celsius']}°C")
    print(f"Utilization: {telemetry['capacity_utilization_percent']}%")
    
    # Retrieve product (FIFO)
    result = storage.complete_processing()
    print(f"Retrieved batch: {result['batch_id']}")
    print(f"Storage integrity: {result['quality_metrics']['product_integrity']}")


def example_barcode_reader():
    """Example: Verify product barcode."""
    barcode = BarcodeReaderSimulator("barcode-01")
    
    # Scan for verification
    barcode.start_processing("BATCH-001")
    
    # Get scan quality
    telemetry = barcode.generate_telemetry()
    print(f"Scan quality: {telemetry['last_scan_quality']}")
    
    # Verify
    result = barcode.complete_processing()
    print(f"Verification: {result['barcode_data']['verification_status']}")
    print(f"Barcode: {result['barcode_data']['barcode']}")


def example_shipping_prep():
    """Example: Prepare for shipping."""
    shipping = ShippingPrepSimulator("shipping-01")
    
    # Check consumables
    telemetry = shipping.generate_telemetry()
    print(f"Boxes: {telemetry['insulation_boxes_available']}")
    print(f"Monitors: {telemetry['temperature_monitors_available']}")
    
    # Start prep
    shipping.start_processing("BATCH-001")
    
    # Monitor progress
    telemetry = shipping.generate_telemetry()
    print(f"Packaging: {telemetry['packaging_complete']}")
    print(f"Documentation: {telemetry['documentation_complete']}")
    
    # Complete
    result = shipping.complete_processing()
    print(f"Shipment ID: {result['shipping_data']['shipment_id']}")
    print(f"Destination: {result['shipping_data']['destination']}")
    print(f"Delivery: {result['shipping_data']['estimated_delivery']}")


def example_fault_injection():
    """Example: Simulate device faults."""
    centrifuge = CentrifugeSimulator("centrifuge-01")
    
    # Simulate a fault
    centrifuge.simulate_fault("motor_overload")
    
    # Check error state
    telemetry = centrifuge.generate_telemetry()
    print(f"State: {telemetry['state']}")
    print(f"Error: {telemetry['error_message']}")
    
    # Try to start (will fail)
    success = centrifuge.start_processing("BATCH-001")
    print(f"Start attempt: {success}")  # False
    
    # Clear error
    centrifuge.clear_error()
    
    # Now can start
    success = centrifuge.start_processing("BATCH-001")
    print(f"Start after clear: {success}")  # True


async def example_iot_integration():
    """Example: Send telemetry to Azure IoT Hub."""
    from core.iot_connector import IoTConnector
    
    # Initialize device and connector
    centrifuge = CentrifugeSimulator("centrifuge-01")
    
    async with IoTConnector("centrifuge-01", "YOUR_CONNECTION_STRING") as connector:
        # Start processing
        centrifuge.start_processing("BATCH-001")
        
        # Send processing started event
        await connector.send_event("processing_started", {
            "batch_id": "BATCH-001",
            "timestamp": "2026-01-20T12:00:00Z"
        })
        
        # Send telemetry every 5 seconds
        for i in range(3):
            await asyncio.sleep(5)
            telemetry = centrifuge.generate_telemetry()
            await connector.send_telemetry(telemetry)
        
        # Complete processing
        result = centrifuge.complete_processing()
        
        # Send completion event
        await connector.send_event("processing_complete", result)


def example_multi_device_workflow():
    """Example: Coordinate multiple devices."""
    scanner = BloodBagScannerSimulator("scanner-01")
    centrifuge = CentrifugeSimulator("centrifuge-01")
    pooling = PoolingStationSimulator("pooling-01")
    
    batch_id = "BATCH-001"
    
    # Step 1: Scan
    scanner.start_processing(batch_id)
    scan_result = scanner.complete_processing()
    
    if not scan_result['success']:
        print("Scan failed, aborting")
        return
    
    # Step 2: Centrifuge
    centrifuge.start_processing(batch_id)
    cent_result = centrifuge.complete_processing()
    
    if cent_result['quality_metrics']['separation_quality'] < 0.9:
        print("Poor separation, aborting")
        return
    
    # Step 3: Pool
    pooling.start_processing(batch_id)
    pool_result = pooling.complete_processing()
    
    print(f"Workflow complete! Final volume: {pool_result['final_volume_ml']} mL")


if __name__ == "__main__":
    print("=" * 60)
    print("DEVICE SIMULATOR USAGE EXAMPLES")
    print("=" * 60)
    
    print("\n1. Blood Bag Scanner:")
    example_blood_bag_scanner()
    
    print("\n2. Centrifuge:")
    example_centrifuge()
    
    print("\n3. Plasma Extractor:")
    example_plasma_extractor()
    
    print("\n4. Pooling Station:")
    example_pooling_station()
    
    print("\n5. Quality Control:")
    example_quality_control()
    
    print("\n6. Labeling Station:")
    example_labeling_station()
    
    print("\n7. Storage Refrigerator:")
    example_storage_refrigerator()
    
    print("\n8. Barcode Reader:")
    example_barcode_reader()
    
    print("\n9. Shipping Prep:")
    example_shipping_prep()
    
    print("\n10. Fault Injection:")
    example_fault_injection()
    
    print("\n11. Multi-Device Workflow:")
    example_multi_device_workflow()
    
    print("\n" + "=" * 60)
