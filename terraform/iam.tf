# Service account for GitHub Actions deployment
resource "google_service_account" "github_actions" {
  account_id   = "github-actions-deployer"
  display_name = "GitHub Actions Deployment Service Account"
  description  = "Service account used by GitHub Actions for CI/CD deployment"
}

# Grant necessary permissions to GitHub Actions service account
resource "google_project_iam_member" "github_actions_roles" {
  for_each = toset([
    "roles/run.admin",                    # Deploy Cloud Run services
    "roles/iam.serviceAccountUser",       # Act as service accounts
    "roles/artifactregistry.writer",      # Push Docker images
    "roles/storage.objectViewer",         # Read from storage if needed
    "roles/compute.admin",                # Manage compute resources
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}

# Create service account key for GitHub Actions
resource "google_service_account_key" "github_actions_key" {
  service_account_id = google_service_account.github_actions.name
}

# Service account for Cloud Run service
resource "google_service_account" "cloud_run" {
  account_id   = "cloud-run-${var.cloud_run_service_name}"
  display_name = "Cloud Run Service Account"
  description  = "Service account for running the DevOps Chatbot Cloud Run service"
}

# Grant Cloud Run service account permissions (if needed to access other GCP services)
resource "google_project_iam_member" "cloud_run_roles" {
  for_each = toset([
    # Add roles here if your app needs to access GCP services
    # e.g., "roles/storage.objectViewer" if reading from GCS
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}
