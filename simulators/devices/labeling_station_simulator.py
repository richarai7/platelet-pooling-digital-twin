"""
Labeling Station device simulator.

Simulates an automated labeling station that prints and applies
labels to platelet products with tracking information.
"""
from typing import Dict, Any
import random
from datetime import datetime, timedelta
from core.base_simulator import BaseDeviceSimulator


class LabelingStationSimulator(BaseDeviceSimulator):
    """
    Simulates a labeling station device.
    
    Prints product labels with all required information (product ID,
    expiration, storage requirements, etc.) and applies them to bags.
    """
    
    def __init__(self, device_id: str, telemetry_interval: int = 5):
        super().__init__(device_id, "labeling_station", telemetry_interval)
        
        # Device-specific parameters
        self.printer_temperature = 0.0  # Celsius
        self.target_printer_temp = 60.0
        self.label_position_accuracy = 0.0  # mm offset
        self.print_quality_score = 0.0  # 0-100
        self.label_time_seconds = 15
        self.remaining_time_seconds = 0
        
        # Consumables
        self.label_stock_count = 500
        self.ribbon_remaining_meters = 150.0
        
        # Processing metrics
        self.labels_completed = 0
        self.label_failures = 0
        self.total_runtime_hours = 0.0
        
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate labeling station telemetry data."""
        # Simulate parameter changes during processing
        if self.is_processing:
            self.printer_temperature = self.target_printer_temp + random.uniform(-3, 3)
            progress = 1 - (self.remaining_time_seconds / self.label_time_seconds)
            
            # Label application accuracy
            self.label_position_accuracy = random.uniform(0, 0.5) if progress > 0.7 else 0
            # Print quality
            self.print_quality_score = random.uniform(90, 100)
            
            if self.remaining_time_seconds > 0:
                self.remaining_time_seconds -= self.telemetry_interval
        else:
            self.printer_temperature = 25.0 + random.uniform(-1, 1)
            self.label_position_accuracy = 0
            self.print_quality_score = 0
        
        telemetry = self.get_base_telemetry()
        telemetry.update({
            "printer_temperature_celsius": round(self.printer_temperature, 1),
            "label_position_accuracy_mm": round(self.label_position_accuracy, 2),
            "print_quality_score": round(self.print_quality_score, 1),
            "remaining_time_seconds": max(0, self.remaining_time_seconds),
            "label_stock_count": self.label_stock_count,
            "ribbon_remaining_meters": round(self.ribbon_remaining_meters, 1),
            "labels_completed": self.labels_completed,
            "label_failures": self.label_failures,
            "success_rate": round((self.labels_completed / max(1, self.labels_completed + self.label_failures)) * 100, 1),
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
        
        # Check consumables
        if self.label_stock_count < 1:
            self.set_error("Label stock depleted")
            return False
        
        if self.ribbon_remaining_meters < 0.2:
            self.set_error("Ribbon depleted")
            return False
        
        self.current_batch_id = batch_id
        self.is_processing = True
        self.state = "processing"
        self.remaining_time_seconds = self.label_time_seconds
        
        self.logger.info(f"Started processing batch {batch_id}")
        return True
    
    def complete_processing(self) -> Dict[str, Any]:
        """Complete the current processing operation."""
        if not self.is_processing:
            self.logger.warning("No batch currently processing")
            return {}
        
        batch_id = self.current_batch_id
        
        # Simulate labeling success (very high success rate)
        labeling_success = random.random() < 0.997
        
        if labeling_success:
            self.labels_completed += 1
            self.label_stock_count -= 1
            self.ribbon_remaining_meters -= 0.2  # ~20cm per label
        else:
            self.label_failures += 1
        
        self.total_runtime_hours += self.label_time_seconds / 3600.0
        
        # Generate label data
        expiration_date = datetime.now() + timedelta(days=5)
        
        result = {
            "batch_id": batch_id,
            "device_id": self.device_id,
            "process_type": "labeling",
            "label_time_seconds": self.label_time_seconds,
            "success": labeling_success,
            "label_data": {
                "product_id": f"PLT-{batch_id}",
                "product_type": "Pooled Platelets",
                "volume_ml": random.randint(280, 320),
                "expiration_date": expiration_date.isoformat(),
                "storage_temp": "20-24°C",
                "barcode": f"{random.randint(100000000, 999999999)}"
            },
            "quality_metrics": {
                "print_quality": random.uniform(0.92, 0.99) if labeling_success else 0.0,
                "position_accuracy": random.uniform(0.95, 0.99) if labeling_success else 0.0,
                "barcode_readable": labeling_success
            }
        }
        
        # Reset state
        self.is_processing = False
        self.current_batch_id = None
        self.state = "idle"
        self.remaining_time_seconds = 0
        
        self.logger.info(f"Completed processing batch {batch_id}: {'Success' if labeling_success else 'Failed'}")
        return result
    
    def simulate_fault(self, fault_type: str) -> None:
        """Simulate a device fault for testing."""
        fault_messages = {
            "print_head_jam": "Print head jammed",
            "label_misalignment": "Label applicator misaligned",
            "ribbon_jam": "Ribbon feed jammed",
            "stock_empty": "Label stock empty"
        }
        
        message = fault_messages.get(fault_type, "Unknown fault")
        self.set_error(message)
        self.is_processing = False
        self.printer_temperature = 25.0
