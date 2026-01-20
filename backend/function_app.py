import azure.functions as func
import logging
import json
from datetime import datetime
from azure.digitaltwins.core import DigitalTwinsClient
from azure.identity import DefaultAzureCredential

app = func.FunctionApp()

# Initialize Digital Twins client (will be initialized on first invocation)
dt_client = None
ADT_INSTANCE_URL = None


def get_digital_twins_client():
    """Get or create Digital Twins client."""
    global dt_client, ADT_INSTANCE_URL
    
    if dt_client is None:
        import os
        ADT_INSTANCE_URL = os.environ.get("DIGITAL_TWINS_INSTANCE_URL")
        if not ADT_INSTANCE_URL:
            raise ValueError("DIGITAL_TWINS_INSTANCE_URL not configured")
        
        credential = DefaultAzureCredential()
        dt_client = DigitalTwinsClient(ADT_INSTANCE_URL, credential)
        logging.info(f"Initialized Digital Twins client: {ADT_INSTANCE_URL}")
    
    return dt_client


@app.event_hub_message_trigger(
    arg_name="events",
    event_hub_name="iothub-ehub-platelet-pool",  # Will be configured via settings
    connection="EventHubConnectionString"
)
def process_telemetry(events: func.EventHubEvent):
    """
    Process telemetry messages from IoT Hub and update Digital Twins.
    
    This function is triggered whenever IoT Hub receives a message from
    a device simulator. It processes the telemetry data and updates the
    corresponding digital twin in Azure Digital Twins.
    
    Args:
        events: EventHub message(s) from IoT Hub
    """
    logging.info(f"Processing {len(events)} telemetry event(s)")
    
    try:
        client = get_digital_twins_client()
        
        for event in events:
            # Parse message body
            message_body = event.get_body().decode('utf-8')
            telemetry_data = json.loads(message_body)
            
            device_id = telemetry_data.get("device_id")
            device_type = telemetry_data.get("device_type")
            message_type = event.metadata.get("messageType", "telemetry")
            
            logging.info(
                f"Processing {message_type} from {device_id} "
                f"({device_type}): state={telemetry_data.get('state')}"
            )
            
            # Route to appropriate handler based on message type
            if message_type == "telemetry":
                update_twin_telemetry(client, device_id, telemetry_data)
            elif message_type == "event":
                handle_device_event(client, device_id, telemetry_data)
            else:
                logging.warning(f"Unknown message type: {message_type}")
            
    except Exception as e:
        logging.error(f"Error processing telemetry: {e}", exc_info=True)
        raise


def update_twin_telemetry(client: DigitalTwinsClient, device_id: str, telemetry: dict):
    """
    Update digital twin with latest telemetry data.
    
    Args:
        client: Digital Twins client
        device_id: Device identifier (digital twin ID)
        telemetry: Telemetry data to update
    """
    try:
        # Prepare patch document for digital twin update
        # This uses JSON Patch format to update specific properties
        patch = []
        
        # Update common properties
        if "state" in telemetry:
            patch.append({
                "op": "replace",
                "path": "/state",
                "value": telemetry["state"]
            })
        
        if "is_processing" in telemetry:
            patch.append({
                "op": "replace",
                "path": "/isProcessing",
                "value": telemetry["is_processing"]
            })
        
        if "current_batch_id" in telemetry:
            patch.append({
                "op": "replace",
                "path": "/currentBatchId",
                "value": telemetry.get("current_batch_id") or ""
            })
        
        if "error_state" in telemetry:
            patch.append({
                "op": "replace",
                "path": "/errorState",
                "value": telemetry.get("error_state") or ""
            })
        
        # Update device-specific properties (centrifuge example)
        if "rpm" in telemetry:
            patch.append({
                "op": "replace",
                "path": "/rpm",
                "value": telemetry["rpm"]
            })
        
        if "temperature_celsius" in telemetry:
            patch.append({
                "op": "replace",
                "path": "/temperature",
                "value": telemetry["temperature_celsius"]
            })
        
        if "vibration_mm_s" in telemetry:
            patch.append({
                "op": "replace",
                "path": "/vibration",
                "value": telemetry["vibration_mm_s"]
            })
        
        if "remaining_time_seconds" in telemetry:
            patch.append({
                "op": "replace",
                "path": "/remainingTimeSeconds",
                "value": telemetry["remaining_time_seconds"]
            })
        
        # Update last telemetry timestamp
        patch.append({
            "op": "replace",
            "path": "/lastTelemetryTime",
            "value": datetime.utcnow().isoformat()
        })
        
        # Apply the patch to the digital twin
        client.update_digital_twin(device_id, patch)
        logging.info(f"✓ Updated twin {device_id} with {len(patch)} properties")
        
    except Exception as e:
        logging.error(f"Failed to update twin {device_id}: {e}")
        raise


def handle_device_event(client: DigitalTwinsClient, device_id: str, event_data: dict):
    """
    Handle device events (e.g., processing_started, processing_complete, errors).
    
    Args:
        client: Digital Twins client
        device_id: Device identifier
        event_data: Event data payload
    """
    event_type = event_data.get("event_type")
    logging.info(f"Handling event: {event_type} for {device_id}")
    
    try:
        if event_type == "processing_started":
            # Publish telemetry event to digital twin
            client.publish_telemetry(
                device_id,
                {
                    "eventType": "processingStarted",
                    "batchId": event_data.get("batch_id"),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            logging.info(f"✓ Published processing_started event for {device_id}")
            
        elif event_type == "processing_complete":
            # Publish completion event with quality metrics
            client.publish_telemetry(
                device_id,
                {
                    "eventType": "processingComplete",
                    "batchId": event_data.get("batch_id"),
                    "qualityMetrics": event_data.get("quality_metrics", {}),
                    "cycleTimeMinutes": event_data.get("cycle_time_minutes"),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            logging.info(
                f"✓ Published processing_complete event for {device_id}, "
                f"batch: {event_data.get('batch_id')}"
            )
            
        elif event_type == "device_error":
            # Publish error event
            client.publish_telemetry(
                device_id,
                {
                    "eventType": "deviceError",
                    "errorState": event_data.get("error_state"),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            logging.warning(f"⚠️  Published device_error event for {device_id}")
            
        elif event_type == "error_cleared":
            # Publish error cleared event
            client.publish_telemetry(
                device_id,
                {
                    "eventType": "errorCleared",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            logging.info(f"✓ Published error_cleared event for {device_id}")
            
        else:
            logging.warning(f"Unknown event type: {event_type}")
    
    except Exception as e:
        logging.error(f"Failed to handle event {event_type} for {device_id}: {e}")
        raise
