"""
Test all 12 device simulators locally without Azure.

Demonstrates a complete end-to-end platelet pooling process
using all devices in sequence.
"""
import asyncio
import logging
from datetime import datetime

from devices import (
    BloodBagScannerSimulator,
    CentrifugeSimulator,
    PlasmaExtractorSimulator,
    SterileConnectorSimulator,
    PoolingStationSimulator,
    QualityControlSimulator,
    LabelingStationSimulator,
    StorageRefrigeratorSimulator,
    BarcodeReaderSimulator,
    ShippingPrepSimulator,
    MacopressSimulator,
    PlateletAgitatorSimulator
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def run_complete_platelet_pooling_cycle():
    """
    Run a complete platelet pooling cycle through all 12 devices.
    
    Process flow:
    1. Blood Bag Scanner - Scan incoming blood bags
    2. Centrifuge - Separate blood components
    3. Plasma Extractor - Extract plasma
    4. Macopress - Express platelets
    5. Platelet Agitator - Mix platelets
    6. Sterile Connector - Connect bags for pooling
    7. Pooling Station - Pool multiple units
    8. Quality Control - Test pooled product
    9. Labeling Station - Apply product labels
    10. Storage Refrigerator - Store product
    11. Barcode Reader - Final verification
    12. Shipping Prep - Prepare for distribution
    """
    batch_id = f"BATCH-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    logger.info(f"=" * 80)
    logger.info(f"Starting complete platelet pooling cycle for {batch_id}")
    logger.info(f"=" * 80)
    
    # Initialize all devices
    scanner = BloodBagScannerSimulator("scanner-01")
    centrifuge = CentrifugeSimulator("centrifuge-01")
    extractor = PlasmaExtractorSimulator("extractor-01")
    macopress = MacopressSimulator("macopress-01")
    agitator = PlateletAgitatorSimulator("agitator-01")
    connector = SterileConnectorSimulator("connector-01")
    pooling = PoolingStationSimulator("pooling-01")
    qc = QualityControlSimulator("qc-01")
    labeler = LabelingStationSimulator("labeler-01")
    storage = StorageRefrigeratorSimulator("storage-01")
    barcode = BarcodeReaderSimulator("barcode-01")
    shipping = ShippingPrepSimulator("shipping-01")
    
    try:
        # Step 1: Scan blood bags
        logger.info("\n[STEP 1] Scanning blood bags...")
        scanner.start_processing(f"{batch_id}-SCAN")
        await asyncio.sleep(2.5)  # Wait for scan to complete
        telemetry = scanner.generate_telemetry()
        logger.info(f"  Remaining time: {telemetry.get('remaining_time_seconds')}s")
        result = scanner.complete_processing()
        if result:
            logger.info(f"  Result: {result.get('success')}")
            if result.get('barcode_data'):
                logger.info(f"  Donation ID: {result.get('barcode_data', {}).get('donation_id')}")
                logger.info(f"  Blood Type: {result.get('barcode_data', {}).get('blood_type')}")
        
        # Step 2: Centrifuge blood
        logger.info("\n[STEP 2] Centrifuging blood...")
        centrifuge.start_processing(f"{batch_id}-CENT")
        for i in range(3):
            await asyncio.sleep(1)
            telemetry = centrifuge.generate_telemetry()
            logger.info(f"  RPM: {telemetry.get('rpm')}, Temp: {telemetry.get('temperature_celsius')}°C")
        result = centrifuge.complete_processing()
        logger.info(f"  Separation quality: {result.get('quality_metrics', {}).get('separation_quality')}")
        
        # Step 3: Extract plasma
        logger.info("\n[STEP 3] Extracting plasma...")
        extractor.start_processing(f"{batch_id}-EXTR")
        for i in range(2):
            await asyncio.sleep(1)
            telemetry = extractor.generate_telemetry()
            logger.info(f"  Pressure: {telemetry.get('extraction_pressure_psi')} PSI, Flow: {telemetry.get('flow_rate_ml_per_min')} mL/min")
        result = extractor.complete_processing()
        logger.info(f"  Extracted volume: {result.get('quality_metrics', {}).get('extracted_volume_ml')} mL")
        
        # Step 4: Express platelets with Macopress
        logger.info("\n[STEP 4] Expressing platelets...")
        macopress.start_processing(f"{batch_id}-MACO")
        await asyncio.sleep(1)
        telemetry = macopress.generate_telemetry()
        logger.info(f"  Pressure: {telemetry.get('pressure_psi')} PSI")
        result = macopress.complete_processing()
        logger.info(f"  Recovery rate: {result.get('quality_metrics', {}).get('platelet_recovery_rate')}")
        
        # Step 5: Agitate platelets
        logger.info("\n[STEP 5] Agitating platelets...")
        agitator.start_processing(f"{batch_id}-AGIT")
        await asyncio.sleep(1)
        telemetry = agitator.generate_telemetry()
        logger.info(f"  RPM: {telemetry.get('rpm')}, Temp: {telemetry.get('temperature_celsius')}°C")
        result = agitator.complete_processing()
        logger.info(f"  Platelet activation: {result.get('quality_metrics', {}).get('platelet_activation')}")
        
        # Step 6: Sterile connection for pooling
        logger.info("\n[STEP 6] Creating sterile connections...")
        connector.start_processing(f"{batch_id}-CONN")
        await asyncio.sleep(1)
        telemetry = connector.generate_telemetry()
        logger.info(f"  Weld temp: {telemetry.get('welding_temperature_celsius')}°C, Pressure: {telemetry.get('weld_pressure_psi')} PSI")
        result = connector.complete_processing()
        logger.info(f"  Weld integrity: {result.get('quality_metrics', {}).get('weld_integrity')}")
        
        # Step 7: Pool multiple units
        logger.info("\n[STEP 7] Pooling platelet units...")
        pooling.start_processing(f"{batch_id}-POOL")
        for i in range(2):
            await asyncio.sleep(1)
            telemetry = pooling.generate_telemetry()
            logger.info(f"  Volume: {telemetry.get('current_volume_ml')} mL, Units pooled: {telemetry.get('units_pooled')}")
        result = pooling.complete_processing()
        logger.info(f"  Final volume: {result.get('final_volume_ml')} mL, Platelet concentration: {result.get('quality_metrics', {}).get('platelet_concentration')}")
        
        # Step 8: Quality control testing
        logger.info("\n[STEP 8] Running quality control tests...")
        qc.start_processing(f"{batch_id}-QC")
        for i in range(2):
            await asyncio.sleep(1)
            telemetry = qc.generate_telemetry()
            logger.info(f"  Platelet count: {telemetry.get('platelet_count_x10_9_per_L')}, pH: {telemetry.get('ph_level')}, Glucose: {telemetry.get('glucose_level_mg_per_dL')}")
        result = qc.complete_processing()
        logger.info(f"  QC Result: {'PASSED' if result.get('success') else 'FAILED'}")
        logger.info(f"  Bacterial test: {result.get('test_results', {}).get('bacterial_test')}")
        
        # Step 9: Apply labels
        logger.info("\n[STEP 9] Applying product labels...")
        labeler.start_processing(f"{batch_id}-LABEL")
        await asyncio.sleep(1)
        telemetry = labeler.generate_telemetry()
        logger.info(f"  Printer temp: {telemetry.get('printer_temperature_celsius')}°C, Print quality: {telemetry.get('print_quality_score')}")
        result = labeler.complete_processing()
        logger.info(f"  Product ID: {result.get('label_data', {}).get('product_id')}")
        logger.info(f"  Expiration: {result.get('label_data', {}).get('expiration_date')}")
        
        # Step 10: Store in refrigerator
        logger.info("\n[STEP 10] Storing in refrigerator...")
        storage.start_processing(f"{batch_id}-STOR")
        await asyncio.sleep(1)
        telemetry = storage.generate_telemetry()
        logger.info(f"  Temperature: {telemetry.get('internal_temperature_celsius')}°C, Inventory: {telemetry.get('current_inventory_count')}/{telemetry.get('max_capacity')}")
        logger.info(f"  Product stored successfully")
        
        # Step 11: Retrieve and scan barcode for verification
        logger.info("\n[STEP 11] Final barcode verification...")
        result = storage.complete_processing()  # Retrieve from storage
        logger.info(f"  Product retrieved from storage")
        
        barcode.start_processing(f"{batch_id}-VERIFY")
        await asyncio.sleep(1)
        telemetry = barcode.generate_telemetry()
        logger.info(f"  Scan quality: {telemetry.get('last_scan_quality')}")
        result = barcode.complete_processing()
        logger.info(f"  Verification: {result.get('barcode_data', {}).get('verification_status')}")
        
        # Step 12: Prepare for shipping
        logger.info("\n[STEP 12] Preparing for shipping...")
        shipping.start_processing(f"{batch_id}-SHIP")
        for i in range(2):
            await asyncio.sleep(1)
            telemetry = shipping.generate_telemetry()
            logger.info(f"  Package temp: {telemetry.get('package_temperature_celsius')}°C, Packaging: {telemetry.get('packaging_complete')}, Docs: {telemetry.get('documentation_complete')}")
        result = shipping.complete_processing()
        logger.info(f"  Shipment ID: {result.get('shipping_data', {}).get('shipment_id')}")
        logger.info(f"  Destination: {result.get('shipping_data', {}).get('destination')}")
        logger.info(f"  Estimated delivery: {result.get('shipping_data', {}).get('estimated_delivery')}")
        
        logger.info(f"\n{'=' * 80}")
        logger.info(f"Complete cycle finished successfully for {batch_id}")
        logger.info(f"{'=' * 80}")
        
        # Print summary statistics
        print("\n" + "=" * 80)
        print("DEVICE SUMMARY STATISTICS")
        print("=" * 80)
        devices = [
            ("Blood Bag Scanner", scanner),
            ("Centrifuge", centrifuge),
            ("Plasma Extractor", extractor),
            ("Macopress", macopress),
            ("Platelet Agitator", agitator),
            ("Sterile Connector", connector),
            ("Pooling Station", pooling),
            ("Quality Control", qc),
            ("Labeling Station", labeler),
            ("Storage Refrigerator", storage),
            ("Barcode Reader", barcode),
            ("Shipping Prep", shipping)
        ]
        
        for name, device in devices:
            telemetry = device.generate_telemetry()
            print(f"\n{name} ({device.device_id}):")
            print(f"  State: {telemetry.get('state')}")
            print(f"  Total runtime: {telemetry.get('total_runtime_hours', 0):.2f} hours")
            
            # Device-specific metrics
            if hasattr(device, 'cycles_completed'):
                print(f"  Cycles completed: {device.cycles_completed}")
            if hasattr(device, 'scans_completed'):
                print(f"  Scans completed: {device.scans_completed}")
            if hasattr(device, 'extractions_completed'):
                print(f"  Extractions completed: {device.extractions_completed}")
            if hasattr(device, 'connections_completed'):
                print(f"  Connections completed: {device.connections_completed}")
            if hasattr(device, 'pools_completed'):
                print(f"  Pools completed: {device.pools_completed}")
            if hasattr(device, 'tests_completed'):
                print(f"  Tests completed: {device.tests_completed}")
            if hasattr(device, 'labels_completed'):
                print(f"  Labels completed: {device.labels_completed}")
            if hasattr(device, 'total_units_stored'):
                print(f"  Units stored: {device.total_units_stored}")
            if hasattr(device, 'total_scans'):
                print(f"  Total scans: {device.total_scans}")
            if hasattr(device, 'shipments_prepared'):
                print(f"  Shipments prepared: {device.shipments_prepared}")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        logger.error(f"Error during cycle: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(run_complete_platelet_pooling_cycle())
