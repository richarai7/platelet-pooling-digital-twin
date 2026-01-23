// Azure Data Explorer Module - Historical Telemetry Data
param location string
param projectName string
param environment string
param tags object

var clusterName = '${projectName}-${environment}-adx'
var databaseName = 'TelemetryHistory'

// Determine SKU and capacity based on environment
var clusterSku = environment == 'prod' ? {
  name: 'Standard_E4ads_v5'
  tier: 'Standard'
  capacity: 2
} : {
  name: 'Dev(No SLA)_Standard_E2a_v4'
  tier: 'Basic'
  capacity: 1
}

// Azure Data Explorer Cluster
resource cluster 'Microsoft.Kusto/clusters@2023-08-15' = {
  name: clusterName
  location: location
  tags: tags
  sku: clusterSku
  properties: {
    enableStreamingIngest: true
    enablePurge: true
    enableDiskEncryption: true
    publicNetworkAccess: 'Enabled'
    trustedExternalTenants: []
    optimizedAutoscale: environment == 'prod' ? {
      version: 1
      isEnabled: true
      minimum: 2
      maximum: 10
    } : null
  }
  identity: {
    type: 'SystemAssigned'
  }
}

// Database for telemetry history
resource database 'Microsoft.Kusto/clusters/databases@2023-08-15' = {
  parent: cluster
  name: databaseName
  location: location
  kind: 'ReadWrite'
  properties: {
    softDeletePeriod: environment == 'prod' ? 'P365D' : 'P90D'
    hotCachePeriod: environment == 'prod' ? 'P31D' : 'P7D'
  }
}

// Outputs
output clusterName string = cluster.name
output clusterId string = cluster.id
output clusterUri string = cluster.properties.uri
output databaseName string = database.name
