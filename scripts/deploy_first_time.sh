#!/usr/bin/env bash
# One-click ECR + Lambda bootstrap for Math Operations API

set -euo pipefail # Exit on error, undefined variable, or failed pipe
IFS=$'\n\t' # Set Internal Field Separator to handle spaces in filenames

### --- Configurable bits -------------------------------------------------- ###
REGION=${AWS_DEFAULT_REGION:-"eu-central-1"}          # or set AWS_DEFAULT_REGION
REPO_NAME="math-api-lambda"
FUNC_NAME="math-api-lambda"
IMAGE_TAG="latest"

# Lambda needs an execution role ARN (basic logging is enough).
# Create once in console or with:
#   aws iam create-role --role-name mathLambdaRole \
#       --assume-role-policy-document file://trust.json
LAMBDA_ROLE_ARN="${LAMBDA_ROLE_ARN:-"arn:aws:iam::<ACCOUNT_ID>:role/mathLambdaRole"}"
### ------------------------------------------------------------------------ ###


echo "Resolving account ID..."
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)     # Get the AWS account ID
ECR_URI="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG"   # ECR URI for the image

echo "Building container from Dockerfile.lambda ..."
docker build -f Dockerfile.lambda -t $REPO_NAME .

echo "Logging Docker into ECR ..."
aws ecr get-login-password --region "$REGION" | \
  docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

#---------------------------------------------------------------------------
# 1. ECR repository (create if missing)
#---------------------------------------------------------------------------
if aws ecr describe-repositories --repository-names "$REPO_NAME" \
        --region "$REGION" >/dev/null 2>&1; then
    echo "ECR repo $REPO_NAME already exists"
else
    echo "Creating ECR repo $REPO_NAME ..."
    aws ecr create-repository --repository-name "$REPO_NAME" --region "$REGION"
fi

echo "Tagging + pushing image to $ECR_URI ..."
docker tag $REPO_NAME:latest "$ECR_URI"
docker push "$ECR_URI"

#---------------------------------------------------------------------------
# 2. Lambda function (create or update)
#---------------------------------------------------------------------------
if aws lambda get-function --function-name "$FUNC_NAME" --region "$REGION" \
        >/dev/null 2>&1; then
    echo "Function exists. Updating image ..."
    aws lambda update-function-code \
        --function-name "$FUNC_NAME" \
        --image-uri "$ECR_URI" \
        --region "$REGION"  \
        --publish
else
    echo "Creating Lambda function $FUNC_NAME ..."
    aws lambda create-function \
        --function-name "$FUNC_NAME" \
        --package-type Image \
        --code ImageUri="$ECR_URI" \
        --role "$LAMBDA_ROLE_ARN" \
        --timeout 30 \
        --memory-size 256 \
        --region "$REGION"
fi

echo "Done. Next step: attach an HTTP API Gateway."
echo "   Example CLI:"
echo "     az api-gateway create-http-api or use AWS Console > API Gateway > HTTP API"
echo
