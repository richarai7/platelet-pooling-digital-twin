"""
Storage Refrigerator device simulator.

Simulates a controlled temperature storage unit for platelet products
maintaining 20-24°C with agitation.
"""
from typing import Dict, Any, List
import random
from core.base_simulator import BaseDeviceSimulator


class StorageRefrigeratorSimulator(BaseDeviceSimulator):
    """
    Simulates a storage refrigerator for platelet products.
    
    Maintains constant agitation and temperature control for
    platelet products during storage period.
    """
    
    def __init__(self, device_id: str, telemetry_interval: int = 5):
        super().__init__(device_id, "storage_refrigerator", telemetry_interval)
        
        # Device-specific parameters
        self.internal_temperature = 22.0  # Celsius
        self.target_temperature = 22.0
        self.temperature_min = 20.0
        self.temperature_max = 24.0
        self.agitation_speed_rpm = 60
        self.target_agitation_rpm = 60
        self.humidity_percent = 60.0
        
        # Storage capacity
        self.max_capacity = 50
        self.current_inventory_count = 0
        self.stored_batches: List[str] = []
        
        # Environmental monitoring
        self.door_open = False
        self.alarm_active = False
        
        # Processing metrics
        self.total_units_stored = 0
        self.temperature_excursions = 0
        self.total_runtime_hours = 0.0
        
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate storage refrigerator telemetry data."""
        # Simulate parameter changes
        if not self.door_open:
            # Normal temperature fluctuation
            self.internal_temperature = self.target_temperature + random.uniform(-0.5, 0.5)
        else:
            # Temperature rises when door is open
            self.internal_temperature += 0.1
        
        # Check for temperature excursions
        if self.internal_temperature < self.temperature_min or self.internal_temperature > self.temperature_max:
            self.alarm_active = True
        else:
            self.alarm_active = False
        
        # Agitation continues during storage
        self.agitation_speed_rpm = self.target_agitation_rpm + random.uniform(-2, 2)
        self.humidity_percent = 60.0 + random.uniform(-5, 5)
        
        telemetry = self.get_base_telemetry()
        telemetry.update({
            "internal_temperature_celsius": round(self.internal_temperature, 1),
            "target_temperature_celsius": self.target_temperature,
            "temperature_min_celsius": self.temperature_min,
            "temperature_max_celsius": self.temperature_max,
            "agitation_speed_rpm": round(self.agitation_speed_rpm, 1),
            "humidity_percent": round(self.humidity_percent, 1),
            "current_inventory_count": self.current_inventory_count,
            "max_capacity": self.max_capacity,
            "capacity_utilization_percent": round((self.current_inventory_count / self.max_capacity) * 100, 1),
            "door_open": self.door_open,
            "alarm_active": self.alarm_active,
            "total_units_stored": self.total_units_stored,
            "temperature_excursions": self.temperature_excursions,
            "total_runtime_hours": round(self.total_runtime_hours, 2)
        })
        
        return telemetry
    
    def start_processing(self, batch_id: str) -> bool:
        """Start processing (storing) a batch."""
        if self.error_state:
            self.logger.error(f"Cannot start processing: {self.error_state}")
            return False
        
        # Check capacity
        if self.current_inventory_count >= self.max_capacity:
            self.set_error("Storage capacity full")
            return False
        
        # Add to storage
        self.stored_batches.append(batch_id)
        self.current_inventory_count += 1
        self.total_units_stored += 1
        self.is_processing = True
        self.state = "processing"
        self.current_batch_id = batch_id
        
        self.logger.info(f"Stored batch {batch_id} (Inventory: {self.current_inventory_count}/{self.max_capacity})")
        return True
    
    def complete_processing(self) -> Dict[str, Any]:
        """Complete processing (retrieve) a batch."""
        if not self.stored_batches:
            self.logger.warning("No batches in storage")
            return {}
        
        # Retrieve oldest batch (FIFO)
        batch_id = self.stored_batches.pop(0)
        self.current_inventory_count -= 1
        
        # Simulate door opening for retrieval
        self.door_open = True
        
        result = {
            "batch_id": batch_id,
            "device_id": self.device_id,
            "process_type": "storage_retrieval",
            "success": True,
            "quality_metrics": {
                "storage_temperature_maintained": self.temperature_excursions == 0,
                "agitation_continuous": True,
                "product_integrity": random.uniform(0.95, 0.99)
            }
        }
        
        # Close door after brief delay (simulated)
        # In real implementation, this would be time-based
        self.door_open = False
        
        self.is_processing = False
        self.current_batch_id = None
        if self.current_inventory_count == 0:
            self.state = "idle"
        
        self.logger.info(f"Retrieved batch {batch_id} (Inventory: {self.current_inventory_count}/{self.max_capacity})")
        return result
    
    def simulate_fault(self, fault_type: str) -> None:
        """Simulate a device fault for testing."""
        fault_messages = {
            "temperature_control": "Temperature control system failure",
            "agitation_motor": "Agitation motor malfunction",
            "door_sensor": "Door sensor error",
            "compressor_failure": "Compressor failure"
        }
        
        message = fault_messages.get(fault_type, "Unknown fault")
        self.set_error(message)
        self.alarm_active = True
