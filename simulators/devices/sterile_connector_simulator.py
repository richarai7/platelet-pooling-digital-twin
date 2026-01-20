"""
Sterile Connector device simulator.

Simulates a sterile connection device used to join blood bags
while maintaining sterility.
"""
from typing import Dict, Any
import random
from core.base_simulator import BaseDeviceSimulator


class SterileConnectorSimulator(BaseDeviceSimulator):
    """
    Simulates a sterile connector device.
    
    Creates sealed, sterile connections between blood bags for
    pooling while preventing contamination.
    """
    
    def __init__(self, device_id: str, telemetry_interval: int = 5):
        super().__init__(device_id, "sterile_connector", telemetry_interval)
        
        # Device-specific parameters
        self.welding_temperature = 0.0  # Celsius
        self.target_weld_temp = 150.0
        self.weld_pressure = 0.0  # PSI
        self.target_weld_pressure = 25.0
        self.connection_time_seconds = 30
        self.remaining_time_seconds = 0
        
        # Processing metrics
        self.connections_completed = 0
        self.connection_failures = 0
        self.total_runtime_hours = 0.0
        
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate connector telemetry data."""
        # Simulate parameter changes during processing
        if self.is_processing:
            self.welding_temperature = self.target_weld_temp + random.uniform(-5, 5)
            self.weld_pressure = self.target_weld_pressure + random.uniform(-2, 2)
            if self.remaining_time_seconds > 0:
                self.remaining_time_seconds -= self.telemetry_interval
        else:
            self.welding_temperature = 25.0 + random.uniform(-1, 1)
            self.weld_pressure = 0
        
        telemetry = self.get_base_telemetry()
        telemetry.update({
            "welding_temperature_celsius": round(self.welding_temperature, 1),
            "weld_pressure_psi": round(self.weld_pressure, 1),
            "remaining_time_seconds": max(0, self.remaining_time_seconds),
            "connections_completed": self.connections_completed,
            "connection_failures": self.connection_failures,
            "success_rate": round((self.connections_completed / max(1, self.connections_completed + self.connection_failures)) * 100, 1),
            "total_runtime_hours": round(self.total_runtime_hours, 2)
        })
        
        return telemetry
    
    def start_processing(self, batch_id: str) -> bool:
        """Start processing a batch."""
        if self.is_processing:
            self.logger.warning(f"Already processing batch {self.current_batch_id}")
            return False
        
        if self.error_state:
            self.logger.error(f"Cannot start processing: {self.error_state}")
            return False
        
        self.current_batch_id = batch_id
        self.is_processing = True
        self.state = "processing"
        self.remaining_time_seconds = self.connection_time_seconds
        
        self.logger.info(f"Started processing batch {batch_id}")
        return True
    
    def complete_processing(self) -> Dict[str, Any]:
        """Complete the current processing operation."""
        if not self.is_processing:
            self.logger.warning("No batch currently processing")
            return {}
        
        batch_id = self.current_batch_id
        
        # Simulate connection success (very high success rate)
        connection_success = random.random() < 0.995
        
        if connection_success:
            self.connections_completed += 1
        else:
            self.connection_failures += 1
        
        self.total_runtime_hours += self.connection_time_seconds / 3600.0
        
        result = {
            "batch_id": batch_id,
            "device_id": self.device_id,
            "process_type": "sterile_connection",
            "connection_time_seconds": self.connection_time_seconds,
            "success": connection_success,
            "quality_metrics": {
                "weld_integrity": random.uniform(0.95, 1.0) if connection_success else 0.0,
                "sterility_maintained": connection_success,
                "leak_test_passed": connection_success
            }
        }
        
        # Reset state
        self.is_processing = False
        self.current_batch_id = None
        self.state = "idle"
        self.remaining_time_seconds = 0
        
        self.logger.info(f"Completed processing batch {batch_id}: {'Success' if connection_success else 'Failed'}")
        return result
    
    def simulate_fault(self, fault_type: str) -> None:
        """Simulate a device fault for testing."""
        fault_messages = {
            "temperature_error": "Welding temperature out of range",
            "pressure_error": "Weld pressure insufficient",
            "alignment_error": "Bag alignment error",
            "seal_failure": "Seal integrity compromised"
        }
        
        message = fault_messages.get(fault_type, "Unknown fault")
        self.set_error(message)
        self.is_processing = False
        self.welding_temperature = 25.0
        self.weld_pressure = 0
