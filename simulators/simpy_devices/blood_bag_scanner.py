"""
SimPy-based Blood Bag Scanner simulator.

This device performs barcode scanning and initial tracking of blood bags
entering the platelet pooling process.
"""
import simpy
import random
from typing import Dict, Any, Tuple
from simpy_core.simpy_base import SimPyDeviceSimulator, BatchItem


class BloodBagScanner(SimPyDeviceSimulator):
    """
    Simulates a blood bag scanner for initial batch tracking.
    
    The scanner reads barcodes, validates donation IDs, and initiates
    batch tracking in the system.
    """
    
    def __init__(
        self,
        env: simpy.Environment,
        device_id: str = "blood_bag_scanner_01",
        capacity: int = 1,
        mean_scan_time: float = 5.0,  # Average time to scan one bag (seconds)
        scan_error_rate: float = 0.01,  # 1% scan error rate
        **kwargs
    ):
        """
        Initialize the blood bag scanner.
        
        Args:
            env: SimPy environment
            device_id: Unique device identifier
            capacity: Number of simultaneous scan operations
            mean_scan_time: Average scanning time in seconds
            scan_error_rate: Probability of scan error (0.0 to 1.0)
            **kwargs: Additional arguments for base class
        """
        super().__init__(
            env=env,
            device_id=device_id,
            device_type="blood_bag_scanner",
            capacity=capacity,
            mean_process_time=mean_scan_time,
            **kwargs
        )
        self.scan_error_rate = scan_error_rate
        self.successful_scans = 0
        self.failed_scans = 0
    
    def _perform_processing(self, batch: BatchItem) -> Tuple[float, Dict[str, Any]]:
        """
        Perform barcode scanning operation.
        
        Args:
            batch: Batch item to scan
            
        Yields:
            SimPy timeout for scan duration
            
        Returns:
            Tuple of (processing_time, result_dict)
        """
        # Simulate scanning time with some variation
        scan_time = random.normalvariate(self.mean_process_time, self.mean_process_time * 0.1)
        scan_time = max(1.0, scan_time)  # Minimum 1 second
        
        yield self.env.timeout(scan_time)
        
        # Determine if scan succeeds
        scan_success = random.random() > self.scan_error_rate
        
        if scan_success:
            self.successful_scans += 1
            result = {
                'success': True,
                'device_id': self.device_id,
                'processing_time': scan_time,
                'barcode': batch.batch_id,
                'scan_quality': random.uniform(0.85, 1.0),
                'donation_verified': True
            }
        else:
            self.failed_scans += 1
            result = {
                'success': False,
                'device_id': self.device_id,
                'processing_time': scan_time,
                'error': 'Barcode read error',
                'retry_required': True
            }
        
        return scan_time, result
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate scanner-specific telemetry."""
        base_telemetry = super().generate_telemetry()
        
        base_telemetry.update({
            'successful_scans': self.successful_scans,
            'failed_scans': self.failed_scans,
            'scan_success_rate': (
                self.successful_scans / max(1, self.successful_scans + self.failed_scans)
            )
        })
        
        return base_telemetry
