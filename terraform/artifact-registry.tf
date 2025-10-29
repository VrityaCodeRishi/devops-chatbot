# Artifact Registry for Docker images
resource "google_artifact_registry_repository" "docker_repo" {
  location      = var.artifact_registry_location
  repository_id = "devops-chatbot"
  description   = "Docker repository for DevOps Chatbot ML model"
  format        = "DOCKER"

  labels = local.common_labels

  depends_on = [
    google_project_service.required_apis
  ]
}

# IAM binding for GitHub Actions to push images
resource "google_artifact_registry_repository_iam_member" "docker_repo_writer" {
  location   = google_artifact_registry_repository.docker_repo.location
  repository = google_artifact_registry_repository.docker_repo.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${google_service_account.github_actions.email}"
}
