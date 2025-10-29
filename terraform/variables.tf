variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "cloud_run_service_name" {
  description = "Name of Cloud Run service"
  type        = string
  default     = "devops-chatbot"
}

variable "cloud_run_memory" {
  description = "Memory allocation for Cloud Run (e.g., 2Gi, 4Gi)"
  type        = string
  default     = "2Gi"
}

variable "cloud_run_cpu" {
  description = "CPU allocation for Cloud Run"
  type        = string
  default     = "2"
}

variable "cloud_run_min_instances" {
  description = "Minimum Cloud Run instances (0 for scale to zero)"
  type        = number
  default     = 0
}

variable "cloud_run_max_instances" {
  description = "Maximum Cloud Run instances"
  type        = number
  default     = 10
}

variable "cloud_run_timeout" {
  description = "Request timeout in seconds"
  type        = number
  default     = 300
}

variable "artifact_registry_location" {
  description = "Location for Artifact Registry"
  type        = string
  default     = "us-central1"
}

variable "enable_public_access" {
  description = "Allow unauthenticated access to Cloud Run"
  type        = bool
  default     = true
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "production"
}

variable "labels" {
  description = "Labels to apply to all resources"
  type        = map(string)
  default = {
    project     = "devops-chatbot"
    managed_by  = "terraform"
    component   = "ml-inference"
  }
}
