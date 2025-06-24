resource "azurerm_key_vault_secret" "flask_secret_key" {
  name         = "FlaskSecretKey"
  value        = var.flask_secret_key
  key_vault_id = azurerm_key_vault.main.id
}

resource "azurerm_key_vault_secret" "sql_admin_password" {
  name         = "SqlAdminPassword"
  value        = var.sql_admin_password
  key_vault_id = azurerm_key_vault.main.id
}
