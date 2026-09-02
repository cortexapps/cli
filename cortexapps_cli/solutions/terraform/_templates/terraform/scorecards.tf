# scorecards.tf — Platform-owned
# Defines the Terraform Demo Production Readiness scorecard.
# Bronze: automatically achieved by all properly-defined services.
# Silver: requires adding links and metadata — see the delta.
# Gold: requires shared ownership and a rich description — aspirational.

resource "cortex_scorecard" "production_readiness" {
  tag         = "terraform-demo-production-readiness"
  name        = "Terraform Demo Production Readiness"
  description = "Measures how production-ready a Parts Unlimited service is. Bronze is table stakes; Gold is the aspirational standard."
  draft       = false

  ladder = {
    levels = [
      {
        name  = "Bronze"
        rank  = 1
        color = "#CD7F32"
      },
      {
        name  = "Silver"
        rank  = 2
        color = "#C0C0C0"
      },
      {
        name  = "Gold"
        rank  = 3
        color = "#D7AC58"
      }
    ]
  }

  rules = [
    # ── Bronze ────────────────────────────────────────────────────────────────
    {
      title       = "Has description"
      description = "Service must have a non-empty description."
      expression  = "entity.description().length > 0"
      weight      = 1
      level       = "Bronze"
    },
    {
      title       = "Has owner team"
      description = "Service must be owned by at least one team."
      expression  = "ownership.teams().length > 0"
      weight      = 1
      level       = "Bronze"
    },
    {
      title       = "Has git configured"
      description = "Service must have a git repository linked."
      expression  = "git != null"
      weight      = 1
      level       = "Bronze"
    },

    # ── Silver ────────────────────────────────────────────────────────────────
    {
      title       = "Has runbook"
      description = "Service must have a runbook link for operational readiness."
      expression  = "links(\"runbook\").length > 0"
      weight      = 1
      level       = "Silver"
    },
    {
      title       = "Has terraform-workspace metadata"
      description = "Service must declare its Terraform workspace via the terraform-workspace metadata key."
      expression  = "custom(\"terraform-workspace\") != null"
      weight      = 1
      level       = "Silver"
    },
    {
      title       = "Meaningful description"
      description = "Service description should be at least 30 characters."
      expression  = "entity.description().length >= 30"
      weight      = 1
      level       = "Silver"
    },

    # ── Gold ──────────────────────────────────────────────────────────────────
    {
      title       = "Rich description"
      description = "Service description should be at least 50 characters."
      expression  = "entity.description().length >= 50"
      weight      = 1
      level       = "Gold"
    },
    {
      title       = "Shared ownership"
      description = "Service should be owned by at least two teams for bus-factor resilience."
      expression  = "ownership.teams().length >= 2"
      weight      = 1
      level       = "Gold"
    },
    {
      title       = "Has documentation"
      description = "Service must have a documentation link in addition to a runbook."
      expression  = "links(\"documentation\").length > 0"
      weight      = 1
      level       = "Gold"
    }
  ]

  filter = {
    types = {
      include = ["service"]
    }
  }

  evaluation = {
    window = 24
  }
}
