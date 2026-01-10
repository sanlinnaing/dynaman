#!/bin/bash
set -e

# 1. Load environment variables from .env
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo "Error: .env file not found in infrastructure/cdk/"
  exit 1
fi

# Set Region if provided
if [ ! -z "$AWS_REGION" ]; then
  export AWS_DEFAULT_REGION=$AWS_REGION
  export CDK_DEPLOY_REGION=$AWS_REGION
fi

# Check for required variables
if [ -z "$MONGODB_URL" ]; then
  echo "Error: MONGODB_URL is not set in .env"
  exit 1
fi

PROJECT_NAME="${PROJECT_NAME:-dynaman}"
ENV_NAME="${ENV:-dev}"

MONGO_SECRET_NAME="/${PROJECT_NAME}/${ENV_NAME}/MONGODB_URL"
JWT_SECRET_NAME="/${PROJECT_NAME}/${ENV_NAME}/JWT_SECRET_KEY"

echo "----------------------------------------------------------------"
echo "Deploying Dynaman Infrastructure..."
echo "Project: $PROJECT_NAME"
echo "Env:     $ENV_NAME"
echo "Region:  ${AWS_REGION:-$(aws configure get region)}"
echo "----------------------------------------------------------------"

# Function to create or update a secret
create_or_update_secret() {
  local name=$1
  local value=$2
  local description=$3

  # Check if secret exists
  if aws secretsmanager describe-secret --secret-id "$name" >/dev/null 2>&1; then
    echo "Updating existing secret: $name"
    aws secretsmanager put-secret-value \
      --secret-id "$name" \
      --secret-string "$value" \
      --no-cli-pager > /dev/null
  else
    echo "Creating new secret: $name"
    aws secretsmanager create-secret \
      --name "$name" \
      --description "$description" \
      --secret-string "$value" \
      --no-cli-pager > /dev/null
  fi
}

echo "1. Configuring Secrets..."

# MongoDB Secret
create_or_update_secret "$MONGO_SECRET_NAME" "$MONGODB_URL" "MongoDB Connection String"

# JWT Secret
# Check if JWT secret exists, if not generate one
if ! aws secretsmanager describe-secret --secret-id "$JWT_SECRET_NAME" >/dev/null 2>&1; then
  echo "Generating new JWT Secret..."
  # Generate a random 32-char string (alphanumeric)
  JWT_SECRET=$(openssl rand -base64 32 | tr -d '/+=' | cut -c 1-32)
  create_or_update_secret "$JWT_SECRET_NAME" "$JWT_SECRET" "JWT Secret Key"
else
  echo "JWT Secret already exists. Skipping generation."
fi

echo "✅ Secrets configured."

# Fetch full ARNs to pass to CDK (required for accurate ECS referencing)
MONGO_SECRET_ARN=$(aws secretsmanager describe-secret --secret-id "$MONGO_SECRET_NAME" --query 'ARN' --output text)
JWT_SECRET_ARN=$(aws secretsmanager describe-secret --secret-id "$JWT_SECRET_NAME" --query 'ARN' --output text)

echo "Mongo Secret ARN: $MONGO_SECRET_ARN"
echo "JWT Secret ARN:   $JWT_SECRET_ARN"

echo "----------------------------------------------------------------"
echo "2. Deploying Infrastructure (CDK)..."
echo "----------------------------------------------------------------"

# Check if stack exists and is in a healthy state
STACK_STATUS=$(aws cloudformation describe-stacks --stack-name "DynamanStack" --query "Stacks[0].StackStatus" --output text 2>/dev/null || echo "NOT_FOUND")

echo "Current Stack Status: $STACK_STATUS"

# Pass Secret ARNs to CDK
CDK_CMD="npx cdk deploy --require-approval never --context mongoSecretArn=$MONGO_SECRET_ARN --context jwtSecretArn=$JWT_SECRET_ARN"

# If stack is new or failed, we trigger 'initialDeploy' mode (desiredCount=0)
# to avoid timeouts if ECR images are missing.
IS_INITIAL_DEPLOY=false
if [[ "$STACK_STATUS" == "NOT_FOUND" || "$STACK_STATUS" == *"ROLLBACK"* || "$STACK_STATUS" == *"FAILED"* ]]; then
  echo "⚠️  Initial/Recovery Deployment detected. Setting desiredCount=0."
  CDK_CMD="$CDK_CMD --context initialDeploy=true"
  IS_INITIAL_DEPLOY=true
else
  echo "ℹ️  Update Deployment detected. Using standard capacity."
fi

# We pass GitHub details as context, but NOT the secret.
if [ ! -z "$GITHUB_REPO_OWNER" ]; then
  CDK_CMD="$CDK_CMD --context githubRepoOwner=$GITHUB_REPO_OWNER"
fi
if [ ! -z "$GITHUB_REPO_NAME" ]; then
  CDK_CMD="$CDK_CMD --context githubRepoName=$GITHUB_REPO_NAME"
fi
if [ ! -z "$GITHUB_BRANCH" ]; then
  CDK_CMD="$CDK_CMD --context githubBranch=$GITHUB_BRANCH"
fi

echo "Running: $CDK_CMD"
$CDK_CMD

echo "----------------------------------------------------------------"
echo "✅ Deployment Complete."
echo "----------------------------------------------------------------"

if [ "$IS_INITIAL_DEPLOY" = true ]; then
  echo "👉 ACTION REQUIRED:"
  echo "1. Go to AWS Console > Developer Tools > Connections and APPROVE the GitHub connection."
  echo "2. Wait for the '${PROJECT_NAME}-pipeline' to run successfully (Build & Deploy)."
  echo "3. Scale up the services using one of these methods:"
  echo "   - Option A (Recommended): Run './deploy.sh' again. (Updates CloudFormation template, no drift)."
  echo "   - Option B (Fast): Run './scale-up.sh'. (Immediate scale up, temporary drift resolved on next deploy)."
fi
