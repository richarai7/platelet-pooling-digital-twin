"""
SimPy-based Barcode Reader simulator.
"""
import simpy
import random
from typing import Dict, Any, Tuple
from simpy_core.simpy_base import SimPyDeviceSimulator, BatchItem


class BarcodeReader(SimPyDeviceSimulator):
    """Simulates final barcode verification before shipping."""
    
    def __init__(
        self,
        env: simpy.Environment,
        device_id: str = "barcode_reader_01",
        capacity: int = 1,
        mean_read_time: float = 8.0,  # 8 seconds
        **kwargs
    ):
        super().__init__(
            env=env,
            device_id=device_id,
            device_type="barcode_reader",
            capacity=capacity,
            mean_process_time=mean_read_time,
            **kwargs
        )
        self.successful_reads = 0
        self.failed_reads = 0
    
    def _perform_processing(self, batch: BatchItem) -> Tuple[float, Dict[str, Any]]:
        """Perform barcode reading and verification."""
        read_time = random.normalvariate(self.mean_process_time, 1.0)
        read_time = max(5.0, read_time)
        
        yield self.env.timeout(read_time)
        
        # 99.5% success rate
        read_success = random.random() > 0.005
        
        if read_success:
            self.successful_reads += 1
            result = {
                'success': True,
                'device_id': self.device_id,
                'processing_time': read_time,
                'barcode_verified': True,
                'product_id': f"PLT-{batch.batch_id}",
                'read_quality': random.uniform(0.90, 1.0)
            }
        else:
            self.failed_reads += 1
            result = {
                'success': False,
                'device_id': self.device_id,
                'processing_time': read_time,
                'error': 'Barcode read error',
                'retry_required': True
            }
        
        return read_time, result
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate barcode reader telemetry."""
        base_telemetry = super().generate_telemetry()
        base_telemetry.update({
            'successful_reads': self.successful_reads,
            'failed_reads': self.failed_reads,
            'read_success_rate': self.successful_reads / max(1, self.successful_reads + self.failed_reads)
        })
        return base_telemetry
