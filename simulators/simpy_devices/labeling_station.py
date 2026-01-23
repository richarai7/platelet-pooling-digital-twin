"""
SimPy-based Labeling Station simulator.
"""
import simpy
import random
from typing import Dict, Any, Tuple
from simpy_core.simpy_base import SimPyDeviceSimulator, BatchItem


class LabelingStation(SimPyDeviceSimulator):
    """Simulates automated product labeling."""
    
    def __init__(
        self,
        env: simpy.Environment,
        device_id: str = "labeling_station_01",
        capacity: int = 1,
        mean_labeling_time: float = 60.0,  # 1 minute
        **kwargs
    ):
        super().__init__(
            env=env,
            device_id=device_id,
            device_type="labeling_station",
            capacity=capacity,
            mean_process_time=mean_labeling_time,
            **kwargs
        )
        self.labels_printed = 0
    
    def _perform_processing(self, batch: BatchItem) -> Tuple[float, Dict[str, Any]]:
        """Perform product labeling."""
        labeling_time = random.normalvariate(self.mean_process_time, 5.0)
        labeling_time = max(45.0, labeling_time)
        
        yield self.env.timeout(labeling_time)
        
        self.labels_printed += 1
        
        # Generate expiration date (5 days from now)
        expiration_hours = 120 + self.env.now / 3600
        
        result = {
            'success': True,
            'device_id': self.device_id,
            'processing_time': labeling_time,
            'label_printed': True,
            'product_code': f"PLT-{batch.batch_id}",
            'expiration_hours': expiration_hours,
            'label_quality': random.uniform(0.95, 1.0)
        }
        
        return labeling_time, result
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate labeling station telemetry."""
        base_telemetry = super().generate_telemetry()
        base_telemetry.update({
            'labels_printed': self.labels_printed,
            'printer_status': 'ready' if self.state.value == 'idle' else 'printing'
        })
        return base_telemetry
