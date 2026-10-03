variable "project_prefix" {
  description = "Project prefix for resource naming"
  type        = string
  default     = "lakehouse-uber-demo"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-north-1"
}

variable "environment" {
  description = "Environment (dev, prod)"
  type        = string
  default     = "dev"
}

variable "cost_center" {
  description = "Cost center for billing"
  type        = string
  default     = "demo"
}

variable "owner" {
  description = "Resource owner"
  type        = string
  default     = "data-platform"
}

# Glue configuration
variable "glue_worker_type" {
  description = "Glue job worker type (G.1X, G.2X)"
  type        = string
  default     = "G.1X"
}

variable "glue_num_workers" {
  description = "Number of Glue workers"
  type        = number
  default     = 2
}

variable "glue_job_timeout" {
  description = "Glue job timeout in minutes"
  type        = number
  default     = 10
}

# Budget configuration
variable "budget_limit" {
  description = "Monthly budget limit in USD"
  type        = number
  default     = 10
}

variable "budget_alert_email" {
  description = "Email for budget alerts"
  type        = string
  default     = "danix.c96@gmail.com"
}
