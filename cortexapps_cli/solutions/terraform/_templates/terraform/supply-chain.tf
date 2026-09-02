# supply-chain.tf — Supply Chain team-owned
# This file defines the Supply Chain domain and all services within it.
# The supply chain team submits PRs to this file to add/update services.

resource "cortex_catalog_entity" "domain_supply_chain" {
  tag         = "domain-supply-chain"
  name        = "Supply Chain"
  description = "Inventory, ordering, and shipping services supporting Parts Unlimited's fulfillment operations."
  type        = "domain"

  groups = ["terraform-demo"]
}

resource "cortex_catalog_entity" "inventory_service" {
  tag         = "inventory-service"
  name        = "Inventory Service"
  description = "Real-time inventory tracking across all Parts Unlimited warehouses."

  owners = [
    {
      name     = "team-operations"
      type     = "group"
      provider = "CORTEX"
    }
  ]

  groups = ["terraform-demo", "domain:supply-chain"]

  git = {
    github = {
      repository = "parts-unlimited/inventory-service"
      base_path  = "/"
    }
  }

  links = [
    {
      name = "Terraform Source"
      type = "source"
      url  = "https://github.com/cortexapps/cli/blob/main/cortexapps_cli/solutions/terraform/_templates/terraform/supply-chain.tf"
    }
  ]
}

resource "cortex_catalog_entity" "ordering_service" {
  tag         = "ordering-service"
  name        = "Ordering Service"
  description = "Order placement, validation, and fulfillment coordination."

  owners = [
    {
      name     = "team-development"
      type     = "group"
      provider = "CORTEX"
    }
  ]

  groups = ["terraform-demo", "domain:supply-chain"]

  git = {
    github = {
      repository = "parts-unlimited/ordering-service"
      base_path  = "/"
    }
  }

  links = [
    {
      name = "Terraform Source"
      type = "source"
      url  = "https://github.com/cortexapps/cli/blob/main/cortexapps_cli/solutions/terraform/_templates/terraform/supply-chain.tf"
    }
  ]
}

resource "cortex_catalog_entity" "shipping_service" {
  tag         = "shipping-service"
  name        = "Shipping Service"
  description = "Shipping and logistics tracking for Parts Unlimited orders."

  owners = [
    {
      name     = "team-operations"
      type     = "group"
      provider = "CORTEX"
    }
  ]

  groups = ["terraform-demo", "domain:supply-chain"]

  git = {
    github = {
      repository = "parts-unlimited/shipping-service"
      base_path  = "/"
    }
  }

  links = [
    {
      name = "Terraform Source"
      type = "source"
      url  = "https://github.com/cortexapps/cli/blob/main/cortexapps_cli/solutions/terraform/_templates/terraform/supply-chain.tf"
    }
  ]
}
