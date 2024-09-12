variable "project_id" {
  description = "The Google Cloud project ID."
  type        = string
}

variable "api_key" {
  description = "Api key to access the app."
  type        = string
  sensitive   = true
}

variable "region" {
  description = "The region to deploy the Cloud Run service."
  type        = string
  default     = "europe-west3"
}

variable "service_name" {
  description = "The name of the Cloud Run service."
  type        = string
  default     = "fun7-cts"
}

variable "image_name" {
  description = "The Docker image name in GCR."
  type        = string
}

variable "image_tag" {
  description = "The tag of the Docker image in GCR."
  type        = string
  default     = "latest"
}

variable "min_instances" {
  description = "The minimum number of instances."
  type        = number
  default     = 1
}

variable "max_instances" {
  description = "The maximum number of instances."
  type        = number
  default     = 10
}

variable "target_cpu_utilization" {
  description = "Target CPU utilization for scaling."
  type        = number
  default     = 80  # Scale when CPU usage exceeds 80%
}

