terraform {
  backend "gcs" {
    bucket  = "miha-fun7-tfstate"
    prefix  = "terraform/state"
    project  = var.project_id
    region   = var.region
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

resource "google_project_service" "cloud_build" {
  project = var.project_id
  service = "cloudbuild.googleapis.com"
}

# Cloud Run Service
resource "google_cloud_run_service" "cloudrun_service" {
  name     = var.service_name
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/${var.image_name}:${var.image_tag}"
        
        # Set resource limits
        resources {
          limits = {
            cpu    = "1"     # 1 CPU core
            memory = "128Mi" # 128 MB memory
          }
        }
      }

      # Scale based on CPU utilization
      scaling {
        min_instance_count = var.min_instances
        max_instance_count = var.max_instances
        target_cpu_utilization = var.target_cpu_utilization
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Allow unauthenticated access (optional)
resource "google_cloud_run_service_iam_policy" "noauth" {
  location    = google_cloud_run_service.cloudrun_service.location
  service     = google_cloud_run_service.cloudrun_service.name
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

