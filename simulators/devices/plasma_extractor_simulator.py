"""
Plasma Extractor device simulator.

Simulates a plasma extraction device that separates plasma from
platelet concentrate after centrifugation.
"""
from typing import Dict, Any
import random
from core.base_simulator import BaseDeviceSimulator


class PlasmaExtractorSimulator(BaseDeviceSimulator):
    """
    Simulates a plasma extractor device.
    
    Extracts excess plasma from platelet concentrate to achieve
    the correct platelet concentration.
    """
    
    def __init__(self, device_id: str, telemetry_interval: int = 5):
        super().__init__(device_id, "plasma_extractor", telemetry_interval)
        
        # Device-specific parameters
        self.extraction_pressure = 0.0  # PSI
        self.target_pressure = 15.0
        self.flow_rate = 0.0  # mL/min
        self.target_flow_rate = 50.0
        self.temperature = 22.0  # Celsius
        self.cycle_time_minutes = 8
        self.remaining_time_seconds = 0
        
        # Processing metrics
        self.cycles_completed = 0
        self.total_volume_extracted_ml = 0.0
        self.total_runtime_hours = 0.0
        
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate extractor telemetry data."""
        # Simulate parameter changes during processing
        if self.is_processing:
            self.extraction_pressure = self.target_pressure + random.uniform(-1, 1)
            self.flow_rate = self.target_flow_rate + random.uniform(-5, 5)
            self.temperature = 22.0 + random.uniform(0, 2.0)
            if self.remaining_time_seconds > 0:
                self.remaining_time_seconds -= self.telemetry_interval
        else:
            self.extraction_pressure = 0
            self.flow_rate = 0
            self.temperature = 22.0 + random.uniform(-0.5, 0.5)
        
        telemetry = self.get_base_telemetry()
        telemetry.update({
            "extraction_pressure_psi": round(self.extraction_pressure, 1),
            "target_pressure_psi": self.target_pressure,
            "flow_rate_ml_min": round(self.flow_rate, 1),
            "temperature_celsius": round(self.temperature, 1),
            "remaining_time_seconds": max(0, self.remaining_time_seconds),
            "cycles_completed": self.cycles_completed,
            "total_volume_extracted_ml": round(self.total_volume_extracted_ml, 1),
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
        
        # Simulate extraction volume
        volume_extracted = random.uniform(180, 220)  # mL
        self.total_volume_extracted_ml += volume_extracted
        self.total_runtime_hours += self.cycle_time_minutes / 60.0
        
        result = {
            "batch_id": batch_id,
            "device_id": self.device_id,
            "process_type": "plasma_extraction",
            "cycle_time_minutes": self.cycle_time_minutes,
            "volume_extracted_ml": round(volume_extracted, 1),
            "avg_flow_rate": round(self.target_flow_rate, 1),
            "success": True,
            "quality_metrics": {
                "extraction_efficiency": random.uniform(0.92, 0.98),
                "platelet_loss": random.uniform(0.02, 0.05),  # Loss during extraction
                "final_concentration": random.uniform(1.0, 1.2)  # 10^6 platelets/µL
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
            "pressure_leak": "Pressure leak detected",
            "flow_blockage": "Flow blockage detected",
            "temperature_high": "Temperature exceeds safe limit",
            "sensor_error": "Pressure sensor malfunction"
        }
        
        message = fault_messages.get(fault_type, "Unknown fault")
        self.set_error(message)
        self.is_processing = False
        self.extraction_pressure = 0
        self.flow_rate = 0
