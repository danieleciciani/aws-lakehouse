# AWS Budgets - Cost Monitoring

resource "aws_budgets_budget" "monthly" {
  name              = "${var.project_prefix}-monthly-budget"
  budget_type       = "MONTHLY"
  limit_unit        = "USD"
  limit_amount      = var.budget_limit
  time_period_start = "2026-10-01"
  time_period_end   = "2087-12-31"

  tags = local.tags
}

# Budget alert at 50%
resource "aws_budgets_budget_action" "alert_50" {
  budget_name        = aws_budgets_budget.monthly.name
  action_id          = "alert-50-percent"
  action_type        = "APPLY_IAM_POLICY"
  approval_model     = "AUTOMATIC"
  notification_type  = "FORECASTED"
  threshold_type     = "PERCENTAGE"
  threshold_value    = 50

  definition {
    iam_action_definition {
      iam_role_arn       = "arn:aws:iam::${local.account_id}:role/service-role/AWSBudgetsNotificationRole"
      policy_arn         = "arn:aws:iam::aws:policy/CloudWatchNotificationRole"
    }
  }

  depends_on = [aws_budgets_budget.monthly]
}

# Budget alert at 80%
resource "aws_budgets_budget_action" "alert_80" {
  budget_name        = aws_budgets_budget.monthly.name
  action_id          = "alert-80-percent"
  action_type        = "APPLY_IAM_POLICY"
  approval_model     = "AUTOMATIC"
  notification_type  = "FORECASTED"
  threshold_type     = "PERCENTAGE"
  threshold_value    = 80

  definition {
    iam_action_definition {
      iam_role_arn       = "arn:aws:iam::${local.account_id}:role/service-role/AWSBudgetsNotificationRole"
      policy_arn         = "arn:aws:iam::aws:policy/CloudWatchNotificationRole"
    }
  }

  depends_on = [aws_budgets_budget.monthly]
}

# Budget alert at 100%
resource "aws_budgets_budget_action" "alert_100" {
  budget_name        = aws_budgets_budget.monthly.name
  action_id          = "alert-100-percent"
  action_type        = "APPLY_IAM_POLICY"
  approval_model     = "AUTOMATIC"
  notification_type  = "ACTUAL"
  threshold_type     = "PERCENTAGE"
  threshold_value    = 100

  definition {
    iam_action_definition {
      iam_role_arn       = "arn:aws:iam::${local.account_id}:role/service-role/AWSBudgetsNotificationRole"
      policy_arn         = "arn:aws:iam::aws:policy/CloudWatchNotificationRole"
    }
  }

  depends_on = [aws_budgets_budget.monthly]
}

# Outputs
output "budget_limit" {
  description = "Monthly budget limit in USD"
  value       = var.budget_limit
}
