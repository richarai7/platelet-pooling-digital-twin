"""
SimPy-based Centrifuge simulator.

This device separates blood components through high-speed spinning,
critical for platelet extraction.
"""
import simpy
import random
from typing import Dict, Any, Tuple
from simpy_core.simpy_base import SimPyDeviceSimulator, BatchItem


class Centrifuge(SimPyDeviceSimulator):
    """
    Simulates a centrifuge for blood component separation.
    
    The centrifuge spins blood bags at high speed to separate components
    by density: red blood cells, platelets, and plasma.
    """
    
    def __init__(
        self,
        env: simpy.Environment,
        device_id: str = "centrifuge_01",
        capacity: int = 4,  # Can process 4 bags simultaneously
        mean_spin_time: float = 180.0,  # 3 minutes average
        target_rpm: int = 3500,
        **kwargs
    ):
        """
        Initialize the centrifuge.
        
        Args:
            env: SimPy environment
            device_id: Unique device identifier
            capacity: Number of bags that can be spun simultaneously
            mean_spin_time: Average centrifugation time in seconds
            target_rpm: Target revolutions per minute
            **kwargs: Additional arguments for base class
        """
        super().__init__(
            env=env,
            device_id=device_id,
            device_type="centrifuge",
            capacity=capacity,
            mean_process_time=mean_spin_time,
            **kwargs
        )
        self.target_rpm = target_rpm
        self.total_spin_time = 0.0
        self.current_rpm = 0
        self.temperature = 20.0  # Celsius
    
    def _perform_processing(self, batch: BatchItem) -> Tuple[float, Dict[str, Any]]:
        """
        Perform centrifugation operation.
        
        Args:
            batch: Batch item to centrifuge
            
        Yields:
            SimPy timeout for spin-up, processing, and spin-down
            
        Returns:
            Tuple of (processing_time, result_dict)
        """
        # Spin-up phase
        spinup_time = random.uniform(15, 25)
        yield self.env.timeout(spinup_time)
        self.current_rpm = self.target_rpm
        
        # Centrifugation phase
        spin_time = random.normalvariate(self.mean_process_time, 10.0)
        spin_time = max(120.0, min(240.0, spin_time))  # Between 2-4 minutes
        yield self.env.timeout(spin_time)
        
        # Temperature increase during spinning
        self.temperature = 20.0 + random.uniform(2, 5)
        
        # Spin-down phase
        spindown_time = random.uniform(20, 30)
        yield self.env.timeout(spindown_time)
        self.current_rpm = 0
        self.temperature = 20.0  # Cool down
        
        total_time = spinup_time + spin_time + spindown_time
        self.total_spin_time += total_time
        
        # Calculate separation quality
        separation_quality = random.uniform(0.90, 0.99)
        platelet_yield = random.uniform(0.85, 0.95)
        
        result = {
            'success': True,
            'device_id': self.device_id,
            'processing_time': total_time,
            'separation_quality': separation_quality,
            'platelet_yield': platelet_yield,
            'final_temperature': self.temperature,
            'max_rpm_achieved': self.target_rpm,
            'phases': {
                'spinup_time': spinup_time,
                'spin_time': spin_time,
                'spindown_time': spindown_time
            }
        }
        
        # Update batch quality metrics
        batch.quality_metrics['separation_quality'] = separation_quality
        batch.quality_metrics['platelet_yield'] = platelet_yield
        
        return total_time, result
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate centrifuge-specific telemetry."""
        base_telemetry = super().generate_telemetry()
        
        base_telemetry.update({
            'current_rpm': self.current_rpm,
            'target_rpm': self.target_rpm,
            'temperature_celsius': self.temperature,
            'total_spin_time': self.total_spin_time,
            'vibration_level': random.uniform(0.5, 2.0) if self.state.value == 'processing' else 0.1
        })
        
        return base_telemetry
