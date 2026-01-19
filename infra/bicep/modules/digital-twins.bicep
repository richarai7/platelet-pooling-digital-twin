// Azure Digital Twins Module
param location string
param projectName string
param environment string
param tags object

var digitalTwinsName = '${projectName}-${environment}-dt'

resource digitalTwins 'Microsoft.DigitalTwins/digitalTwinsInstances@2023-01-31' = {
  name: digitalTwinsName
  location: location
  tags: tags
  properties: {
    publicNetworkAccess: 'Enabled'
  }
  identity: {
    type: 'SystemAssigned'
  }
}

// Outputs
output digitalTwinsName string = digitalTwins.name
output digitalTwinsId string = digitalTwins.id
output digitalTwinsEndpoint string = 'https://${digitalTwins.properties.hostName}'
output digitalTwinsPrincipalId string = digitalTwins.identity.principalId
