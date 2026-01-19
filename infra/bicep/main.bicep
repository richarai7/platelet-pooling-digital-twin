// Main Bicep template for Platelet Pooling Digital Twin
targetScope = 'subscription'

@description('Environment name (dev, test, prod)')
param environment string = 'dev'

@description('Primary Azure region')
param location string = 'eastus'

@description('Resource name prefix')
param projectName string = 'platelet-dt'

@description('Tags for all resources')
param tags object = {
  project: 'Platelet Pooling Digital Twin'
  environment: environment
  managedBy: 'Bicep'
}

// Resource Group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${projectName}-${environment}-rg'
  location: location
  tags: tags
}

// IoT Hub Module
module iotHub 'modules/iot-hub.bicep' = {
  scope: rg
  name: 'iotHub-deployment'
  params: {
    location: location
    projectName: projectName
    environment: environment
    tags: tags
  }
}

// Digital Twins Module
module digitalTwins 'modules/digital-twins.bicep' = {
  scope: rg
  name: 'digitalTwins-deployment'
  params: {
    location: location
    projectName: projectName
    environment: environment
    tags: tags
  }
}

// Azure Functions (Event Processing)
module functions 'modules/functions.bicep' = {
  scope: rg
  name: 'functions-deployment'
  params: {
    location: location
    projectName: projectName
    environment: environment
    iotHubName: iotHub.outputs.iotHubName
    digitalTwinsEndpoint: digitalTwins.outputs.digitalTwinsEndpoint
    tags: tags
  }
}

// Data Explorer (Historical Data)
module dataExplorer 'modules/data-explorer.bicep' = {
  scope: rg
  name: 'dataExplorer-deployment'
  params: {
    location: location
    projectName: projectName
    environment: environment
    tags: tags
  }
}

// Redis Cache (Simulator State)
module redis 'modules/redis.bicep' = {
  scope: rg
  name: 'redis-deployment'
  params: {
    location: location
    projectName: projectName
    environment: environment
    tags: tags
  }
}

// Outputs
output resourceGroupName string = rg.name
output iotHubName string = iotHub.outputs.iotHubName
output iotHubConnectionString string = iotHub.outputs.iotHubConnectionString
output digitalTwinsName string = digitalTwins.outputs.digitalTwinsName
output digitalTwinsEndpoint string = digitalTwins.outputs.digitalTwinsEndpoint
output functionAppName string = functions.outputs.functionAppName
output dataExplorerClusterUri string = dataExplorer.outputs.clusterUri
output redisCacheName string = redis.outputs.redisCacheName
