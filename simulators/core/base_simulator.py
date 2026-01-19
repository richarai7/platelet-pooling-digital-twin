"""
Base device simulator interface.

All device simulators must implement this interface to ensure consistency
across the simulation platform.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging


class BaseDeviceSimulator(ABC):
    """
    Abstract base class for all device simulators.
    
    This class provides the common interface and shared functionality
    for all lab device simulators in the platelet pooling process.
    """
    
    def __init__(
        self,
        device_id: str,
        device_type: str,
        telemetry_interval: int = 5
    ):
        """
        Initialize the base device simulator.
        
        Args:
            device_id: Unique identifier for this device instance
            device_type: Type of device (e.g., 'centrifuge', 'macopress')
            telemetry_interval: Seconds between telemetry transmissions
        """
        self.device_id = device_id
        self.device_type = device_type
        self.telemetry_interval = telemetry_interval
        self.logger = logging.getLogger(f"{device_type}.{device_id}")
        
        # Device state
        self.is_running = False
        self.is_processing = False
        self.current_batch_id: Optional[str] = None
        self.state = "idle"
        self.error_state: Optional[str] = None
        
    @abstractmethod
    def generate_telemetry(self) -> Dict[str, Any]:
        """
        Generate telemetry data for this device.
        
        Returns:
            Dictionary containing telemetry data specific to this device type
        """
        pass
    
    @abstractmethod
    def start_processing(self, batch_id: str) -> bool:
        """
        Start processing a batch.
        
        Args:
            batch_id: Unique identifier for the batch being processed
            
        Returns:
            True if processing started successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def complete_processing(self) -> Dict[str, Any]:
        """
        Complete the current processing operation.
        
        Returns:
            Dictionary containing processing results and metrics
        """
        pass
    
    def get_base_telemetry(self) -> Dict[str, Any]:
        """
        Get common telemetry fields shared by all devices.
        
        Returns:
            Dictionary with base telemetry fields
        """
        return {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "timestamp": datetime.utcnow().isoformat(),
            "state": self.state,
            "is_processing": self.is_processing,
            "current_batch_id": self.current_batch_id,
            "error_state": self.error_state
        }
    
    def set_error(self, error_message: str) -> None:
        """Set device to error state."""
        self.error_state = error_message
        self.state = "error"
        self.logger.error(f"Device error: {error_message}")
    
    def clear_error(self) -> None:
        """Clear device error state."""
        self.error_state = None
        if self.state == "error":
            self.state = "idle"
        self.logger.info("Error cleared")
    
    def start(self) -> None:
        """Start the device simulator."""
        self.is_running = True
        self.logger.info(f"Device {self.device_id} started")
    
    def stop(self) -> None:
        """Stop the device simulator."""
        self.is_running = False
        self.is_processing = False
        self.logger.info(f"Device {self.device_id} stopped")
