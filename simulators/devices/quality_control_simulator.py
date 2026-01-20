"""
Quality Control Station device simulator.

Simulates a QC testing station that performs automated quality tests
on pooled platelet products.
"""
from typing import Dict, Any
import random
from core.base_simulator import BaseDeviceSimulator


class QualityControlSimulator(BaseDeviceSimulator):
    """
    Simulates a quality control testing station.
    
    Performs automated tests including platelet count, pH, glucose,
    bacterial detection, and visual inspection.
    """
    
    def __init__(self, device_id: str, telemetry_interval: int = 5):
        super().__init__(device_id, "quality_control", telemetry_interval)
        
        # Device-specific parameters
        self.test_temperature = 22.0  # Celsius
        self.sample_volume_ml = 0.0
        self.required_sample_ml = 5.0
        self.test_time_minutes = 10
        self.remaining_time_seconds = 0
        
        # Test results (generated during processing)
        self.platelet_count = 0.0  # x10^9/L
        self.ph_level = 0.0
        self.glucose_level = 0.0  # mg/dL
        self.bacterial_test = "pending"
        
        # Processing metrics
        self.tests_completed = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.total_runtime_hours = 0.0
        
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate QC station telemetry data."""
        # Simulate parameter changes during processing
        if self.is_processing:
            # Sample volume fills at start
            progress = 1 - (self.remaining_time_seconds / (self.test_time_minutes * 60))
            if progress < 0.2:
                self.sample_volume_ml = self.required_sample_ml * (progress / 0.2)
            else:
                self.sample_volume_ml = self.required_sample_ml
            
            # Generate test results as testing progresses
            if progress > 0.3:
                self.platelet_count = random.uniform(800, 1200)  # Normal range
            if progress > 0.5:
                self.ph_level = random.uniform(7.0, 7.6)  # Normal range
            if progress > 0.7:
                self.glucose_level = random.uniform(200, 400)  # Normal range
            if progress > 0.9:
                self.bacterial_test = "negative" if random.random() < 0.995 else "positive"
            
            self.test_temperature = 22.0 + random.uniform(-0.5, 0.5)
            if self.remaining_time_seconds > 0:
                self.remaining_time_seconds -= self.telemetry_interval
        else:
            self.sample_volume_ml = 0
            self.platelet_count = 0
            self.ph_level = 0
            self.glucose_level = 0
            self.bacterial_test = "pending"
            self.test_temperature = 22.0 + random.uniform(-0.5, 0.5)
        
        telemetry = self.get_base_telemetry()
        telemetry.update({
            "test_temperature_celsius": round(self.test_temperature, 1),
            "sample_volume_ml": round(self.sample_volume_ml, 1),
            "platelet_count_x10_9_per_L": round(self.platelet_count, 1) if self.platelet_count > 0 else None,
            "ph_level": round(self.ph_level, 2) if self.ph_level > 0 else None,
            "glucose_level_mg_per_dL": round(self.glucose_level, 1) if self.glucose_level > 0 else None,
            "bacterial_test_result": self.bacterial_test,
            "remaining_time_seconds": max(0, self.remaining_time_seconds),
            "tests_completed": self.tests_completed,
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "pass_rate": round((self.tests_passed / max(1, self.tests_completed)) * 100, 1),
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
        self.remaining_time_seconds = self.test_time_minutes * 60
        
        self.logger.info(f"Started processing batch {batch_id}")
        return True
    
    def complete_processing(self) -> Dict[str, Any]:
        """Complete the current processing operation."""
        if not self.is_processing:
            self.logger.warning("No batch currently processing")
            return {}
        
        batch_id = self.current_batch_id
        self.tests_completed += 1
        
        # Final test results (ensure all are within acceptable ranges)
        final_platelet_count = random.uniform(800, 1200)
        final_ph = random.uniform(7.0, 7.6)
        final_glucose = random.uniform(200, 400)
        final_bacterial = "negative" if random.random() < 0.995 else "positive"
        
        # Determine pass/fail
        passed = (
            final_platelet_count >= 800 and
            final_ph >= 6.8 and final_ph <= 7.8 and
            final_glucose >= 150 and
            final_bacterial == "negative"
        )
        
        if passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
        
        self.total_runtime_hours += self.test_time_minutes / 60.0
        
        result = {
            "batch_id": batch_id,
            "device_id": self.device_id,
            "process_type": "quality_control",
            "test_time_minutes": self.test_time_minutes,
            "success": passed,
            "test_results": {
                "platelet_count": round(final_platelet_count, 1),
                "ph_level": round(final_ph, 2),
                "glucose_level": round(final_glucose, 1),
                "bacterial_test": final_bacterial,
                "visual_inspection": "clear" if random.random() < 0.98 else "cloudy"
            },
            "quality_metrics": {
                "overall_quality_score": random.uniform(0.85, 0.99) if passed else random.uniform(0.50, 0.75),
                "platelet_viability": random.uniform(0.90, 0.98) if passed else random.uniform(0.70, 0.85),
                "sterility_confirmed": final_bacterial == "negative"
            }
        }
        
        # Reset state
        self.is_processing = False
        self.current_batch_id = None
        self.state = "idle"
        self.remaining_time_seconds = 0
        
        self.logger.info(f"Completed processing batch {batch_id}: {'Passed' if passed else 'Failed'}")
        return result
    
    def simulate_fault(self, fault_type: str) -> None:
        """Simulate a device fault for testing."""
        fault_messages = {
            "sensor_calibration": "Sensor calibration error",
            "reagent_low": "Testing reagent level low",
            "contamination": "Sample contamination detected",
            "analyzer_error": "Analyzer malfunction"
        }
        
        message = fault_messages.get(fault_type, "Unknown fault")
        self.set_error(message)
        self.is_processing = False
