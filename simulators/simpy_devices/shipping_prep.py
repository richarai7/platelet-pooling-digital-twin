"""
SimPy-based Shipping Prep simulator.
"""
import simpy
import random
from typing import Dict, Any, Tuple
from simpy_core.simpy_base import SimPyDeviceSimulator, BatchItem


class ShippingPrep(SimPyDeviceSimulator):
    """Simulates final packaging and documentation for shipping."""
    
    def __init__(
        self,
        env: simpy.Environment,
        device_id: str = "shipping_prep_01",
        capacity: int = 2,
        mean_prep_time: float = 180.0,  # 3 minutes
        **kwargs
    ):
        super().__init__(
            env=env,
            device_id=device_id,
            device_type="shipping_prep",
            capacity=capacity,
            mean_process_time=mean_prep_time,
            **kwargs
        )
        self.total_shipped = 0
        self.documentation_errors = 0
    
    def _perform_processing(self, batch: BatchItem) -> Tuple[float, Dict[str, Any]]:
        """Perform shipping preparation."""
        prep_time = random.normalvariate(self.mean_process_time, 15.0)
        prep_time = max(120.0, prep_time)
        
        yield self.env.timeout(prep_time)
        
        # Documentation completion
        documentation_complete = random.random() > 0.02  # 98% success
        
        if documentation_complete:
            self.total_shipped += 1
        else:
            self.documentation_errors += 1
        
        result = {
            'success': documentation_complete,
            'device_id': self.device_id,
            'processing_time': prep_time,
            'packaging_complete': True,
            'documentation_complete': documentation_complete,
            'shipping_label_applied': True,
            'ready_for_dispatch': documentation_complete
        }
        
        if documentation_complete:
            batch.end_time = self.env.now
        
        return prep_time, result
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate shipping prep telemetry."""
        base_telemetry = super().generate_telemetry()
        base_telemetry.update({
            'total_shipped': self.total_shipped,
            'documentation_errors': self.documentation_errors,
            'completion_rate': self.total_shipped / max(1, self.total_shipped + self.documentation_errors)
        })
        return base_telemetry
