terraform {
  required_providers {
    cortex = {
      source  = "cortexapps/cortex"
      version = "~> 0.6"
    }
  }
  required_version = ">= 1.5"
}

provider "cortex" {
  token        = var.cortex_api_token
  base_api_url = var.cortex_base_url
}
