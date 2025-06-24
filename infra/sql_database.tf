resource "azurerm_mssql_server" "sqlserver" {
  name                         = "${var.project_name}-sqlsrv"
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  version                      = "12.0"
  administrator_login          = var.sql_admin_username
  administrator_login_password = var.sql_admin_password

  minimum_tls_version = "1.2"
}

resource "azurerm_mssql_database" "sqldb" {
  name                = "${var.project_name}-db"
  server_id           = azurerm_mssql_server.sqlserver.id
  sku_name            = "Basic"
  max_size_gb         = 2
  zone_redundant      = false
  collation           = "SQL_Latin1_General_CP1_CI_AS"
}
