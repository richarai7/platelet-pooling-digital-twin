// Azure Cache for Redis Module - Simulator State Management
param location string
param projectName string
param environment string
param tags object

var redisCacheName = '${projectName}-${environment}-redis'

// Determine SKU based on environment
var redisSku = environment == 'dev' ? {
  name: 'Basic'
  family: 'C'
  capacity: 0
} : {
  name: 'Standard'
  family: 'C'
  capacity: 1
}

// Azure Cache for Redis
resource redisCache 'Microsoft.Cache/redis@2023-08-01' = {
  name: redisCacheName
  location: location
  tags: tags
  properties: {
    sku: redisSku
    enableNonSslPort: false
    minimumTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
    redisConfiguration: {
      'maxmemory-policy': 'allkeys-lru'
    }
    redisVersion: '6'
  }
}

// Outputs
output redisCacheName string = redisCache.name
output redisCacheId string = redisCache.id
output redisCacheHostName string = redisCache.properties.hostName
output redisCachePrimaryKey string = redisCache.listKeys().primaryKey
