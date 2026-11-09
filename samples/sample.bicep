// Preview file: Bicep
@description('Location for all resources')
param location string = resourceGroup().location

@minValue(1)
param count int = 2

var prefix = 'dusk'

resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: '${prefix}${uniqueString(resourceGroup().id)}'
  location: location
  kind: 'StorageV2'
  sku: { name: 'Standard_LRS' }
}

output id string = storage.id
