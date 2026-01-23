"""
SimPy-based Macopress simulator.
"""
import simpy
import random
from typing import Dict, Any, Tuple
from simpy_core.simpy_base import SimPyDeviceSimulator, BatchItem


class Macopress(SimPyDeviceSimulator):
    """Simulates the Macopress device for platelet expression."""
    
    def __init__(
        self,
        env: simpy.Environment,
        device_id: str = "macopress_01",
        capacity: int = 1,
        mean_expression_time: float = 120.0,  # 2 minutes
        **kwargs
    ):
        super().__init__(
            env=env,
            device_id=device_id,
            device_type="macopress",
            capacity=capacity,
            mean_process_time=mean_expression_time,
            **kwargs
        )
        self.pressure_psi = 0.0
        self.total_platelet_volume = 0.0
    
    def _perform_processing(self, batch: BatchItem) -> Tuple[float, Dict[str, Any]]:
        """Perform platelet expression."""
        expression_time = random.normalvariate(self.mean_process_time, 8.0)
        expression_time = max(90.0, expression_time)
        
        # Apply pressure phase
        self.pressure_psi = random.uniform(8, 12)
        yield self.env.timeout(expression_time)
        
        platelet_volume = random.uniform(45, 65)  # mL
        self.total_platelet_volume += platelet_volume
        self.pressure_psi = 0.0
        
        result = {
            'success': True,
            'device_id': self.device_id,
            'processing_time': expression_time,
            'platelet_volume_ml': platelet_volume,
            'expression_pressure_psi': self.pressure_psi,
            'expression_efficiency': random.uniform(0.90, 0.98)
        }
        
        batch.quality_metrics['platelet_volume'] = platelet_volume
        
        return expression_time, result
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate Macopress telemetry."""
        base_telemetry = super().generate_telemetry()
        base_telemetry.update({
            'current_pressure_psi': self.pressure_psi,
            'total_platelet_volume_ml': self.total_platelet_volume
        })
        return base_telemetry
