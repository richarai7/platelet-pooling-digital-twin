"""
SimPy-based Pooling Station simulator.
"""
import simpy
import random
from typing import Dict, Any, Tuple
from simpy_core.simpy_base import SimPyDeviceSimulator, BatchItem


class PoolingStation(SimPyDeviceSimulator):
    """Simulates platelet pooling from multiple donations."""
    
    def __init__(
        self,
        env: simpy.Environment,
        device_id: str = "pooling_station_01",
        capacity: int = 1,
        mean_pooling_time: float = 300.0,  # 5 minutes
        units_per_pool: int = 4,
        **kwargs
    ):
        super().__init__(
            env=env,
            device_id=device_id,
            device_type="pooling_station",
            capacity=capacity,
            mean_process_time=mean_pooling_time,
            **kwargs
        )
        self.units_per_pool = units_per_pool
        self.total_pools_created = 0
    
    def _perform_processing(self, batch: BatchItem) -> Tuple[float, Dict[str, Any]]:
        """Perform platelet pooling."""
        pooling_time = random.normalvariate(self.mean_process_time, 20.0)
        pooling_time = max(240.0, pooling_time)
        
        yield self.env.timeout(pooling_time)
        
        self.total_pools_created += 1
        
        # Calculate pooled volume
        total_volume = random.uniform(200, 250)  # mL per pool
        
        result = {
            'success': True,
            'device_id': self.device_id,
            'processing_time': pooling_time,
            'units_pooled': self.units_per_pool,
            'total_volume_ml': total_volume,
            'pooling_efficiency': random.uniform(0.92, 0.98)
        }
        
        batch.quality_metrics['pooled_volume'] = total_volume
        batch.quality_metrics['units_pooled'] = self.units_per_pool
        
        return pooling_time, result
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate pooling station telemetry."""
        base_telemetry = super().generate_telemetry()
        base_telemetry.update({
            'total_pools_created': self.total_pools_created,
            'units_per_pool': self.units_per_pool
        })
        return base_telemetry
