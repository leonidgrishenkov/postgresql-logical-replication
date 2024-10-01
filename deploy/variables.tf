variable "cloud_id" {
  type        = string
  description = "Cloud ID"
}

variable "folder_id" {
  type        = string
  description = "Folder ID"
}

variable "iam_token" {
  type        = string
  description = "IAM Token"
}

variable "zone" {
  type        = string
  description = "Zone name"
}

variable "image_id" {
  type        = string
  description = "Image ID"
}

# Variables for PostgreSQL databases.
variable "postgres_user" {
  type        = string
  description = "PostgreSQL database root user"
}

variable "postgres_password" {
  type        = string
  description = "PostgreSQL database root user password"
}

variable "postgres_image" {
  type        = string
  description = "PostgreSQL database Docker image and tag that will be pulled from the registry"
}


