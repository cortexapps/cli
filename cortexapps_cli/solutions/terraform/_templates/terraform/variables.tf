variable "cortex_api_token" {
  description = "Cortex API token. Can also be set via the CORTEX_API_TOKEN environment variable."
  type        = string
  sensitive   = true
}

variable "cortex_base_url" {
  description = "Cortex API base URL."
  type        = string
  default     = "https://api.getcortexapp.com"
}
