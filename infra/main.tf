terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.89.0"
    }
  }

  required_version = ">= 1.2.0"

  backend "local" {}
}

provider "azurerm" {
  features {}

  subscription_id            = "5832fe9e-11be-402d-83e3-22494863aec9"
  skip_provider_registration = true
}
