"""
Centrifuge device simulator.

Simulates a centrifuge used in the platelet pooling process for
separating blood components.
"""
from typing import Dict, Any
import random
from core.base_simulator import BaseDeviceSimulator


class CentrifugeSimulator(BaseDeviceSimulator):
    """
    Simulates a centrifuge device for blood component separation.
    
    The centrifuge spins blood samples at high speeds to separate
    components by density (platelets, plasma, red blood cells).
    """
    
    def __init__(self, device_id: str, telemetry_interval: int = 5):
        super().__init__(device_id, "centrifuge", telemetry_interval)
        
        # Device-specific parameters
        self.target_rpm = 3000
        self.current_rpm = 0
        self.temperature = 22.0  # Celsius
        self.cycle_time_minutes = 15
        self.remaining_time_seconds = 0
        self.vibration_level = 0.0  # mm/s
        
        # Processing metrics
        self.cycles_completed = 0
        self.total_runtime_hours = 0.0
        
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate centrifuge telemetry data."""
        # Simulate RPM changes during processing
        if self.is_processing:
            self.current_rpm = self.target_rpm + random.uniform(-50, 50)
            self.vibration_level = random.uniform(0.5, 2.0)
            self.temperature = 22.0 + random.uniform(0, 3.0)
            if self.remaining_time_seconds > 0:
                self.remaining_time_seconds -= self.telemetry_interval
        else:
            self.current_rpm = max(0, self.current_rpm - 100)  # Spin down
            self.vibration_level = random.uniform(0, 0.3)
            self.temperature = 22.0 + random.uniform(-0.5, 0.5)
        
        telemetry = self.get_base_telemetry()
        telemetry.update({
            "rpm": round(self.current_rpm, 1),
            "target_rpm": self.target_rpm,
            "temperature_celsius": round(self.temperature, 1),
            "vibration_mm_s": round(self.vibration_level, 2),
            "remaining_time_seconds": max(0, self.remaining_time_seconds),
            "cycles_completed": self.cycles_completed,
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
        self.remaining_time_seconds = self.cycle_time_minutes * 60
        
        self.logger.info(f"Started processing batch {batch_id}")
        return True
    
    def complete_processing(self) -> Dict[str, Any]:
        """Complete the current processing operation."""
        if not self.is_processing:
            self.logger.warning("No batch currently processing")
            return {}
        
        batch_id = self.current_batch_id
        self.cycles_completed += 1
        self.total_runtime_hours += self.cycle_time_minutes / 60.0
        
        result = {
            "batch_id": batch_id,
            "device_id": self.device_id,
            "process_type": "centrifugation",
            "cycle_time_minutes": self.cycle_time_minutes,
            "avg_rpm": round(self.target_rpm, 1),
            "success": True,
            "quality_metrics": {
                "separation_quality": random.uniform(0.92, 0.98),
                "platelet_yield": random.uniform(0.88, 0.95)
            }
        }
        
        # Reset state
        self.is_processing = False
        self.current_batch_id = None
        self.state = "idle"
        self.remaining_time_seconds = 0
        
        self.logger.info(f"Completed processing batch {batch_id}")
        return result
    
    def simulate_fault(self, fault_type: str) -> None:
        """Simulate a device fault for testing."""
        fault_messages = {
            "overspeed": "RPM exceeded safe limit",
            "temperature": "Temperature too high",
            "vibration": "Excessive vibration detected",
            "imbalance": "Load imbalance detected"
        }
        
        message = fault_messages.get(fault_type, "Unknown fault")
        self.set_error(message)
        self.is_processing = False
        self.current_rpm = 0
