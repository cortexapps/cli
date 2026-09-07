# teams.tf — Platform-owned
# Changes to teams (membership, new hires, reorgs) are made here via platform PR.

resource "cortex_catalog_entity" "team_development" {
  tag         = "terraform-demo-team-development"
  name        = "Development"
  type        = "team"
  description = "Application development team responsible for Parts Unlimited's e-commerce platform and core services."

  groups = ["terraform-demo"]

  links = [
    {
      name = "Terraform Source"
      type = "documentation"
      url  = "https://github.com/cortexapps/cli/blob/main/cortexapps_cli/solutions/terraform/_templates/terraform/teams.tf"
    }
  ]

  team = {
    members = [
      {
        name  = "Bill Palmer"
        email = "bill.palmer@parts-unlimited.com"
        role  = "Team-Lead"
      },
      {
        name  = "Maxine Chambers"
        email = "maxine.chambers@parts-unlimited.com"
        role  = "Senior-Engineer"
      },
      {
        name  = "Dev Magee"
        email = "dev.magee@parts-unlimited.com"
        role  = "Engineer"
      }
    ]
  }
}

resource "cortex_catalog_entity" "team_operations" {
  tag         = "terraform-demo-team-operations"
  name        = "IT Operations"
  type        = "team"
  description = "Infrastructure, reliability, and operations for Parts Unlimited's production systems."

  groups = ["terraform-demo"]

  links = [
    {
      name = "Terraform Source"
      type = "documentation"
      url  = "https://github.com/cortexapps/cli/blob/main/cortexapps_cli/solutions/terraform/_templates/terraform/teams.tf"
    }
  ]

  team = {
    members = [
      {
        name  = "Brent Geller"
        email = "brent.geller@parts-unlimited.com"
        role  = "Principal-Engineer"
      },
      {
        name  = "Wes Davis"
        email = "wes.davis@parts-unlimited.com"
        role  = "Operations-Manager"
      }
    ]
  }
}

resource "cortex_catalog_entity" "team_security" {
  tag         = "terraform-demo-team-security"
  name        = "Information Security"
  type        = "team"
  description = "Security, compliance, and risk management for Parts Unlimited."

  groups = ["terraform-demo"]

  links = [
    {
      name = "Terraform Source"
      type = "documentation"
      url  = "https://github.com/cortexapps/cli/blob/main/cortexapps_cli/solutions/terraform/_templates/terraform/teams.tf"
    }
  ]

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
  tag         = "terraform-demo-team-qa"
  name        = "Quality Assurance"
  type        = "team"
  description = "Testing, QA, and release verification for Parts Unlimited services."

  groups = ["terraform-demo"]

  links = [
    {
      name = "Terraform Source"
      type = "documentation"
      url  = "https://github.com/cortexapps/cli/blob/main/cortexapps_cli/solutions/terraform/_templates/terraform/teams.tf"
    }
  ]

  team = {
    members = [
      {
        name  = "Patty McKee"
        email = "patty.mckee@parts-unlimited.com"
        role  = "QA-Manager"
      }
    ]
  }
}
