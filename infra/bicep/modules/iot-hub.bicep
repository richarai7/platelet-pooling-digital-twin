// Azure IoT Hub Module
param location string
param projectName string
param environment string
param tags object

var iotHubName = '${projectName}-${environment}-iothub'
var iotHubSkuName = environment == 'prod' ? 'S2' : 'S1'
var iotHubSkuUnits = 1

resource iotHub 'Microsoft.Devices/IotHubs@2023-06-30' = {
  name: iotHubName
  location: location
  tags: tags
  sku: {
    name: iotHubSkuName
    capacity: iotHubSkuUnits
  }
  properties: {
    eventHubEndpoints: {
      events: {
        retentionTimeInDays: 1
        partitionCount: 4
      }
    }
    routing: {
      endpoints: {
        eventHubs: []
      }
      routes: []
      fallbackRoute: {
        name: '$fallback'
        source: 'DeviceMessages'
        condition: 'true'
        endpointNames: [
          'events'
        ]
        isEnabled: true
      }
    }
    cloudToDevice: {
      maxDeliveryCount: 10
      defaultTtlAsIso8601: 'PT1H'
      feedback: {
        lockDurationAsIso8601: 'PT1M'
        ttlAsIso8601: 'PT1H'
        maxDeliveryCount: 10
      }
    }
    enableFileUploadNotifications: false
  }
}

// Consumer group for Azure Functions
resource consumerGroup 'Microsoft.Devices/IotHubs/eventHubEndpoints/ConsumerGroups@2023-06-30' = {
  parent: iotHub::eventHubEndpoint
  name: 'functions-consumer-group'
}

resource eventHubEndpoint 'Microsoft.Devices/IotHubs/eventHubEndpoints@2023-06-30' existing = {
  parent: iotHub
  name: 'events'
}

// Outputs
output iotHubName string = iotHub.name
output iotHubId string = iotHub.id
output iotHubConnectionString string = 'HostName=${iotHub.properties.hostName};SharedAccessKeyName=iothubowner;SharedAccessKey=${listKeys(iotHub.id, '2023-06-30').value[0].primaryKey}'
output eventHubEndpoint string = iotHub.properties.eventHubEndpoints.events.endpoint
