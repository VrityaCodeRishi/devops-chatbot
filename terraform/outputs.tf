output "artifact_registry_url" {
  description = "Artifact Registry repository URL"
  value       = "${var.artifact_registry_location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}"
}

output "docker_push_command" {
  description = "Command to push Docker images to Artifact Registry"
  value       = "docker push ${var.artifact_registry_location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/app:latest"
}

output "github_actions_sa_email" {
  description = "GitHub Actions service account email"
  value       = google_service_account.github_actions.email
}

output "github_actions_sa_key" {
  description = "GitHub Actions service account key (base64 encoded) - Use for GCP_SA_KEY secret"
  value       = google_service_account_key.github_actions_key.private_key
  sensitive   = true
}

output "cloud_run_service_account" {
  description = "Cloud Run service account email"
  value       = google_service_account.cloud_run.email
}

output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}