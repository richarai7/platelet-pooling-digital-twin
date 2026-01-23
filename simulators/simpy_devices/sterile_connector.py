"""
SimPy-based Sterile Connector simulator.
"""
import simpy
import random
from typing import Dict, Any, Tuple
from simpy_core.simpy_base import SimPyDeviceSimulator, BatchItem


class SterileConnector(SimPyDeviceSimulator):
    """Simulates sterile bag connection for pooling."""
    
    def __init__(
        self,
        env: simpy.Environment,
        device_id: str = "sterile_connector_01",
        capacity: int = 1,
        mean_connection_time: float = 45.0,  # 45 seconds
        **kwargs
    ):
        super().__init__(
            env=env,
            device_id=device_id,
            device_type="sterile_connector",
            capacity=capacity,
            mean_process_time=mean_connection_time,
            **kwargs
        )
        self.successful_connections = 0
        self.failed_connections = 0
    
    def _perform_processing(self, batch: BatchItem) -> Tuple[float, Dict[str, Any]]:
        """Perform sterile connection."""
        connection_time = random.normalvariate(self.mean_process_time, 5.0)
        connection_time = max(30.0, connection_time)
        
        yield self.env.timeout(connection_time)
        
        # 99% success rate for sterile connections
        connection_success = random.random() > 0.01
        
        if connection_success:
            self.successful_connections += 1
            result = {
                'success': True,
                'device_id': self.device_id,
                'processing_time': connection_time,
                'sterility_verified': True,
                'connection_quality': random.uniform(0.95, 1.0)
            }
        else:
            self.failed_connections += 1
            result = {
                'success': False,
                'device_id': self.device_id,
                'processing_time': connection_time,
                'error': 'Connection failed - sterility compromised'
            }
        
        return connection_time, result
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate sterile connector telemetry."""
        base_telemetry = super().generate_telemetry()
        base_telemetry.update({
            'successful_connections': self.successful_connections,
            'failed_connections': self.failed_connections,
            'success_rate': self.successful_connections / max(1, self.successful_connections + self.failed_connections)
        })
        return base_telemetry
