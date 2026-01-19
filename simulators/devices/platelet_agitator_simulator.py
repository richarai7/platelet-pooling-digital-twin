"""
Platelet Agitator device simulator.

Simulates a platelet agitator used to maintain platelet viability during storage.
"""
from typing import Dict, Any
import random
from core.base_simulator import BaseDeviceSimulator


class PlateletAgitatorSimulator(BaseDeviceSimulator):
    """
    Simulates a platelet agitator for maintaining platelet quality during storage.
    
    The agitator provides continuous gentle agitation to prevent platelet
    aggregation and maintain optimal gas exchange during storage.
    """
    
    def __init__(self, device_id: str, telemetry_interval: int = 5):
        super().__init__(device_id, "platelet_agitator", telemetry_interval)
        
        # Device-specific parameters
        self.target_rpm = 60
        self.current_rpm = 0
        self.temperature = 22.0  # Celsius (room temperature storage)
        self.humidity = 45.0  # Percent
        self.current_bag_count = 0
        self.max_bag_capacity = 24
        
        # Storage duration tracking
        self.storage_start_time = None
        self.storage_duration_hours = 0.0
        
        # Processing metrics
        self.total_bags_processed = 0
        self.total_runtime_hours = 0.0
        
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate platelet agitator telemetry data."""
        if self.is_processing:
            # Maintain steady agitation
            self.current_rpm = self.target_rpm + random.uniform(-2, 2)
            self.temperature = 22.0 + random.uniform(-1.0, 1.0)
            self.humidity = 45.0 + random.uniform(-5, 5)
            
            # Track storage time
            self.storage_duration_hours += (self.telemetry_interval / 3600.0)
            self.total_runtime_hours += (self.telemetry_interval / 3600.0)
        else:
            self.current_rpm = 0
            self.temperature = 22.0 + random.uniform(-0.5, 0.5)
        
        telemetry = self.get_base_telemetry()
        telemetry.update({
            "rpm": round(self.current_rpm, 1),
            "target_rpm": self.target_rpm,
            "temperature_celsius": round(self.temperature, 1),
            "humidity_percent": round(self.humidity, 1),
            "current_bag_count": self.current_bag_count,
            "max_capacity": self.max_bag_capacity,
            "utilization_percent": round((self.current_bag_count / self.max_bag_capacity) * 100, 1),
            "storage_duration_hours": round(self.storage_duration_hours, 2),
            "total_bags_processed": self.total_bags_processed,
            "total_runtime_hours": round(self.total_runtime_hours, 2)
        })
        
        return telemetry
    
    def start_processing(self, batch_id: str, bag_count: int = 1) -> bool:
        """
        Start agitation for a batch of platelet bags.
        
        Args:
            batch_id: Unique identifier for the batch
            bag_count: Number of bags in this batch
        """
        if self.error_state:
            self.logger.error(f"Cannot start processing: {self.error_state}")
            return False
        
        if self.current_bag_count + bag_count > self.max_bag_capacity:
            self.logger.error(f"Insufficient capacity: {self.max_bag_capacity - self.current_bag_count} slots available")
            return False
        
        self.current_batch_id = batch_id
        self.is_processing = True
        self.state = "processing"
        self.current_bag_count += bag_count
        self.storage_duration_hours = 0.0
        
        self.logger.info(f"Started agitation for batch {batch_id} ({bag_count} bags)")
        return True
    
    def complete_processing(self, bag_count: int = None) -> Dict[str, Any]:
        """
        Complete agitation and remove bags.
        
        Args:
            bag_count: Number of bags to remove (None = remove all)
        """
        if not self.is_processing:
            self.logger.warning("No batch currently processing")
            return {}
        
        bags_removed = bag_count if bag_count is not None else self.current_bag_count
        bags_removed = min(bags_removed, self.current_bag_count)
        
        batch_id = self.current_batch_id
        storage_hours = self.storage_duration_hours
        
        result = {
            "batch_id": batch_id,
            "device_id": self.device_id,
            "process_type": "platelet_agitation",
            "bags_processed": bags_removed,
            "storage_duration_hours": round(storage_hours, 2),
            "avg_temperature_celsius": round(self.temperature, 1),
            "success": True,
            "quality_metrics": {
                "platelet_viability": random.uniform(0.94, 0.99),
                "ph_stability": random.uniform(0.95, 0.99),
                "swirling_score": random.uniform(0.90, 0.98)
            }
        }
        
        # Update state
        self.current_bag_count -= bags_removed
        self.total_bags_processed += bags_removed
        
        if self.current_bag_count == 0:
            self.is_processing = False
            self.current_batch_id = None
            self.state = "idle"
            self.storage_duration_hours = 0.0
        
        self.logger.info(f"Removed {bags_removed} bags from batch {batch_id}")
        return result
    
    def simulate_fault(self, fault_type: str) -> None:
        """Simulate a device fault for testing."""
        fault_messages = {
            "motor": "Agitation motor failure",
            "temperature": "Temperature control malfunction",
            "sensor": "Environmental sensor error",
            "overload": "Bag capacity overload detected"
        }
        
        message = fault_messages.get(fault_type, "Unknown fault")
        self.set_error(message)
        self.current_rpm = 0
