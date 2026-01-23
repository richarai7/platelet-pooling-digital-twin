"""
SimPy-based Storage Refrigerator simulator.
"""
import simpy
import random
from typing import Dict, Any, Tuple
from simpy_core.simpy_base import SimPyDeviceSimulator, BatchItem


class StorageRefrigerator(SimPyDeviceSimulator):
    """Simulates temperature-controlled platelet storage."""
    
    def __init__(
        self,
        env: simpy.Environment,
        device_id: str = "storage_refrigerator_01",
        capacity: int = 20,  # Can store 20 products
        mean_storage_time: float = 7200.0,  # 2 hours before shipment
        target_temperature: float = 22.0,  # Celsius
        **kwargs
    ):
        super().__init__(
            env=env,
            device_id=device_id,
            device_type="storage_refrigerator",
            capacity=capacity,
            mean_process_time=mean_storage_time,
            **kwargs
        )
        self.target_temperature = target_temperature
        self.current_temperature = target_temperature
        self.humidity = 60.0  # Percent
    
    def _perform_processing(self, batch: BatchItem) -> Tuple[float, Dict[str, Any]]:
        """Perform temperature-controlled storage."""
        storage_time = random.normalvariate(self.mean_process_time, 600.0)
        storage_time = max(3600.0, storage_time)  # Minimum 1 hour
        
        # Monitor temperature during storage
        temp_variations = []
        check_interval = 300.0  # Check every 5 minutes
        remaining_time = storage_time
        
        while remaining_time > 0:
            interval = min(check_interval, remaining_time)
            yield self.env.timeout(interval)
            
            # Temperature fluctuation
            self.current_temperature = self.target_temperature + random.uniform(-0.5, 0.5)
            temp_variations.append(self.current_temperature)
            
            remaining_time -= interval
        
        avg_temperature = sum(temp_variations) / len(temp_variations)
        
        result = {
            'success': True,
            'device_id': self.device_id,
            'processing_time': storage_time,
            'avg_temperature': avg_temperature,
            'min_temperature': min(temp_variations),
            'max_temperature': max(temp_variations),
            'temperature_stable': max(temp_variations) - min(temp_variations) < 1.0,
            'humidity_percent': self.humidity
        }
        
        batch.quality_metrics['storage_temperature'] = avg_temperature
        
        return storage_time, result
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate storage refrigerator telemetry."""
        base_telemetry = super().generate_telemetry()
        base_telemetry.update({
            'current_temperature': self.current_temperature,
            'target_temperature': self.target_temperature,
            'humidity_percent': self.humidity,
            'products_stored': self.resource.count,
            'storage_capacity': self.resource.capacity
        })
        return base_telemetry
