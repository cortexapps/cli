# ecommerce.tf — E-Commerce team-owned
# This file defines the E-Commerce domain and all services within it.
# The e-commerce team submits PRs to this file to add/update services.
#
# NOTE: Services are intentionally at Bronze level only (no links, no metadata).
# See _templates/terraform-delta/ecommerce.tf for the Silver-state version.

resource "cortex_catalog_entity" "domain_ecommerce" {
  tag         = "domain-ecommerce"
  name        = "E-Commerce"
  description = "Customer-facing e-commerce platform including product catalog, checkout, and payments."
  type        = "domain"

  groups = ["terraform-demo"]
}

resource "cortex_catalog_entity" "phoenix" {
  tag         = "phoenix"
  name        = "The Phoenix Project"
  description = "Main e-commerce monolith handling browsing and checkout."

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
