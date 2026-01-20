"""
Barcode Reader device simulator.

Simulates a final verification barcode reader that scans products
before shipping to ensure tracking and traceability.
"""
from typing import Dict, Any
import random
from datetime import datetime
from core.base_simulator import BaseDeviceSimulator


class BarcodeReaderSimulator(BaseDeviceSimulator):
    """
    Simulates a barcode reader for final product verification.
    
    Scans product barcodes to verify identity, expiration, and
    readiness for shipping while maintaining audit trail.
    """
    
    def __init__(self, device_id: str, telemetry_interval: int = 5):
        super().__init__(device_id, "barcode_reader", telemetry_interval)
        
        # Device-specific parameters
        self.scan_in_progress = False
        self.laser_power_mw = 1.0  # milliwatts
        self.scan_success_rate = 0.99
        self.scan_time_seconds = 1.5
        self.remaining_time_seconds = 0
        
        # Last scanned data
        self.last_barcode = ""
        self.last_scan_quality = 0.0
        self.verification_status = "pending"
        
        # Processing metrics
        self.total_scans = 0
        self.successful_scans = 0
        self.failed_scans = 0
        self.verification_failures = 0
        self.total_runtime_hours = 0.0
        
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate barcode reader telemetry data."""
        # Simulate parameter changes during processing
        if self.is_processing:
            self.laser_power_mw = 1.0 + random.uniform(-0.1, 0.1)
            progress = 1 - (self.remaining_time_seconds / self.scan_time_seconds)
            
            if progress > 0.5:
                # Scan is being processed
                self.last_scan_quality = random.uniform(0.85, 1.0)
            
            if self.remaining_time_seconds > 0:
                self.remaining_time_seconds -= self.telemetry_interval
        else:
            self.laser_power_mw = 1.0
            self.last_scan_quality = 0.0
        
        telemetry = self.get_base_telemetry()
        telemetry.update({
            "laser_power_mw": round(self.laser_power_mw, 2),
            "scan_in_progress": self.is_processing,
            "last_barcode": self.last_barcode,
            "last_scan_quality": round(self.last_scan_quality, 3),
            "verification_status": self.verification_status,
            "remaining_time_seconds": max(0, self.remaining_time_seconds),
            "total_scans": self.total_scans,
            "successful_scans": self.successful_scans,
            "failed_scans": self.failed_scans,
            "verification_failures": self.verification_failures,
            "success_rate": round((self.successful_scans / max(1, self.total_scans)) * 100, 1),
            "total_runtime_hours": round(self.total_runtime_hours, 2)
        })
        
        return telemetry
    
    def start_processing(self, batch_id: str) -> bool:
        """Start processing (scanning) a batch."""
        if self.is_processing:
            self.logger.warning(f"Already processing batch {self.current_batch_id}")
            return False
        
        if self.error_state:
            self.logger.error(f"Cannot start processing: {self.error_state}")
            return False
        
        self.current_batch_id = batch_id
        self.is_processing = True
        self.state = "processing"
        self.remaining_time_seconds = self.scan_time_seconds
        self.verification_status = "scanning"
        
        self.logger.info(f"Started processing batch {batch_id}")
        return True
    
    def complete_processing(self) -> Dict[str, Any]:
        """Complete the current processing operation."""
        if not self.is_processing:
            self.logger.warning("No batch currently processing")
            return {}
        
        batch_id = self.current_batch_id
        self.total_scans += 1
        
        # Simulate scan success
        scan_success = random.random() < self.scan_success_rate
        
        if scan_success:
            self.successful_scans += 1
            # Generate barcode data
            self.last_barcode = f"{random.randint(100000000, 999999999)}"
            self.last_scan_quality = random.uniform(0.90, 1.0)
            
            # Verify product data (check expiration, quality, etc.)
            verification_passed = random.random() < 0.99
            
            if verification_passed:
                self.verification_status = "verified"
            else:
                self.verification_status = "failed"
                self.verification_failures += 1
        else:
            self.failed_scans += 1
            self.last_barcode = ""
            self.last_scan_quality = 0.0
            self.verification_status = "scan_failed"
        
        self.total_runtime_hours += self.scan_time_seconds / 3600.0
        
        result = {
            "batch_id": batch_id,
            "device_id": self.device_id,
            "process_type": "barcode_verification",
            "scan_time_seconds": self.scan_time_seconds,
            "success": scan_success and self.verification_status == "verified",
            "barcode_data": {
                "barcode": self.last_barcode if scan_success else None,
                "product_id": f"PLT-{batch_id}" if scan_success else None,
                "scan_timestamp": datetime.now().isoformat(),
                "verification_status": self.verification_status
            },
            "quality_metrics": {
                "scan_quality": round(self.last_scan_quality, 3),
                "barcode_readable": scan_success,
                "data_valid": self.verification_status == "verified"
            }
        }
        
        # Reset state
        self.is_processing = False
        self.current_batch_id = None
        self.state = "idle"
        self.remaining_time_seconds = 0
        
        self.logger.info(f"Completed processing batch {batch_id}: {self.verification_status}")
        return result
    
    def simulate_fault(self, fault_type: str) -> None:
        """Simulate a device fault for testing."""
        fault_messages = {
            "laser_failure": "Laser module failure",
            "calibration_error": "Scanner calibration error",
            "communication_error": "Database connection lost",
            "lens_dirty": "Scanner lens requires cleaning"
        }
        
        message = fault_messages.get(fault_type, "Unknown fault")
        self.set_error(message)
        self.is_processing = False
        self.verification_status = "error"
