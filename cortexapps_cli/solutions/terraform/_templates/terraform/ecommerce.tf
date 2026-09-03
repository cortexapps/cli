# ecommerce.tf — E-Commerce team-owned
# This file defines the E-Commerce domain and all services within it.
# The e-commerce team submits PRs to this file to add/update services.
#
# NOTE: Services are intentionally at Bronze level only (no links, no metadata).
# See _templates/terraform-delta/ecommerce.tf for the Silver-state version.

resource "cortex_catalog_entity" "domain_ecommerce" {
  tag         = "terraform-demo-domain-ecommerce"
  name        = "E-Commerce"
  description = "Customer-facing e-commerce platform including product catalog, checkout, and payments."
  type        = "domain"

  groups = ["terraform-demo"]

  links = [
    {
      name = "Terraform Source"
      type = "source"
      url  = "https://github.com/cortexapps/cli/blob/main/cortexapps_cli/solutions/terraform/_templates/terraform/ecommerce.tf"
    }
  ]
}

resource "cortex_catalog_entity" "phoenix" {
  tag         = "terraform-demo-phoenix"
  name        = "The Phoenix Project"
  description = "Main e-commerce monolith handling browsing and checkout."

  owners = [
    {
      name     = "terraform-demo-team-development"
      type     = "group"
      provider = "CORTEX"
    }
  ]

  groups = ["terraform-demo", "domain:ecommerce"]

  git = {
    github = {
      repository = "parts-unlimited/phoenix"
      base_path  = "/"
    }
  }

  links = [
    {
      name = "Terraform Source"
      type = "source"
      url  = "https://github.com/cortexapps/cli/blob/main/cortexapps_cli/solutions/terraform/_templates/terraform/ecommerce.tf"
    }
  ]
}

resource "cortex_catalog_entity" "parts_catalog_api" {
  tag         = "terraform-demo-parts-catalog-api"
  name        = "Parts Catalog API"
  description = "REST API for browsing the parts catalog."

  owners = [
    {
      name     = "terraform-demo-team-development"
      type     = "group"
      provider = "CORTEX"
    }
  ]

  groups = ["terraform-demo", "domain:ecommerce"]

  git = {
    github = {
      repository = "parts-unlimited/parts-catalog-api"
      base_path  = "/"
    }
  }

  links = [
    {
      name = "Terraform Source"
      type = "source"
      url  = "https://github.com/cortexapps/cli/blob/main/cortexapps_cli/solutions/terraform/_templates/terraform/ecommerce.tf"
    }
  ]
}

resource "cortex_catalog_entity" "payments_service" {
  tag         = "terraform-demo-payments-service"
  name        = "Payments Service"
  description = "Payment processing and refund handling."

  owners = [
    {
      name     = "terraform-demo-team-development"
      type     = "group"
      provider = "CORTEX"
    }
  ]

  groups = ["terraform-demo", "domain:ecommerce"]

  git = {
    github = {
      repository = "parts-unlimited/payments-service"
      base_path  = "/"
    }
  }

  links = [
    {
      name = "Terraform Source"
      type = "source"
      url  = "https://github.com/cortexapps/cli/blob/main/cortexapps_cli/solutions/terraform/_templates/terraform/ecommerce.tf"
    }
  ]
}
