variable "project_name" {
  description = "Project name to be used for resource naming"
  type        = string
  default     = "fastapi-ecs"  # You can change this default value
} 

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

variable "aws_bucket_name" {
  description = "AWS S3 Bucket Name"
  type        = string
  sensitive   = true
}

variable "langchain_endpoint" {
  description = "LangChain Endpoint URL"
  type        = string
  sensitive   = true
}

variable "langchain_project" {
  description = "LangChain Project Name"
  type        = string
  sensitive   = true
}

variable "chroma_db_path" {
  description = "ChromaDB Path"
  type        = string
  sensitive   = true
} 
