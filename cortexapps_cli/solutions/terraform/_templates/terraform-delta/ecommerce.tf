# ecommerce.tf — E-Commerce team-owned (DELTA VERSION)
# This is a complete replacement for _templates/terraform/ecommerce.tf
# Changes: phoenix promoted to Silver (links + metadata + expanded description),
#          notification-service added (new Bronze service)

resource "cortex_catalog_entity" "domain_ecommerce" {
  tag         = "domain-ecommerce"
  name        = "E-Commerce"
  description = "Customer-facing e-commerce platform including product catalog, checkout, and payments."
  type        = "domain"

  groups = ["terraform-demo"]
}

# CHANGED: description expanded (≥30 chars for Silver rule 3),
#          links added (Silver rule 1), metadata added (Silver rule 2)
resource "cortex_catalog_entity" "phoenix" {
  tag         = "phoenix"
  name        = "The Phoenix Project"
  description = "Main e-commerce monolith for Parts Unlimited, handling product browsing, cart, and checkout flows."

  owners = [
    {
      name     = "team-development"
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
      name = "Runbook"
      type = "runbook"
      url  = "https://wiki.parts-unlimited.com/runbooks/phoenix"
    },
    {
      name = "Architecture Docs"
      type = "documentation"
      url  = "https://wiki.parts-unlimited.com/architecture/phoenix"
    }
  ]

  metadata = jsonencode({
    "terraform-workspace" = "phoenix-prod"
  })
}

resource "cortex_catalog_entity" "parts_catalog_api" {
  tag         = "parts-catalog-api"
  name        = "Parts Catalog API"
  description = "REST API for browsing the parts catalog."

  owners = [
    {
      name     = "team-development"
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
}

resource "cortex_catalog_entity" "payments_service" {
  tag         = "payments-service"
  name        = "Payments Service"
  description = "Payment processing and refund handling."

  owners = [
    {
      name     = "team-development"
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
}

# NEW SERVICE — will show as `+ create` in terraform plan
resource "cortex_catalog_entity" "notification_service" {
  tag         = "notification-service"
  name        = "Notification Service"
  description = "Handles email, SMS, and push notifications for Parts Unlimited customer events."

  owners = [
    {
      name     = "team-development"
      type     = "group"
      provider = "CORTEX"
    }
  ]

  groups = ["terraform-demo", "domain:ecommerce"]

  git = {
    github = {
      repository = "parts-unlimited/notification-service"
      base_path  = "/"
    }
  }
}
