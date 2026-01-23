"""
SimPy-based base simulator for platelet pooling devices.

This module provides the foundation for discrete-event simulation using SimPy,
enabling sophisticated modeling of device resources, queues, and process flows.
"""
import simpy
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import logging
from enum import Enum


class DeviceState(Enum):
    """Device operational states."""
    IDLE = "idle"
    PROCESSING = "processing"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class BatchItem:
    """Represents a batch item flowing through the process."""
    batch_id: str
    arrival_time: float
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    process_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_process_step(self, device_type: str, device_id: str, 
                        start_time: float, end_time: float, 
                        result: Dict[str, Any]):
        """Add a processing step to the batch history."""
        self.process_history.append({
            'device_type': device_type,
            'device_id': device_id,
            'start_time': start_time,
            'end_time': end_time,
            'duration': end_time - start_time,
            'result': result
        })


class SimPyDeviceSimulator:
    """
    Base class for SimPy-based device simulators.
    
    This class provides common functionality for all device simulators,
    including resource management, telemetry generation, and process modeling.
    """
    
    def __init__(
        self,
        env: simpy.Environment,
        device_id: str,
        device_type: str,
        capacity: int = 1,
        mean_process_time: float = 60.0,
        mtbf: Optional[float] = None,  # Mean time between failures (seconds)
        mttr: Optional[float] = None   # Mean time to repair (seconds)
    ):
        """
        Initialize the SimPy device simulator.
        
        Args:
            env: SimPy environment for discrete-event simulation
            device_id: Unique identifier for this device instance
            device_type: Type of device (e.g., 'centrifuge', 'macopress')
            capacity: Number of items the device can process simultaneously
            mean_process_time: Average processing time in seconds
            mtbf: Mean time between failures (for reliability simulation)
            mttr: Mean time to repair (for maintenance simulation)
        """
        self.env = env
        self.device_id = device_id
        self.device_type = device_type
        self.mean_process_time = mean_process_time
        self.mtbf = mtbf
        self.mttr = mttr
        
        # Create SimPy resource for this device
        self.resource = simpy.Resource(env, capacity=capacity)
        
        # Device state tracking
        self.state = DeviceState.IDLE
        self.current_batch: Optional[BatchItem] = None
        self.total_processed = 0
        self.total_processing_time = 0.0
        self.total_idle_time = 0.0
        self.total_downtime = 0.0
        self.failure_count = 0
        
        # Telemetry data
        self.telemetry_data: Dict[str, Any] = {}
        
        # Logger
        self.logger = logging.getLogger(f"{device_type}.{device_id}")
        
        # Start failure/repair process if configured
        if self.mtbf and self.mttr:
            env.process(self._failure_process())
    
    def _failure_process(self):
        """
        SimPy process to simulate random failures and repairs.
        """
        while True:
            # Wait until next failure
            yield self.env.timeout(self.mtbf)
            
            if self.state != DeviceState.OFFLINE:
                self.logger.warning(f"Device {self.device_id} has failed at {self.env.now}")
                self.state = DeviceState.ERROR
                self.failure_count += 1
                
                # Repair time
                repair_start = self.env.now
                yield self.env.timeout(self.mttr)
                self.total_downtime += (self.env.now - repair_start)
                
                self.logger.info(f"Device {self.device_id} repaired at {self.env.now}")
                self.state = DeviceState.IDLE
    
    def process_batch(self, batch: BatchItem):
        """
        SimPy process for processing a batch through this device.
        
        Args:
            batch: BatchItem to process
        
        Yields:
            SimPy events for resource acquisition and processing time
        """
        arrival_time = self.env.now
        
        # Request device resource
        with self.resource.request() as request:
            # Wait for device to be available
            yield request
            
            # Record start time
            start_time = self.env.now
            wait_time = start_time - arrival_time
            
            if self.state == DeviceState.IDLE:
                self.total_idle_time += wait_time
            
            # Update state
            self.state = DeviceState.PROCESSING
            self.current_batch = batch
            
            self.logger.info(
                f"Device {self.device_id} started processing batch {batch.batch_id} "
                f"at {start_time:.2f} (waited {wait_time:.2f}s)"
            )
            
            # Perform processing (subclasses override this)
            processing_time, result = yield from self._perform_processing(batch)
            
            # Record completion
            end_time = self.env.now
            self.total_processed += 1
            self.total_processing_time += processing_time
            
            # Add to batch history
            batch.add_process_step(
                device_type=self.device_type,
                device_id=self.device_id,
                start_time=start_time,
                end_time=end_time,
                result=result
            )
            
            # Update state
            self.state = DeviceState.IDLE
            self.current_batch = None
            
            self.logger.info(
                f"Device {self.device_id} completed batch {batch.batch_id} "
                f"at {end_time:.2f} (duration: {processing_time:.2f}s)"
            )
    
    def _perform_processing(self, batch: BatchItem):
        """
        Perform the actual processing operation.
        Subclasses should override this to implement device-specific logic.
        
        Args:
            batch: BatchItem being processed
        
        Yields:
            SimPy timeout event
            
        Returns:
            Tuple of (processing_time, result_dict)
        """
        # Default implementation: simple timeout
        processing_time = self.mean_process_time
        yield self.env.timeout(processing_time)
        
        result = {
            'success': True,
            'device_id': self.device_id,
            'processing_time': processing_time
        }
        
        return processing_time, result
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """
        Generate current telemetry data for this device.
        
        Returns:
            Dictionary containing device telemetry
        """
        utilization = 0.0
        if self.env.now > 0:
            utilization = self.total_processing_time / self.env.now
        
        return {
            'device_id': self.device_id,
            'device_type': self.device_type,
            'timestamp': self.env.now,
            'state': self.state.value,
            'current_batch_id': self.current_batch.batch_id if self.current_batch else None,
            'total_processed': self.total_processed,
            'utilization': utilization,
            'total_processing_time': self.total_processing_time,
            'total_idle_time': self.total_idle_time,
            'total_downtime': self.total_downtime,
            'failure_count': self.failure_count,
            'queue_length': len(self.resource.queue)
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for this device.
        
        Returns:
            Dictionary containing performance metrics
        """
        total_time = self.env.now
        
        if total_time == 0:
            return {
                'utilization': 0.0,
                'throughput': 0.0,
                'avg_processing_time': 0.0,
                'total_processed': 0,
                'failure_rate': 0.0
            }
        
        return {
            'device_id': self.device_id,
            'device_type': self.device_type,
            'utilization': self.total_processing_time / total_time,
            'throughput': self.total_processed / total_time,  # items per second
            'avg_processing_time': (
                self.total_processing_time / self.total_processed 
                if self.total_processed > 0 else 0
            ),
            'total_processed': self.total_processed,
            'total_idle_time': self.total_idle_time,
            'total_downtime': self.total_downtime,
            'failure_count': self.failure_count,
            'failure_rate': self.failure_count / total_time if total_time > 0 else 0.0,
            'avg_queue_length': len(self.resource.queue)  # Current snapshot
        }
