"""
Macopress device simulator.

Simulates a Macopress used for expressing plasma from platelet-rich plasma bags.
"""
from typing import Dict, Any
import random
from core.base_simulator import BaseDeviceSimulator


class MacopressSimulator(BaseDeviceSimulator):
    """
    Simulates a Macopress device for plasma expression.
    
    The Macopress applies controlled pressure to blood bags to express
    plasma from platelet-rich plasma while preserving platelet quality.
    """
    
    def __init__(self, device_id: str, telemetry_interval: int = 5):
        super().__init__(device_id, "macopress", telemetry_interval)
        
        # Device-specific parameters
        self.target_pressure_psi = 15.0
        self.current_pressure_psi = 0.0
        self.expression_rate_ml_min = 0.0
        self.total_volume_expressed_ml = 0.0
        self.cycle_time_minutes = 8
        self.remaining_time_seconds = 0
        
        # Processing metrics
        self.cycles_completed = 0
        self.total_volume_processed_ml = 0.0
        
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate Macopress telemetry data."""
        if self.is_processing:
            # Simulate pressure application
            self.current_pressure_psi = self.target_pressure_psi + random.uniform(-0.5, 0.5)
            self.expression_rate_ml_min = 25.0 + random.uniform(-3, 3)
            
            # Accumulate volume
            volume_increment = (self.expression_rate_ml_min / 60) * self.telemetry_interval
            self.total_volume_expressed_ml += volume_increment
            
            if self.remaining_time_seconds > 0:
                self.remaining_time_seconds -= self.telemetry_interval
        else:
            self.current_pressure_psi = max(0, self.current_pressure_psi - 1.0)
            self.expression_rate_ml_min = 0.0
        
        telemetry = self.get_base_telemetry()
        telemetry.update({
            "pressure_psi": round(self.current_pressure_psi, 2),
            "target_pressure_psi": self.target_pressure_psi,
            "expression_rate_ml_min": round(self.expression_rate_ml_min, 1),
            "volume_expressed_ml": round(self.total_volume_expressed_ml, 1),
            "remaining_time_seconds": max(0, self.remaining_time_seconds),
            "cycles_completed": self.cycles_completed,
            "total_volume_processed_ml": round(self.total_volume_processed_ml, 1)
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
        self.total_volume_expressed_ml = 0.0
        
        self.logger.info(f"Started processing batch {batch_id}")
        return True
    
    def complete_processing(self) -> Dict[str, Any]:
        """Complete the current processing operation."""
        if not self.is_processing:
            self.logger.warning("No batch currently processing")
            return {}
        
        batch_id = self.current_batch_id
        self.cycles_completed += 1
        final_volume = self.total_volume_expressed_ml
        self.total_volume_processed_ml += final_volume
        
        result = {
            "batch_id": batch_id,
            "device_id": self.device_id,
            "process_type": "plasma_expression",
            "cycle_time_minutes": self.cycle_time_minutes,
            "volume_expressed_ml": round(final_volume, 1),
            "avg_pressure_psi": round(self.target_pressure_psi, 2),
            "success": True,
            "quality_metrics": {
                "expression_efficiency": random.uniform(0.90, 0.97),
                "platelet_preservation": random.uniform(0.93, 0.99)
            }
        }
        
        # Reset state
        self.is_processing = False
        self.current_batch_id = None
        self.state = "idle"
        self.remaining_time_seconds = 0
        self.total_volume_expressed_ml = 0.0
        
        self.logger.info(f"Completed processing batch {batch_id}")
        return result
    
    def simulate_fault(self, fault_type: str) -> None:
        """Simulate a device fault for testing."""
        fault_messages = {
            "overpressure": "Pressure exceeded safe limit",
            "leak": "Fluid leak detected",
            "blockage": "Expression pathway blocked",
            "sensor": "Pressure sensor malfunction"
        }
        
        message = fault_messages.get(fault_type, "Unknown fault")
        self.set_error(message)
        self.is_processing = False
        self.current_pressure_psi = 0
