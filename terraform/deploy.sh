#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f ../.env ]; then
    echo -e "${BLUE}📁 Loading environment variables...${NC}"
    export $(cat ../.env | grep -v '^#' | xargs)
else
    echo -e "${RED}❌ .env file not found${NC}"
    exit 1
fi

# Verify AWS credentials are loaded
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ] || [ -z "$AWS_REGION" ]; then
    echo -e "${RED}❌ AWS credentials not found in .env file${NC}"
    echo "Please ensure AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_REGION are set in .env"
    exit 1
fi

echo -e "${BLUE}🚀 Starting deployment process...${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "Docker is not running. Please start Docker first."
    exit 1
fi

# Get configuration from Terraform outputs
echo -e "${BLUE}📖 Reading Terraform outputs...${NC}"
ECR_REPO=$(terraform output -raw ecr_repository_url)
EC2_IP=$(terraform output -raw public_ip)
if [ $? -ne 0 ]; then
    echo "Failed to get outputs from Terraform. Have you run terraform apply?"
    exit 1
fi

# Extract region from ECR repo URL
AWS_REGION=$(echo $ECR_REPO | cut -d'.' -f4)
APP_NAME=$(echo $ECR_REPO | cut -d'/' -f2)

echo -e "${BLUE}ℹ️  Using ECR repository: ${ECR_REPO}${NC}"

# Login to ECR
echo -e "${BLUE}📦 Logging in to ECR...${NC}"
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPO%/*}

# Build the Docker image
echo -e "${BLUE}🔨 Building Docker image...${NC}"
cd ..
docker build --no-cache -t ${APP_NAME} .

# Tag the image
echo -e "${BLUE}🏷️  Tagging image...${NC}"
docker tag ${APP_NAME}:latest ${ECR_REPO}:latest

# Push the image to ECR
echo -e "${BLUE}⬆️  Pushing image to ECR...${NC}"
docker push ${ECR_REPO}:latest

# Return to terraform directory
cd terraform

# Function to update SSM parameter
update_ssm_parameter() {
    local name=$1
    local value=$2
    
    if [ -n "$value" ]; then
        echo -e "${BLUE}🔒 Updating parameter: ${name}${NC}"
        aws ssm put-parameter \
            --name "/${APP_NAME}/${name}" \
            --value "${value}" \
            --type "SecureString" \
            --overwrite \
            --region "${AWS_REGION}"
    fi
}

# Update all sensitive parameters
echo -e "${BLUE}🔒 Updating AWS Systems Manager Parameters...${NC}"
update_ssm_parameter "OPENAI_API_KEY" "${OPENAI_API_KEY}"
update_ssm_parameter "PINECONE_API_KEY" "${PINECONE_API_KEY}"
update_ssm_parameter "POSTGRES_URI" "${POSTGRES_URI}"
update_ssm_parameter "AWS_ACCESS_KEY_ID" "${AWS_ACCESS_KEY_ID}"
update_ssm_parameter "AWS_SECRET_ACCESS_KEY" "${AWS_SECRET_ACCESS_KEY}"
update_ssm_parameter "SERPAPI_API_KEY" "${SERPAPI_API_KEY}"
update_ssm_parameter "LANGCHAIN_API_KEY" "${LANGCHAIN_API_KEY}"

# When running terraform apply, pass all variables
echo -e "${BLUE}🔄 Applying Terraform configuration...${NC}"
terraform apply \
  -var="aws_access_key_id=${AWS_ACCESS_KEY_ID}" \
  -var="aws_secret_access_key=${AWS_SECRET_ACCESS_KEY}" \
  -var="openai_api_key=${OPENAI_API_KEY}" \
  -var="pinecone_api_key=${PINECONE_API_KEY}" \
  -var="postgres_uri=${POSTGRES_URI}" \
  -var="serpapi_api_key=${SERPAPI_API_KEY}" \
  -var="langchain_api_key=${LANGCHAIN_API_KEY}" \
  -auto-approve

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${GREEN}🌐 Your application is accessible at: http://${EC2_IP}:8000/api/v1/${NC}"