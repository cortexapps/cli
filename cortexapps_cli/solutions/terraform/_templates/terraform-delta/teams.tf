# teams.tf — Platform-owned (DELTA VERSION)
# This is a complete replacement for _templates/terraform/teams.tf
# Changes: Sarah Connor added to team-development

# CHANGED: Sarah Connor added
resource "cortex_catalog_entity" "team_development" {
  tag         = "team-development"
  name        = "Development"
  description = "Application development team responsible for Parts Unlimited's e-commerce platform and core services."

  groups = ["terraform-demo"]

  team = {
    members = [
      {
        name  = "Bill Palmer"
        email = "bill.palmer@parts-unlimited.com"
        role  = "Team Lead"
      },
      {
        name  = "Maxine Chambers"
        email = "maxine.chambers@parts-unlimited.com"
        role  = "Senior Engineer"
      },
      {
        name  = "Dev Magee"
        email = "dev.magee@parts-unlimited.com"
        role  = "Engineer"
      },
      {
        name  = "Sarah Connor"
        email = "sarah.connor@parts-unlimited.com"
        role  = "Engineer"
      }
    ]
  }
}

resource "cortex_catalog_entity" "team_operations" {
  tag         = "team-operations"
  name        = "IT Operations"
  description = "Infrastructure, reliability, and operations for Parts Unlimited's production systems."

  groups = ["terraform-demo"]

  team = {
    members = [
      {
        name  = "Brent Geller"
        email = "brent.geller@parts-unlimited.com"
        role  = "Principal Engineer"
      },
      {
        name  = "Wes Davis"
        email = "wes.davis@parts-unlimited.com"
        role  = "Operations Manager"
      }
    ]
  }
}

resource "cortex_catalog_entity" "team_security" {
  tag         = "team-security"
  name        = "Information Security"
  description = "Security, compliance, and risk management for Parts Unlimited."

  groups = ["terraform-demo"]

  team = {
    members = [
      {
        name  = "John Pesche"
        email = "john.pesche@parts-unlimited.com"
        role  = "CISO"
      }
    ]
  }
}

resource "cortex_catalog_entity" "team_qa" {
  tag         = "team-qa"
  name        = "Quality Assurance"
  description = "Testing, QA, and release verification for Parts Unlimited services."

  groups = ["terraform-demo"]

  team = {
    members = [
      {
        name  = "Patty McKee"
        email = "patty.mckee@parts-unlimited.com"
        role  = "QA Manager"
      }
    ]
  }
}
