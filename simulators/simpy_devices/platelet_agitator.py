"""
SimPy-based Platelet Agitator simulator.
"""
import simpy
import random
from typing import Dict, Any, Tuple
from simpy_core.simpy_base import SimPyDeviceSimulator, BatchItem


class PlateletAgitator(SimPyDeviceSimulator):
    """Simulates continuous platelet agitation to maintain viability."""
    
    def __init__(
        self,
        env: simpy.Environment,
        device_id: str = "platelet_agitator_01",
        capacity: int = 8,  # Can hold multiple bags
        mean_agitation_time: float = 3600.0,  # 1 hour
        **kwargs
    ):
        super().__init__(
            env=env,
            device_id=device_id,
            device_type="platelet_agitator",
            capacity=capacity,
            mean_process_time=mean_agitation_time,
            **kwargs
        )
        self.agitation_speed_rpm = 60  # Gentle rocking
        self.temperature = 22.0  # Room temperature storage
    
    def _perform_processing(self, batch: BatchItem) -> Tuple[float, Dict[str, Any]]:
        """Perform platelet agitation."""
        agitation_time = random.normalvariate(self.mean_process_time, 180.0)
        agitation_time = max(3000.0, agitation_time)  # Minimum 50 minutes
        
        yield self.env.timeout(agitation_time)
        
        # Temperature fluctuations
        self.temperature = 22.0 + random.uniform(-0.5, 0.5)
        
        result = {
            'success': True,
            'device_id': self.device_id,
            'processing_time': agitation_time,
            'agitation_speed_rpm': self.agitation_speed_rpm,
            'temperature_celsius': self.temperature,
            'platelet_viability': random.uniform(0.92, 0.99)
        }
        
        batch.quality_metrics['platelet_viability'] = result['platelet_viability']
        
        return agitation_time, result
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate agitator telemetry."""
        base_telemetry = super().generate_telemetry()
        base_telemetry.update({
            'agitation_speed_rpm': self.agitation_speed_rpm,
            'temperature_celsius': self.temperature,
            'bags_on_agitator': self.resource.count
        })
        return base_telemetry
