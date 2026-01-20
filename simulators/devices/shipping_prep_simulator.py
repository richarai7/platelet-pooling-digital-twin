"""
Shipping Prep Station device simulator.

Simulates a shipping preparation station that packages and documents
platelet products for distribution to hospitals.
"""
from typing import Dict, Any
import random
from datetime import datetime, timedelta
from core.base_simulator import BaseDeviceSimulator


class ShippingPrepSimulator(BaseDeviceSimulator):
    """
    Simulates a shipping preparation station.
    
    Packages platelet products with appropriate insulation,
    temperature monitoring, and shipping documentation.
    """
    
    def __init__(self, device_id: str, telemetry_interval: int = 5):
        super().__init__(device_id, "shipping_prep", telemetry_interval)
        
        # Device-specific parameters
        self.package_temperature = 22.0  # Celsius
        self.target_package_temp = 22.0
        self.insulation_integrity = 100.0  # percentage
        self.prep_time_minutes = 8
        self.remaining_time_seconds = 0
        
        # Packaging status
        self.packaging_complete = False
        self.documentation_complete = False
        self.temperature_monitor_active = False
        
        # Consumables
        self.insulation_boxes_available = 100
        self.temperature_monitors_available = 50
        self.documentation_forms_available = 200
        
        # Processing metrics
        self.shipments_prepared = 0
        self.shipment_failures = 0
        self.total_runtime_hours = 0.0
        
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate shipping prep station telemetry data."""
        # Simulate parameter changes during processing
        if self.is_processing:
            progress = 1 - (self.remaining_time_seconds / (self.prep_time_minutes * 60))
            
            # Package temperature during prep
            self.package_temperature = self.target_package_temp + random.uniform(-0.5, 0.5)
            
            # Update prep stages
            if progress > 0.3:
                self.packaging_complete = True
                self.insulation_integrity = random.uniform(98, 100)
            if progress > 0.6:
                self.temperature_monitor_active = True
            if progress > 0.8:
                self.documentation_complete = True
            
            if self.remaining_time_seconds > 0:
                self.remaining_time_seconds -= self.telemetry_interval
        else:
            self.package_temperature = 22.0 + random.uniform(-1, 1)
            self.packaging_complete = False
            self.documentation_complete = False
            self.temperature_monitor_active = False
            self.insulation_integrity = 100.0
        
        telemetry = self.get_base_telemetry()
        telemetry.update({
            "package_temperature_celsius": round(self.package_temperature, 1),
            "insulation_integrity_percent": round(self.insulation_integrity, 1),
            "packaging_complete": self.packaging_complete,
            "documentation_complete": self.documentation_complete,
            "temperature_monitor_active": self.temperature_monitor_active,
            "remaining_time_seconds": max(0, self.remaining_time_seconds),
            "insulation_boxes_available": self.insulation_boxes_available,
            "temperature_monitors_available": self.temperature_monitors_available,
            "documentation_forms_available": self.documentation_forms_available,
            "shipments_prepared": self.shipments_prepared,
            "shipment_failures": self.shipment_failures,
            "success_rate": round((self.shipments_prepared / max(1, self.shipments_prepared + self.shipment_failures)) * 100, 1),
            "total_runtime_hours": round(self.total_runtime_hours, 2)
        })
        
        return telemetry
    
    def start_processing(self, batch_id: str) -> bool:
        """Start processing (preparing for shipment) a batch."""
        if self.is_processing:
            self.logger.warning(f"Already processing batch {self.current_batch_id}")
            return False
        
        if self.error_state:
            self.logger.error(f"Cannot start processing: {self.error_state}")
            return False
        
        # Check consumables
        if self.insulation_boxes_available < 1:
            self.set_error("Insulation boxes depleted")
            return False
        
        if self.temperature_monitors_available < 1:
            self.set_error("Temperature monitors depleted")
            return False
        
        if self.documentation_forms_available < 1:
            self.set_error("Documentation forms depleted")
            return False
        
        self.current_batch_id = batch_id
        self.is_processing = True
        self.state = "processing"
        self.remaining_time_seconds = self.prep_time_minutes * 60
        
        self.logger.info(f"Started processing batch {batch_id}")
        return True
    
    def complete_processing(self) -> Dict[str, Any]:
        """Complete the current processing operation."""
        if not self.is_processing:
            self.logger.warning("No batch currently processing")
            return {}
        
        batch_id = self.current_batch_id
        
        # Simulate prep success (very high success rate)
        prep_success = random.random() < 0.998
        
        if prep_success:
            self.shipments_prepared += 1
            self.insulation_boxes_available -= 1
            self.temperature_monitors_available -= 1
            self.documentation_forms_available -= 1
        else:
            self.shipment_failures += 1
        
        self.total_runtime_hours += self.prep_time_minutes / 60.0
        
        # Generate shipping data
        estimated_delivery = datetime.now() + timedelta(hours=random.randint(4, 12))
        
        result = {
            "batch_id": batch_id,
            "device_id": self.device_id,
            "process_type": "shipping_preparation",
            "prep_time_minutes": self.prep_time_minutes,
            "success": prep_success,
            "shipping_data": {
                "shipment_id": f"SHIP-{batch_id}",
                "product_id": f"PLT-{batch_id}",
                "destination": f"Hospital-{random.randint(1, 50)}",
                "shipping_method": random.choice(["Express", "Priority", "Standard"]),
                "estimated_delivery": estimated_delivery.isoformat(),
                "temperature_monitor_id": f"TM-{random.randint(10000, 99999)}" if prep_success else None
            },
            "quality_metrics": {
                "packaging_integrity": random.uniform(0.95, 0.99) if prep_success else 0.0,
                "insulation_quality": random.uniform(0.96, 0.99) if prep_success else 0.0,
                "documentation_complete": prep_success,
                "temperature_monitor_functional": prep_success
            }
        }
        
        # Reset state
        self.is_processing = False
        self.current_batch_id = None
        self.state = "idle"
        self.remaining_time_seconds = 0
        
        self.logger.info(f"Completed processing batch {batch_id}: {'Success' if prep_success else 'Failed'}")
        return result
    
    def simulate_fault(self, fault_type: str) -> None:
        """Simulate a device fault for testing."""
        fault_messages = {
            "insulation_defect": "Insulation box defect detected",
            "monitor_malfunction": "Temperature monitor malfunction",
            "printer_error": "Documentation printer error",
            "sealing_failure": "Package sealing failure"
        }
        
        message = fault_messages.get(fault_type, "Unknown fault")
        self.set_error(message)
        self.is_processing = False
