"""
Blood Bag Scanner device simulator.

Simulates a barcode scanner used to identify and track blood bags
entering the platelet pooling process.
"""
from typing import Dict, Any
import random
from core.base_simulator import BaseDeviceSimulator


class BloodBagScannerSimulator(BaseDeviceSimulator):
    """
    Simulates a blood bag scanner for identification and tracking.
    
    The scanner reads barcodes on blood bags to track them through
    the pooling process and verify compatibility.
    """
    
    def __init__(self, device_id: str, telemetry_interval: int = 5):
        super().__init__(device_id, "blood_bag_scanner", telemetry_interval)
        
        # Device-specific parameters
        self.scan_success_rate = 0.98  # 98% success rate
        self.scan_time_seconds = 2
        self.scanner_temperature = 22.0  # Celsius
        self.laser_power = 100.0  # Percentage
        
        # Processing metrics
        self.scans_completed = 0
        self.scan_failures = 0
        self.total_runtime_hours = 0.0
        
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate scanner telemetry data."""
        # Simulate temperature fluctuation
        if self.is_processing:
            self.scanner_temperature = 22.0 + random.uniform(0, 1.5)
            self.laser_power = 100.0 + random.uniform(-2, 0)
        else:
            self.scanner_temperature = 22.0 + random.uniform(-0.5, 0.5)
            self.laser_power = 100.0
        
        telemetry = self.get_base_telemetry()
        telemetry.update({
            "scanner_temperature_celsius": round(self.scanner_temperature, 1),
            "laser_power_percent": round(self.laser_power, 1),
            "scan_success_rate": round(self.scan_success_rate * 100, 1),
            "scans_completed": self.scans_completed,
            "scan_failures": self.scan_failures,
            "total_runtime_hours": round(self.total_runtime_hours, 2)
        })
        
        return telemetry
    
    def start_processing(self, batch_id: str) -> bool:
        """Start scanning a batch."""
        if self.is_processing:
            self.logger.warning(f"Already processing batch {self.current_batch_id}")
            return False
        
        if self.error_state:
            self.logger.error(f"Cannot start processing: {self.error_state}")
            return False
        
        self.current_batch_id = batch_id
        self.is_processing = True
        self.state = "processing"
        
        self.logger.info(f"Started scanning batch {batch_id}")
        return True
    
    def complete_processing(self) -> Dict[str, Any]:
        """Complete the current scanning operation."""
        if not self.is_processing:
            self.logger.warning("No batch currently processing")
            return {}
        
        batch_id = self.current_batch_id
        
        # Simulate scan result
        scan_success = random.random() < self.scan_success_rate
        
        if scan_success:
            self.scans_completed += 1
        else:
            self.scan_failures += 1
        
        self.total_runtime_hours += self.scan_time_seconds / 3600.0
        
        result = {
            "batch_id": batch_id,
            "device_id": self.device_id,
            "process_type": "barcode_scan",
            "scan_time_seconds": self.scan_time_seconds,
            "success": scan_success,
            "barcode_data": {
                "donation_id": f"DON-{random.randint(100000, 999999)}",
                "blood_type": random.choice(["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]),
                "collection_date": "2026-01-20",
                "expiration_date": "2026-02-04"
            } if scan_success else None,
            "quality_metrics": {
                "barcode_quality": random.uniform(0.85, 1.0) if scan_success else 0.0,
                "read_confidence": random.uniform(0.90, 1.0) if scan_success else 0.0
            }
        }
        
        # Reset state
        self.is_processing = False
        self.current_batch_id = None
        self.state = "idle"
        
        self.logger.info(f"Completed scanning batch {batch_id}: {'Success' if scan_success else 'Failed'}")
        return result
    
    def simulate_fault(self, fault_type: str) -> None:
        """Simulate a device fault for testing."""
        fault_messages = {
            "laser_failure": "Laser power below threshold",
            "barcode_damaged": "Barcode unreadable",
            "connection_lost": "Connection to database lost",
            "calibration_error": "Scanner calibration required"
        }
        
        message = fault_messages.get(fault_type, "Unknown fault")
        self.set_error(message)
        self.is_processing = False
        self.laser_power = 0 if fault_type == "laser_failure" else self.laser_power
