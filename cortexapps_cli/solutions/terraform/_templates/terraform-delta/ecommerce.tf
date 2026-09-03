# ecommerce.tf — E-Commerce team-owned (DELTA VERSION)
# This is a complete replacement for _templates/terraform/ecommerce.tf
# Changes: phoenix promoted to Silver (links + metadata + expanded description),
#          notification-service added (new Bronze service)

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

# CHANGED: description expanded (≥30 chars for Silver rule 3),
#          links added (Silver rule 1 + Gold runbook rule), metadata added (Silver rule 2)
# NOTE: Phoenix reaches Silver only — Gold requires ownership.teams().length >= 2 (shared ownership)
resource "cortex_catalog_entity" "phoenix" {
  tag         = "terraform-demo-phoenix"
  name        = "The Phoenix Project"
  description = "Main e-commerce monolith for Parts Unlimited, handling product browsing, cart, and checkout flows."

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
    },
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

# NEW SERVICE — will show as `+ create` in terraform plan
resource "cortex_catalog_entity" "notification_service" {
  tag         = "terraform-demo-notification-service"
  name        = "Notification Service"
  description = "Handles email, SMS, and push notifications for Parts Unlimited customer events."

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
      repository = "parts-unlimited/notification-service"
      base_path  = "/"
    }
  }

  links = [
    {
      name = "Terraform Source"
      type = "source"
      url  = "https://github.com/cortexapps/cli/blob/main/cortexapps_cli/solutions/terraform/_templates/terraform-delta/ecommerce.tf"
    }
  ]
}
