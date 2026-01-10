#!/bin/bash
set -e

# 1. Load environment variables from .env
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo "Warning: .env file not found. Ensure you have the necessary context if context lookups are required."
fi

# Set Region if provided
if [ ! -z "$AWS_REGION" ]; then
  export AWS_DEFAULT_REGION=$AWS_REGION
  export CDK_DEPLOY_REGION=$AWS_REGION
fi

PROJECT_NAME="${PROJECT_NAME:-dynaman}"
ENV_NAME="${ENV:-dev}"

echo "----------------------------------------------------------------"
echo "DESTROYING Dynaman Infrastructure..."
echo "Project: $PROJECT_NAME"
echo "Env:     $ENV_NAME"
echo "Region:  ${AWS_REGION:-$(aws configure get region)}"
echo "----------------------------------------------------------------"
echo "⚠️  WARNING: This will delete ALL resources including:"
echo "   - ECS Cluster & Services"
echo "   - Load Balancers"
echo "   - ECR Repositories (and images)"
echo "   - Secrets Manager Secrets (Data will be lost!)"
echo "   - CI/CD Pipelines & Artifact Buckets"
echo "----------------------------------------------------------------"
read -p "Are you sure you want to proceed? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

# 2. Build the CDK destroy command
# We pass the same context variables to ensure consistent synthesis before destruction.
CDK_CMD="npx cdk destroy --force"

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
echo "✅ Infrastructure Destroyed."
echo "----------------------------------------------------------------"
