resource "azurerm_storage_account" "static" {
  name                     = "${var.project_name}storage"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  enable_https_traffic_only = true
}


resource "azurerm_storage_container" "static_assets" {
  name                  = "assets"
  storage_account_name  = azurerm_storage_account.static.name
  container_access_type = "blob"
}
