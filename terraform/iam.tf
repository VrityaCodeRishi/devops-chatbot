
resource "google_service_account" "github_actions" {
  account_id   = "github-actions-deployer"
  display_name = "GitHub Actions Deployment Service Account"
  description  = "Service account used by GitHub Actions for CI/CD deployment"
}


resource "google_project_iam_member" "github_actions_roles" {
  for_each = toset([
    "roles/run.admin",
    "roles/iam.serviceAccountUser",
    "roles/artifactregistry.writer",
    "roles/storage.objectViewer",
    "roles/compute.admin",
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}


resource "google_service_account_key" "github_actions_key" {
  service_account_id = google_service_account.github_actions.name
}

resource "google_service_account" "cloud_run" {
  account_id   = "cloud-run-${var.cloud_run_service_name}"
  display_name = "Cloud Run Service Account"
  description  = "Service account for running the DevOps Chatbot Cloud Run service"
}


resource "google_project_iam_member" "cloud_run_roles" {
  for_each = toset([
    # Add roles here if your app needs to access GCP services
    # e.g., "roles/storage.objectViewer" if reading from GCS
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}
