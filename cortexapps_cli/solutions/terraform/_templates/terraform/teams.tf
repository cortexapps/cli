# teams.tf — Platform-owned
# Changes to teams (membership, new hires, reorgs) are made here via platform PR.

resource "cortex_catalog_entity" "team_development" {
  tag         = "team-development"
  name        = "Development"
  description = "Application development team responsible for Parts Unlimited's e-commerce platform and core services."

  groups = ["terraform-demo"]

  team = {
    members = [
      {
        name        = "Bill Palmer"
        email       = "bill.palmer@parts-unlimited.com"
        role        = "Team Lead"
        description = "IT Manager leading the Phoenix Project"
      },
      {
        name        = "Maxine Chambers"
        email       = "maxine.chambers@parts-unlimited.com"
        role        = "Senior Engineer"
        description = "Staff engineer on the Phoenix Project"
      },
      {
        name        = "Dev Magee"
        email       = "dev.magee@parts-unlimited.com"
        role        = "Engineer"
        description = "Developer on the Phoenix Project"
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
        name        = "Brent Geller"
        email       = "brent.geller@parts-unlimited.com"
        role        = "Principal Engineer"
        description = "Indispensable operations expert and bottleneck"
      },
      {
        name        = "Wes Davis"
        email       = "wes.davis@parts-unlimited.com"
        role        = "Operations Manager"
        description = "Manages day-to-day operations work"
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
        name        = "John Pesche"
        email       = "john.pesche@parts-unlimited.com"
        role        = "CISO"
        description = "Chief Information Security Officer"
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
        name        = "Patty McKee"
        email       = "patty.mckee@parts-unlimited.com"
        role        = "QA Manager"
        description = "Manages QA processes and testing"
      }
    ]
  }
}
