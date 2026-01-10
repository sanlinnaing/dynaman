# Dynaman Infrastructure (AWS CDK)

This directory contains the Infrastructure as Code (IaC) for the Dynaman project using the **AWS Cloud Development Kit (CDK)**. It deploys a complete ECS architecture on AWS.

## Architecture Overview
- **VPC:** Custom VPC with 2 Public Subnets (No NAT Gateways for cost optimization).
- **Compute:** ECS Cluster with Auto Scaling Group (ASG) using **Spot Instances (t4g.small - ARM64)** running **Amazon Linux 2023**.
- **Load Balancing:** Application Load Balancer (ALB) routing traffic to 4 services:
  - `ui` (Port 80)
  - `auth` (Port 8000)
  - `meta` (Port 8000)
  - `exec` (Port 8000)
- **Secrets:** Managed via **AWS Secrets Manager** (Secure).
- **CI/CD:** AWS CodePipeline + CodeBuild (linked to GitHub).

## Prerequisites

1.  **Node.js & NPM:** Ensure you have Node.js installed.
2.  **AWS CLI:** Configured with valid credentials (`aws configure`).
3.  **Docker:** Required for CDK to build assets (if needed) or for local testing.
4.  **GitHub Connection:** You must have a GitHub repository for this project.

## Setup

1.  **Install Dependencies:**
    ```bash
    cd infrastructure/cdk
    npm install
    ```

2.  **Configure Environment (`.env`):**
    Create a `.env` file in this directory. **DO NOT COMMIT THIS FILE.**

    ```env
    # AWS Configuration
    AWS_REGION=us-east-1

    # Project Settings
    PROJECT_NAME=dynaman
    ENV=dev

    # Secrets (Will be securely injected into Secrets Manager)
    MONGODB_URL=mongodb+srv://user:pass@host/dbname

    # CI/CD Configuration (Required for Pipeline)
    GITHUB_REPO_OWNER=your-github-username
    GITHUB_REPO_NAME=dynaman
    GITHUB_BRANCH=main
    ```

## Deployment

We use a helper script to ensure secure secret handling and consistent context.

### 1. Deploy
```bash
./deploy.sh
```
*   **Initial Run:** The script detects if this is a fresh deployment. To prevent failure due to missing Docker images (chicken-and-egg problem), it deploys the ECS Services with **0 tasks** (`DesiredCount=0`).
    *   **Action Required:** After the stack is created, go to the [AWS Console > Developer Tools > Connections](https://console.aws.amazon.com/codesuite/settings/connections) and **Approve** the GitHub connection.
    *   **Wait:** The Pipeline will auto-trigger, build your code, and push the images to ECR.

*   **Scale Up (Day 1):** Once the pipeline has successfully built and pushed the images:
    ```bash
    ./deploy.sh
    ```
    Running the script a second time detects the stack exists, updates the configuration to the standard capacity (`DesiredCount=2`), and CloudFormation scales up the services.

*   **Updates (Day 2+):** Just run `./deploy.sh`. It updates secrets and infrastructure as needed.

### 2. Destroy
To tear down all resources (ECS, ALB, VPC, Pipelines, Secrets):
```bash
./destroy.sh
```
*   **WARNING:** This deletes **everything**, including the database connection string stored in Secrets Manager.

## ⚠️ Critical Warnings

### 1. `cdk.context.json` & Determinism
We have explicitly **ignored** `cdk.context.json` in `.gitignore` to prevent infrastructure details from leaking into version control.
*   **Risk:** This file caches values like Availability Zones and AMI IDs. By ignoring it, **deployments from different machines (or at different times) may result in different infrastructure states** (e.g., recreating the VPC if AZs change, or replacing instances if the AMI ID updates).
*   **Mitigation:** If you deploy from multiple machines, consider manually sharing/syncing this file or pinning versions strictly in the code.

### 2. Secrets Management
*   Secrets are stored in **AWS Secrets Manager**, not in the CloudFormation template or Terraform state.
*   The `deploy.sh` script securely updates the secret value via the AWS CLI after the stack is created.
*   **Security:** Never commit your `.env` file.

### 3. State Management
*   Unlike Terraform, CDK state is managed via CloudFormation Stacks in your AWS account.
*   However, the local `cdk.out` and context act as a local cache. Clearing them (`rm -rf cdk.out cdk.context.json`) forces a full re-synthesis of the template.
