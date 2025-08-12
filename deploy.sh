#!/bin/bash

# ---
# Deploys the Math API to AWS Lambda.
# This script is idempotent: it creates resources if they don't exist,
# or updates them if they do.
#
# It requires a `.env` file in the root directory with:
#   - AWS_DEFAULT_REGION
#   - LAMBDA_ROLE_ARN
# ---

# Exit immediately if a command exits with a non-zero status.
# Exit immediately if a pipeline returns a non-zero status.
# Treat unset variables as an error.
set -euo pipefail

### --- Load and Validate Environment --- ###

# Check if .env file exists and load it
if [ -f .env ]; then
  # Use `export` to make the variables available to sub-shells (like aws-cli)
  export $(cat .env | sed 's/#.*//g' | xargs)
else
  echo "❌ Error: .env file not found."
  echo "Please copy .env.example to .env and fill in your values."
  exit 1
fi

# Check that required variables are set
if [ -z "${AWS_DEFAULT_REGION:-}" ] || [ -z "${LAMBDA_ROLE_ARN:-}" ]; then
  echo "❌ Error: AWS_DEFAULT_REGION and LAMBDA_ROLE_ARN must be set in your .env file."
  exit 1
fi

### --- Configuration (from .env and dynamic) --- ###
REGION="$AWS_DEFAULT_REGION"
ECR_REPO_NAME="math-operations-api-repo"   # ECR Repository Name
LAMBDA_FUNCTION_NAME="math-operations-api" # Lambda Function Name
IMAGE_TAG="latest"

echo "➡️ Resolving AWS Account ID..."
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
if [ -z "$ACCOUNT_ID" ]; then
    echo "❌ Error: Could not resolve AWS Account ID. Is AWS CLI configured correctly?"
    exit 1
fi
echo "✅ Account ID: $ACCOUNT_ID"

ECR_URI="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPO_NAME:$IMAGE_TAG"

### --- Build and Push Docker Image --- ###

echo "➡️ Building container from Dockerfile.lambda..."
# We can use the ECR_REPO_NAME for the local docker tag for consistency
docker build -f Dockerfile.lambda -t "$ECR_REPO_NAME" .

echo "➡️ Logging Docker into Amazon ECR..."
aws ecr get-login-password --region "$REGION" | \
  docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

### --- 1. ECR Repository (Create if missing) --- ###

# The >/dev/null 2>&1 redirects all output (stdout and stderr) to /dev/null to keep things clean.
if aws ecr describe-repositories --repository-names "$ECR_REPO_NAME" --region "$REGION" >/dev/null 2>&1; then
    echo "✅ ECR repo '$ECR_REPO_NAME' already exists."
else
    echo "➡️ Creating ECR repo '$ECR_REPO_NAME'..."
    aws ecr create-repository --repository-name "$ECR_REPO_NAME" --region "$REGION"
    echo "✅ ECR repo created."
fi

echo "➡️ Tagging and pushing image to $ECR_URI..."
docker tag "$ECR_REPO_NAME:$IMAGE_TAG" "$ECR_URI"
docker push "$ECR_URI"
echo "✅ Image pushed successfully."

### --- 2. Lambda Function (Create or Update) --- ###

if aws lambda get-function --function-name "$LAMBDA_FUNCTION_NAME" --region "$REGION" >/dev/null 2>&1; then
    echo "➡️ Function '$LAMBDA_FUNCTION_NAME' exists. Updating function code..."
    aws lambda update-function-code \
        --function-name "$LAMBDA_FUNCTION_NAME" \
        --image-uri "$ECR_URI" \
        --region "$REGION"
    echo "✅ Function code updated."
else
    echo "➡️ Creating Lambda function '$LAMBDA_FUNCTION_NAME'..."
    aws lambda create-function \
        --function-name "$LAMBDA_FUNCTION_NAME" \
        --package-type Image \
        --code ImageUri="$ECR_URI" \
        --role "$LAMBDA_ROLE_ARN" \
        --timeout 30 \
        --memory-size 512 \
        --region "$REGION"
    echo "✅ Function created."
fi

# Fetch the function ARN to use in the API Gateway suggestion
FUNCTION_ARN=$(aws lambda get-function --function-name "$LAMBDA_FUNCTION_NAME" --query 'Configuration.FunctionArn' --output text)

### --- Final Instructions --- ###

echo "
🎉 Deployment Complete!

Your Lambda function is deployed. To make it accessible via the internet,
you need to connect it to an API Gateway.

You can do this in the AWS Console or run the following AWS CLI command:
"
aws apigatewayv2 create-api \
    --name "MathHttpApi" \
    --protocol-type HTTP \
    --target "$FUNCTION_ARN"
"
echo "The output of that command will give you the public URL for your API."