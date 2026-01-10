#!/usr/bin/env node
import 'source-map-support/register';
import * as dotenv from 'dotenv';
dotenv.config(); // Load environment variables from .env file

import * as cdk from 'aws-cdk-lib';
import { DynamanStack } from '../lib/dynaman-stack';

const app = new cdk.App();
new DynamanStack(app, 'DynamanStack', {
  env: { 
    account: process.env.CDK_DEFAULT_ACCOUNT || process.env.CDK_DEPLOY_ACCOUNT, 
    region: process.env.CDK_DEFAULT_REGION || process.env.CDK_DEPLOY_REGION || process.env.AWS_REGION 
  },
  /* If you don't specify 'env', this stack will be environment-agnostic.
   * Account/Region-dependent features and context lookups will not work,
   * but a single synthesized template can be deployed anywhere. */

  /* Uncomment the next line to specialize this stack for the AWS Account
   * and Region that are implied by the current CLI configuration. */
  // env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },

  /* Uncomment the next line if you know exactly what Account and Region you
   * want to deploy the stack to. */
  // env: { account: '123456789012', region: 'us-east-1' },
});
