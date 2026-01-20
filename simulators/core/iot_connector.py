"""
IoT Hub connection manager for device simulators.

Handles authentication, connection management, and message sending
to Azure IoT Hub for all device simulators.
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message


class IoTConnector:
    """
    Manages IoT Hub connectivity for device simulators.
    
    This class handles the connection lifecycle and message transmission
    to Azure IoT Hub for a single device simulator.
    """
    
    def __init__(self, connection_string: str, device_id: str):
        """
        Initialize the IoT connector.
        
        Args:
            connection_string: Azure IoT Hub device connection string
            device_id: Unique identifier for this device
        """
        self.connection_string = connection_string
        self.device_id = device_id
        self.client: Optional[IoTHubDeviceClient] = None
        self.logger = logging.getLogger(f"IoTConnector.{device_id}")
        self.is_connected = False
        
    async def connect(self) -> bool:
        """
        Establish connection to Azure IoT Hub.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.client = IoTHubDeviceClient.create_from_connection_string(
                self.connection_string
            )
            await self.client.connect()
            self.is_connected = True
            self.logger.info(f"Connected to IoT Hub: {self.device_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to IoT Hub: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Azure IoT Hub."""
        if self.client and self.is_connected:
            try:
                await self.client.disconnect()
                self.is_connected = False
                self.logger.info(f"Disconnected from IoT Hub: {self.device_id}")
            except Exception as e:
                self.logger.error(f"Error during disconnect: {e}")
    
    async def send_telemetry(self, telemetry_data: Dict[str, Any]) -> bool:
        """
        Send telemetry message to IoT Hub.
        
        Args:
            telemetry_data: Dictionary containing telemetry data
            
        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.is_connected or not self.client:
            self.logger.error("Not connected to IoT Hub")
            return False
        
        try:
            # Convert telemetry to JSON message
            import json
            message_body = json.dumps(telemetry_data)
            message = Message(message_body)
            
            # Add message properties
            message.content_type = "application/json"
            message.content_encoding = "utf-8"
            message.custom_properties["deviceType"] = telemetry_data.get("device_type", "unknown")
            message.custom_properties["messageType"] = "telemetry"
            
            # Send message
            await self.client.send_message(message)
            self.logger.debug(f"Sent telemetry: {telemetry_data.get('state', 'unknown')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send telemetry: {e}")
            return False
    
    async def send_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """
        Send event message to IoT Hub.
        
        Args:
            event_type: Type of event (e.g., 'processing_complete', 'error')
            event_data: Event data payload
            
        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.is_connected or not self.client:
            self.logger.error("Not connected to IoT Hub")
            return False
        
        try:
            import json
            event_data["event_type"] = event_type
            message_body = json.dumps(event_data)
            message = Message(message_body)
            
            # Add message properties
            message.content_type = "application/json"
            message.content_encoding = "utf-8"
            message.custom_properties["deviceType"] = event_data.get("device_type", "unknown")
            message.custom_properties["messageType"] = "event"
            message.custom_properties["eventType"] = event_type
            
            # Send message
            await self.client.send_message(message)
            self.logger.info(f"Sent event: {event_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send event: {e}")
            return False
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
