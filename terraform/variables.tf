variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "fastapi-app"
}

variable "app_environment" {
  description = "Application environment"
  type        = string
  default     = "production"
}

variable "container_port" {
  description = "Container port"
  type        = number
  default     = 8000
}

variable "openai_api_key" {
  description = "OpenAI API Key"
  type        = string
  sensitive   = true
}

variable "pinecone_api_key" {
  description = "Pinecone API Key"
  type        = string
  sensitive   = true
}

variable "postgres_uri" {
  description = "PostgreSQL Connection URI"
  type        = string
  sensitive   = true
}

variable "serpapi_api_key" {
  description = "SerpAPI Key"
  type        = string
  sensitive   = true
}

variable "langchain_api_key" {
  description = "LangChain API Key"
  type        = string
  sensitive   = true
}

variable "aws_access_key_id" {
  description = "AWS Access Key ID"
  type        = string
  sensitive   = true
}

variable "aws_secret_access_key" {
  description = "AWS Secret Access Key"
  type        = string
  sensitive   = true
} 