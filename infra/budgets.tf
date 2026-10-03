# AWS Budgets - Cost Monitoring

resource "aws_budgets_budget" "monthly" {
  name              = "${var.project_prefix}-monthly-budget"
  budget_type       = "COST"
  limit_unit        = "USD"
  limit_amount      = var.budget_limit
  time_period_start = "2026-10-01_00:00"
  time_period_end   = "2027-12-31_00:00"
  time_unit         = "MONTHLY"
  tags              = local.tags

  lifecycle {
    ignore_changes = [tags_all]
  }
}

# Outputs
output "budget_limit" {
  description = "Monthly budget limit in USD"
  value       = var.budget_limit
}

output "budget_name" {
  description = "Budget name"
  value       = aws_budgets_budget.monthly.name
}
