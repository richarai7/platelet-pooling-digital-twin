"""
SimPy-based Plasma Extractor simulator.
"""
import simpy
import random
from typing import Dict, Any, Tuple
from simpy_core.simpy_base import SimPyDeviceSimulator, BatchItem


class PlasmaExtractor(SimPyDeviceSimulator):
    """Simulates plasma extraction from centrifuged blood."""
    
    def __init__(
        self,
        env: simpy.Environment,
        device_id: str = "plasma_extractor_01",
        capacity: int = 2,
        mean_extraction_time: float = 90.0,  # 1.5 minutes
        **kwargs
    ):
        super().__init__(
            env=env,
            device_id=device_id,
            device_type="plasma_extractor",
            capacity=capacity,
            mean_process_time=mean_extraction_time,
            **kwargs
        )
        self.total_plasma_extracted = 0.0  # mL
    
    def _perform_processing(self, batch: BatchItem) -> Tuple[float, Dict[str, Any]]:
        """Perform plasma extraction."""
        extraction_time = random.normalvariate(self.mean_process_time, 5.0)
        extraction_time = max(60.0, extraction_time)
        
        yield self.env.timeout(extraction_time)
        
        # Extract plasma volume
        plasma_volume = random.uniform(200, 280)  # mL
        self.total_plasma_extracted += plasma_volume
        
        result = {
            'success': True,
            'device_id': self.device_id,
            'processing_time': extraction_time,
            'plasma_extracted_ml': plasma_volume,
            'extraction_efficiency': random.uniform(0.88, 0.96)
        }
        
        batch.quality_metrics['plasma_volume'] = plasma_volume
        
        return extraction_time, result
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate plasma extractor telemetry."""
        base_telemetry = super().generate_telemetry()
        base_telemetry.update({
            'total_plasma_extracted_ml': self.total_plasma_extracted,
            'extraction_rate_ml_per_min': random.uniform(180, 220) if self.state.value == 'processing' else 0
        })
        return base_telemetry
