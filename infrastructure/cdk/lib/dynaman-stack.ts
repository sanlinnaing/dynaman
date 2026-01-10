import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as autoscaling from 'aws-cdk-lib/aws-autoscaling';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as codebuild from 'aws-cdk-lib/aws-codebuild';
import * as codepipeline from 'aws-cdk-lib/aws-codepipeline';
import * as codepipeline_actions from 'aws-cdk-lib/aws-codepipeline-actions';
import * as codestar from 'aws-cdk-lib/aws-codestarconnections';

export class DynamanStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Context / Parameters
    const projectName = this.node.tryGetContext('projectName') || 'dynaman';
    const envName = this.node.tryGetContext('env') || 'dev';

    // 1. VPC
    const vpc = new ec2.Vpc(this, 'VPC', {
      vpcName: `${projectName}-vpc`,
      ipAddresses: ec2.IpAddresses.cidr('10.0.0.0/16'),
      maxAzs: 2,
      subnetConfiguration: [
        {
          cidrMask: 24,
          name: 'Public',
          subnetType: ec2.SubnetType.PUBLIC,
        }
      ],
      natGateways: 0, // Terraform config has 0 NAT Gateways (Public Subnets only)
    });

    // 2. Security Groups
    const albSg = new ec2.SecurityGroup(this, 'AlbSg', {
      vpc,
      description: 'Allow inbound traffic to ALB',
      securityGroupName: `${projectName}-alb-sg`,
      allowAllOutbound: true,
    });
    albSg.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(80), 'HTTP from anywhere');

    const ecsHostSg = new ec2.SecurityGroup(this, 'EcsHostSg', {
      vpc,
      description: 'Allow traffic from ALB',
      securityGroupName: `${projectName}-ecs-host-sg`,
      allowAllOutbound: true,
    });
    ecsHostSg.addIngressRule(albSg, ec2.Port.allTcp(), 'Traffic from ALB');

    // 3. Secrets (AWS Secrets Manager)
    // Managed by deploy.sh (External to CDK)
    // We receive the Full ARNs via context to ensure ECS can resolve them correctly.
    
    const jwtSecretArn = this.node.tryGetContext('jwtSecretArn');
    const mongoSecretArn = this.node.tryGetContext('mongoSecretArn');

    let jwtSecret: secretsmanager.ISecret;
    let mongoSecret: secretsmanager.ISecret;

    if (jwtSecretArn) {
      jwtSecret = secretsmanager.Secret.fromSecretCompleteArn(this, 'JwtSecret', jwtSecretArn);
    } else {
      // Fallback (might fail with ECS if suffix is missing)
      jwtSecret = secretsmanager.Secret.fromSecretNameV2(this, 'JwtSecret', `/${projectName}/${envName}/JWT_SECRET_KEY`);
    }

    if (mongoSecretArn) {
      mongoSecret = secretsmanager.Secret.fromSecretCompleteArn(this, 'MongoSecret', mongoSecretArn);
    } else {
      mongoSecret = secretsmanager.Secret.fromSecretNameV2(this, 'MongoSecret', `/${projectName}/${envName}/MONGODB_URL`);
    }

    // 4. ECR Repositories

    // 4. ECR Repositories
    const uiRepo = new ecr.Repository(this, 'UiRepo', {
      repositoryName: `${projectName}-ui`,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      imageTagMutability: ecr.TagMutability.MUTABLE,
      emptyOnDelete: true,
    });

    const authRepo = new ecr.Repository(this, 'AuthRepo', {
      repositoryName: `${projectName}-auth`,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      imageTagMutability: ecr.TagMutability.MUTABLE,
      emptyOnDelete: true,
    });

    const engineRepo = new ecr.Repository(this, 'EngineRepo', {
      repositoryName: `${projectName}-engine`,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      imageTagMutability: ecr.TagMutability.MUTABLE,
      emptyOnDelete: true,
    });

    // Lifecycle Rules
    const lifecycleRule = {
      maxImageCount: 10,
      description: 'Keep last 10 images',
    };
    uiRepo.addLifecycleRule(lifecycleRule);
    authRepo.addLifecycleRule(lifecycleRule);
    engineRepo.addLifecycleRule(lifecycleRule);

    // 5. ECS Cluster
    const cluster = new ecs.Cluster(this, 'Cluster', {
      clusterName: `${projectName}-cluster`,
      vpc,
    });

    // Create a Launch Template (required for newer AWS accounts/regions)
    const launchTemplate = new ec2.LaunchTemplate(this, 'EcsLaunchTemplate', {
      machineImage: ecs.EcsOptimizedImage.amazonLinux2023(ecs.AmiHardwareType.ARM),
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.T4G, ec2.InstanceSize.SMALL),
      securityGroup: ecsHostSg,
      userData: ec2.UserData.forLinux(),
      role: new iam.Role(this, 'EcsInstanceRole', {
        assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
        managedPolicies: [
          iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonEC2ContainerServiceforEC2Role'),
        ],
      }),
    });

    // Add User Data to match Terraform
    launchTemplate.userData?.addCommands(`echo ECS_CLUSTER=${cluster.clusterName} >> /etc/ecs/ecs.config`);

    // Add Capacity (ASG) using Launch Template
    const asg = new autoscaling.AutoScalingGroup(this, 'ASG', {
      vpc,
      autoScalingGroupName: `${projectName}-asg`,
      minCapacity: 1,
      maxCapacity: 2,
      vpcSubnets: { subnetType: ec2.SubnetType.PUBLIC }, // Hosts in public subnet per Terraform
      newInstancesProtectedFromScaleIn: false,
      launchTemplate: launchTemplate,
    });

    // Note: We already added user data to the Launch Template, so we don't need to add it to the ASG directly.

    const capacityProvider = new ecs.AsgCapacityProvider(this, 'AsgCapacityProvider', {
      autoScalingGroup: asg,
      capacityProviderName: `${projectName}-capacity-provider`,
      enableManagedScaling: true,
      enableManagedTerminationProtection: false,
    });
    
    cluster.addAsgCapacityProvider(capacityProvider);

    // 6. ALB
    const alb = new elbv2.ApplicationLoadBalancer(this, 'ALB', {
      vpc,
      internetFacing: true,
      loadBalancerName: `${projectName}-alb`,
      securityGroup: albSg,
      vpcSubnets: { subnetType: ec2.SubnetType.PUBLIC },
    });

    const httpListener = alb.addListener('HttpListener', {
      port: 80,
      open: true,
    });

    // Log Group
    const logGroup = new logs.LogGroup(this, 'LogGroup', {
      logGroupName: `/ecs/${projectName}`,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      retention: logs.RetentionDays.ONE_WEEK,
    });

    // Shared Execution Role logic
    const executionRole = new iam.Role(this, 'ExecutionRole', {
      assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
      roleName: `${projectName}-execution-role-cdk`, // Suffix to avoid conflict if TF exists
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonECSTaskExecutionRolePolicy'),
      ],
    });
    
    // Grant access to Secrets
    mongoSecret.grantRead(executionRole);
    jwtSecret.grantRead(executionRole);

    const taskRole = new iam.Role(this, 'TaskRole', {
      assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
      roleName: `${projectName}-task-role-cdk`,
    });

    // --- Services ---

    // Deployment Configuration
    // If 'initialDeploy' context is true, we set desiredCount to 0.
    // This allows the stack to deploy successfully without waiting for images (which don't exist yet).
    // After the pipeline runs and pushes images, the user must scale up the services.
    const isInitialDeploy = this.node.tryGetContext('initialDeploy') === 'true';
    const defaultDesiredCount = isInitialDeploy ? 0 : 2; // UI/Exec default
    const singleDesiredCount = isInitialDeploy ? 0 : 1;  // Auth/Meta default

    // UI Service
    const uiTaskDef = new ecs.Ec2TaskDefinition(this, 'UiTaskDef', {
      family: `${projectName}-ui`,
      networkMode: ecs.NetworkMode.BRIDGE,
      executionRole,
      taskRole,
    });

    const uiContainer = uiTaskDef.addContainer('ui', {
      image: ecs.ContainerImage.fromEcrRepository(uiRepo, 'latest'),
      cpu: 256,
      memoryLimitMiB: 256,
      logging: ecs.LogDrivers.awsLogs({
        streamPrefix: 'ui',
        logGroup,
      }),
    });
    uiContainer.addPortMappings({ containerPort: 80 });

    const uiService = new ecs.Ec2Service(this, 'UiService', {
      serviceName: `${projectName}-ui`,
      cluster,
      taskDefinition: uiTaskDef,
      desiredCount: defaultDesiredCount,
      capacityProviderStrategies: [
        { capacityProvider: capacityProvider.capacityProviderName, weight: 100, base: 1 }
      ]
    });

    // Auth Service
    const authTaskDef = new ecs.Ec2TaskDefinition(this, 'AuthTaskDef', {
      family: `${projectName}-auth`,
      networkMode: ecs.NetworkMode.BRIDGE,
      executionRole,
      taskRole,
    });

    const authContainer = authTaskDef.addContainer('auth', {
      image: ecs.ContainerImage.fromEcrRepository(authRepo, 'latest'),
      cpu: 256,
      memoryLimitMiB: 256,
      environment: {
        'DATABASE_NAME': 'dynaman_auth',
      },
      secrets: {
        'MONGODB_URL': ecs.Secret.fromSecretsManager(mongoSecret),
        'SECRET_KEY': ecs.Secret.fromSecretsManager(jwtSecret),
      },
      logging: ecs.LogDrivers.awsLogs({
        streamPrefix: 'auth',
        logGroup,
      }),
    });
    authContainer.addPortMappings({ containerPort: 8000 });

    const authService = new ecs.Ec2Service(this, 'AuthService', {
      serviceName: `${projectName}-auth`,
      cluster,
      taskDefinition: authTaskDef,
      desiredCount: singleDesiredCount,
      capacityProviderStrategies: [
        { capacityProvider: capacityProvider.capacityProviderName, weight: 100, base: 1 }
      ]
    });

    // Engine Metadata Service
    const metaTaskDef = new ecs.Ec2TaskDefinition(this, 'MetaTaskDef', {
      family: `${projectName}-meta`,
      networkMode: ecs.NetworkMode.BRIDGE,
      executionRole,
      taskRole,
    });

    const metaContainer = metaTaskDef.addContainer('meta', {
      image: ecs.ContainerImage.fromEcrRepository(engineRepo, 'latest'),
      cpu: 256,
      memoryLimitMiB: 256,
      environment: {
        'DATABASE_NAME': 'dynaman',
        'APP_MODE': 'metadata',
      },
      secrets: {
        'MONGODB_URL': ecs.Secret.fromSecretsManager(mongoSecret),
        'SECRET_KEY': ecs.Secret.fromSecretsManager(jwtSecret),
      },
      logging: ecs.LogDrivers.awsLogs({
        streamPrefix: 'meta',
        logGroup,
      }),
    });
    metaContainer.addPortMappings({ containerPort: 8000 });

    const metaService = new ecs.Ec2Service(this, 'MetaService', {
      serviceName: `${projectName}-meta`,
      cluster,
      taskDefinition: metaTaskDef,
      desiredCount: singleDesiredCount,
      capacityProviderStrategies: [
        { capacityProvider: capacityProvider.capacityProviderName, weight: 100, base: 1 }
      ]
    });

    // Engine Execution Service
    const execTaskDef = new ecs.Ec2TaskDefinition(this, 'ExecTaskDef', {
      family: `${projectName}-exec`,
      networkMode: ecs.NetworkMode.BRIDGE,
      executionRole,
      taskRole,
    });

    const execContainer = execTaskDef.addContainer('exec', {
      image: ecs.ContainerImage.fromEcrRepository(engineRepo, 'latest'),
      cpu: 256,
      memoryLimitMiB: 256,
      environment: {
        'DATABASE_NAME': 'dynaman',
        'APP_MODE': 'execution',
      },
      secrets: {
        'MONGODB_URL': ecs.Secret.fromSecretsManager(mongoSecret),
        'SECRET_KEY': ecs.Secret.fromSecretsManager(jwtSecret),
      },
      logging: ecs.LogDrivers.awsLogs({
        streamPrefix: 'exec',
        logGroup,
      }),
    });
    execContainer.addPortMappings({ containerPort: 8000 });

    const execService = new ecs.Ec2Service(this, 'ExecService', {
      serviceName: `${projectName}-exec`,
      cluster,
      taskDefinition: execTaskDef,
      desiredCount: defaultDesiredCount,
      capacityProviderStrategies: [
        { capacityProvider: capacityProvider.capacityProviderName, weight: 100, base: 1 }
      ]
    });

    // --- Routing ---
    
    // Default -> UI
    httpListener.addTargets('UiTarget', {
      port: 80,
      targets: [uiService],
      healthCheck: { path: '/' }
    });

    // Auth -> /api/v1/auth/*
    httpListener.addTargets('AuthTarget', {
      priority: 100,
      conditions: [elbv2.ListenerCondition.pathPatterns(['/api/v1/auth/*'])],
      port: 8000,
      targets: [authService],
      healthCheck: { path: '/health' }
    });

    // Meta -> /api/v1/schemas/*
    httpListener.addTargets('MetaTarget', {
      priority: 110,
      conditions: [elbv2.ListenerCondition.pathPatterns(['/api/v1/schemas/*'])],
      port: 8000,
      targets: [metaService],
      healthCheck: { path: '/api/v1/schemas/openapi.json' }
    });

    // Exec -> /api/v1/data/*
    httpListener.addTargets('ExecTarget', {
      priority: 120,
      conditions: [elbv2.ListenerCondition.pathPatterns(['/api/v1/data/*'])],
      port: 8000,
      targets: [execService],
      healthCheck: { path: '/api/v1/data/openapi.json' }
    });

    // Outputs
    new cdk.CfnOutput(this, 'AlbDnsName', {
      value: alb.loadBalancerDnsName,
      description: 'ALB DNS Name',
    });

    // --- CI/CD Pipeline ---
    // Requires: githubRepoOwner, githubRepoName
    const githubRepoOwner = this.node.tryGetContext('githubRepoOwner');
    const githubRepoName = this.node.tryGetContext('githubRepoName');
    const githubBranch = this.node.tryGetContext('githubBranch') || 'main';

    if (githubRepoOwner && githubRepoName) {
      
      // 1. Artifact Bucket
      const artifactBucket = new s3.Bucket(this, 'ArtifactBucket', {
        bucketName: `${projectName}-pipeline-artifacts-${this.region}-${this.account}`,
        removalPolicy: cdk.RemovalPolicy.DESTROY,
        autoDeleteObjects: true,
      });

      // 2. CodeStar Connection (GitHub)
      // Note: This will be created in PENDING state. You must visit the AWS Console 
      // (Developer Tools > Connections) to complete the handshake.
      const connection = new codestar.CfnConnection(this, 'GithubConnection', {
        connectionName: `${projectName}-github`,
        providerType: 'GitHub',
      });

      // 3. CodeBuild Project
      const buildProject = new codebuild.PipelineProject(this, 'BuildProject', {
        projectName: `${projectName}-build`,
        environment: {
          buildImage: codebuild.LinuxBuildImage.AMAZON_LINUX_2_ARM_3, // Match Terraform ARM_CONTAINER
          privileged: true,
          computeType: codebuild.ComputeType.SMALL,
          environmentVariables: {
            AWS_DEFAULT_REGION: { value: this.region },
            AWS_ACCOUNT_ID: { value: this.account },
            IMAGE_REPO_UI: { value: uiRepo.repositoryUri },
            IMAGE_REPO_AUTH: { value: authRepo.repositoryUri },
            IMAGE_REPO_ENGINE: { value: engineRepo.repositoryUri },
          },
        },
        buildSpec: codebuild.BuildSpec.fromSourceFilename('buildspec.yml'),
      });

      // Grant ECR Permissions to CodeBuild
      uiRepo.grantPullPush(buildProject);
      authRepo.grantPullPush(buildProject);
      engineRepo.grantPullPush(buildProject);

      // 4. CodePipeline
      const sourceOutput = new codepipeline.Artifact();
      const buildOutput = new codepipeline.Artifact();

      new codepipeline.Pipeline(this, 'Pipeline', {
        pipelineName: `${projectName}-pipeline`,
        artifactBucket: artifactBucket,
        stages: [
          {
            stageName: 'Source',
            actions: [
              new codepipeline_actions.CodeStarConnectionsSourceAction({
                actionName: 'Source',
                connectionArn: connection.attrConnectionArn,
                output: sourceOutput,
                repo: githubRepoName,
                branch: githubBranch,
                owner: githubRepoOwner, // Note: owner parameter is deprecated in newer CDK versions in favor of just repo/branch context from connection, but kept for clarity/compat.
              }),
            ],
          },
          {
            stageName: 'Build',
            actions: [
              new codepipeline_actions.CodeBuildAction({
                actionName: 'Build',
                project: buildProject,
                input: sourceOutput,
                outputs: [buildOutput],
              }),
            ],
          },
          {
            stageName: 'Deploy',
            actions: [
              new codepipeline_actions.EcsDeployAction({
                actionName: 'DeployUI',
                service: uiService,
                imageFile: new codepipeline.ArtifactPath(buildOutput, 'imagedefinitions_ui.json'),
              }),
              new codepipeline_actions.EcsDeployAction({
                actionName: 'DeployAuth',
                service: authService,
                imageFile: new codepipeline.ArtifactPath(buildOutput, 'imagedefinitions_auth.json'),
              }),
              new codepipeline_actions.EcsDeployAction({
                actionName: 'DeployMeta',
                service: metaService,
                imageFile: new codepipeline.ArtifactPath(buildOutput, 'imagedefinitions_meta.json'),
              }),
              new codepipeline_actions.EcsDeployAction({
                actionName: 'DeployExec',
                service: execService,
                imageFile: new codepipeline.ArtifactPath(buildOutput, 'imagedefinitions_exec.json'),
              }),
            ],
          },
        ],
      });
    }
  }
}
