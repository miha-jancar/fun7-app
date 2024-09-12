terraform {
  backend "gcs" {
    bucket  = "miha-fun7-tfstate"
    prefix  = "terraform/state"
  }
}

# Google Cloud provider
provider "google" {
  project = var.project_id
  region  = var.region
}

# Enabling required APIs
resource "google_project_service" "cloud_run" {
  project = var.project_id
  service = "run.googleapis.com"
}

# Cloud Run Service
resource "google_cloud_run_v2_service" "cloudrun_service" {
  name     = var.service_name
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/fun7/${var.image_name}:${var.image_tag}"
        
      # Set resource limits
      resources {
        limits = {
          cpu    = "1"     # 1 CPU core
          memory = "512Mi" # 512 MB memory
        }
      }
    }

    # Scale based on CPU utilization
    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }
  }

}

# Allow unauthenticated access (optional)
resource "google_cloud_run_service_iam_policy" "noauth" {
  location    = google_cloud_run_v2_service.cloudrun_service.location
  service     = google_cloud_run_v2_service.cloudrun_service.name
  policy_data = data.google_iam_policy.noauth.policy_data
}

data "google_iam_policy" "noauth" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}

