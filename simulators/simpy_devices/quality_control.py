"""
SimPy-based Quality Control simulator.
"""
import simpy
import random
from typing import Dict, Any, Tuple
from simpy_core.simpy_base import SimPyDeviceSimulator, BatchItem


class QualityControl(SimPyDeviceSimulator):
    """Simulates automated quality control testing."""
    
    def __init__(
        self,
        env: simpy.Environment,
        device_id: str = "quality_control_01",
        capacity: int = 2,
        mean_test_time: float = 240.0,  # 4 minutes
        **kwargs
    ):
        super().__init__(
            env=env,
            device_id=device_id,
            device_type="quality_control",
            capacity=capacity,
            mean_process_time=mean_test_time,
            **kwargs
        )
        self.passed_tests = 0
        self.failed_tests = 0
    
    def _perform_processing(self, batch: BatchItem) -> Tuple[float, Dict[str, Any]]:
        """Perform quality control testing."""
        test_time = random.normalvariate(self.mean_process_time, 15.0)
        test_time = max(180.0, test_time)
        
        yield self.env.timeout(test_time)
        
        # Run multiple tests
        platelet_count = random.uniform(2.5e11, 4.0e11)  # Platelet count
        ph_level = random.uniform(6.8, 7.4)
        bacterial_test = random.random() > 0.001  # 99.9% pass rate
        
        # Determine pass/fail
        test_passed = (
            platelet_count >= 3.0e11 and
            6.9 <= ph_level <= 7.3 and
            bacterial_test
        )
        
        if test_passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
        
        result = {
            'success': test_passed,
            'device_id': self.device_id,
            'processing_time': test_time,
            'platelet_count': platelet_count,
            'ph_level': ph_level,
            'bacterial_test_passed': bacterial_test,
            'overall_quality_score': random.uniform(0.85, 0.99) if test_passed else random.uniform(0.50, 0.84)
        }
        
        batch.quality_metrics['qc_passed'] = test_passed
        batch.quality_metrics['quality_score'] = result['overall_quality_score']
        
        return test_time, result
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate quality control telemetry."""
        base_telemetry = super().generate_telemetry()
        base_telemetry.update({
            'passed_tests': self.passed_tests,
            'failed_tests': self.failed_tests,
            'pass_rate': self.passed_tests / max(1, self.passed_tests + self.failed_tests)
        })
        return base_telemetry
