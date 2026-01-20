"""
Pooling Station device simulator.

Simulates a pooling station where platelet units from multiple donors
are combined into a single pooled product.
"""
from typing import Dict, Any
import random
from core.base_simulator import BaseDeviceSimulator


class PoolingStationSimulator(BaseDeviceSimulator):
    """
    Simulates a pooling station device.
    
    Combines multiple platelet units into a pooled product while
    monitoring volume and maintaining sterility.
    """
    
    def __init__(self, device_id: str, telemetry_interval: int = 5):
        super().__init__(device_id, "pooling_station", telemetry_interval)
        
        # Device-specific parameters
        self.current_volume_ml = 0.0
        self.target_volume_ml = 300.0  # Target pool volume
        self.units_pooled = 0
        self.target_units = 4  # Pool 4 units
        self.mixing_speed_rpm = 0
        self.target_mixing_rpm = 40
        self.temperature = 22.0  # Celsius
        self.cycle_time_minutes = 12
        self.remaining_time_seconds = 0
        
        # Processing metrics
        self.pools_completed = 0
        self.total_volume_pooled_ml = 0.0
        self.total_runtime_hours = 0.0
        
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate pooling station telemetry data."""
        # Simulate parameter changes during processing
        if self.is_processing:
            # Volume increases as units are added
            progress = 1 - (self.remaining_time_seconds / (self.cycle_time_minutes * 60))
            self.current_volume_ml = self.target_volume_ml * progress
            self.units_pooled = int(self.target_units * progress)
            self.mixing_speed_rpm = self.target_mixing_rpm + random.uniform(-3, 3)
            self.temperature = 22.0 + random.uniform(0, 1.5)
            if self.remaining_time_seconds > 0:
                self.remaining_time_seconds -= self.telemetry_interval
        else:
            self.current_volume_ml = 0
            self.units_pooled = 0
            self.mixing_speed_rpm = 0
            self.temperature = 22.0 + random.uniform(-0.5, 0.5)
        
        telemetry = self.get_base_telemetry()
        telemetry.update({
            "current_volume_ml": round(self.current_volume_ml, 1),
            "target_volume_ml": self.target_volume_ml,
            "units_pooled": self.units_pooled,
            "target_units": self.target_units,
            "mixing_speed_rpm": round(self.mixing_speed_rpm, 1),
            "temperature_celsius": round(self.temperature, 1),
            "remaining_time_seconds": max(0, self.remaining_time_seconds),
            "pools_completed": self.pools_completed,
            "total_volume_pooled_ml": round(self.total_volume_pooled_ml, 1),
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
        self.pools_completed += 1
        
        # Simulate final pool volume
        final_volume = self.target_volume_ml + random.uniform(-10, 10)
        self.total_volume_pooled_ml += final_volume
        self.total_runtime_hours += self.cycle_time_minutes / 60.0
        
        result = {
            "batch_id": batch_id,
            "device_id": self.device_id,
            "process_type": "platelet_pooling",
            "cycle_time_minutes": self.cycle_time_minutes,
            "units_pooled": self.target_units,
            "final_volume_ml": round(final_volume, 1),
            "success": True,
            "quality_metrics": {
                "platelet_concentration": random.uniform(0.9, 1.2),  # 10^6/µL
                "mixing_uniformity": random.uniform(0.92, 0.99),
                "volume_accuracy": 1 - abs(final_volume - self.target_volume_ml) / self.target_volume_ml,
                "contamination_test": random.random() < 0.999  # Very low contamination rate
            }
        }
        
        # Reset state
        self.is_processing = False
        self.current_batch_id = None
        self.state = "idle"
        self.remaining_time_seconds = 0
        self.current_volume_ml = 0
        self.units_pooled = 0
        
        self.logger.info(f"Completed processing batch {batch_id}")
        return result
    
    def simulate_fault(self, fault_type: str) -> None:
        """Simulate a device fault for testing."""
        fault_messages = {
            "volume_error": "Volume measurement error",
            "mixing_failure": "Mixer motor malfunction",
            "contamination": "Contamination detected",
            "seal_breach": "Sterile seal compromised"
        }
        
        message = fault_messages.get(fault_type, "Unknown fault")
        self.set_error(message)
        self.is_processing = False
        self.mixing_speed_rpm = 0
