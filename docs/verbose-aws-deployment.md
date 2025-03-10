<think>The user wants me to write the steps necessary to deploy the application to AWS based on our AWS deployment specification document. I'll extract and organize the deployment steps from the AWS specification we created earlier, making them clear and actionable.

The main AWS services we'll be using according to the spec are:
1. AWS Amplify for the Next.js frontend
2. AWS ECS (Elastic Container Service) for the Flask backend
3. Amazon RDS for PostgreSQL database
4. AWS Secrets Manager for secrets
5. S3 for file storage
6. CloudFront for CDN

I'll organize the steps in a logical order for deployment, starting with setting up the foundational infrastructure and then deploying the application components.</think># AWS Deployment Steps for Contact Management Application

Based on our AWS deployment specification, here's a step-by-step guide to deploy the application to AWS:

## Prerequisites

1. Install and configure the required tools:
   ```bash
   # Install AWS CLI
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   
   # Configure AWS CLI with your credentials
   aws configure
   
   # Install Docker if not already installed
   sudo apt-get update
   sudo apt-get install docker.io
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

2. Create a GitHub repository (if not already done) and push your code there

## Step 1: Set Up the Network Infrastructure

1. Create a VPC with public and private subnets:
   ```bash
   # Create VPC
   vpc_id=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 --query 'Vpc.VpcId' --output text)
   aws ec2 create-tags --resources $vpc_id --tags Key=Name,Value=contacts-vpc
   
   # Create subnets
   public_subnet_1=$(aws ec2 create-subnet --vpc-id $vpc_id --cidr-block 10.0.1.0/24 --availability-zone us-east-1a --query 'Subnet.SubnetId' --output text)
   public_subnet_2=$(aws ec2 create-subnet --vpc-id $vpc_id --cidr-block 10.0.2.0/24 --availability-zone us-east-1b --query 'Subnet.SubnetId' --output text)
   private_subnet_1=$(aws ec2 create-subnet --vpc-id $vpc_id --cidr-block 10.0.3.0/24 --availability-zone us-east-1a --query 'Subnet.SubnetId' --output text)
   private_subnet_2=$(aws ec2 create-subnet --vpc-id $vpc_id --cidr-block 10.0.4.0/24 --availability-zone us-east-1b --query 'Subnet.SubnetId' --output text)
   
   # Create and configure Internet Gateway
   igw_id=$(aws ec2 create-internet-gateway --query 'InternetGateway.InternetGatewayId' --output text)
   aws ec2 attach-internet-gateway --internet-gateway-id $igw_id --vpc-id $vpc_id
   
   # Create route tables and associate with subnets
   public_rt=$(aws ec2 create-route-table --vpc-id $vpc_id --query 'RouteTable.RouteTableId' --output text)
   aws ec2 create-route --route-table-id $public_rt --destination-cidr-block 0.0.0.0/0 --gateway-id $igw_id
   aws ec2 associate-route-table --route-table-id $public_rt --subnet-id $public_subnet_1
   aws ec2 associate-route-table --route-table-id $public_rt --subnet-id $public_subnet_2
   ```

2. Create security groups:
   ```bash
   # Create security group for RDS
   db_sg=$(aws ec2 create-security-group --group-name contacts-db-sg --description "Security group for RDS" --vpc-id $vpc_id --query 'GroupId' --output text)
   
   # Create security group for ECS
   ecs_sg=$(aws ec2 create-security-group --group-name contacts-ecs-sg --description "Security group for ECS" --vpc-id $vpc_id --query 'GroupId' --output text)
   
   # Create security group for ALB
   alb_sg=$(aws ec2 create-security-group --group-name contacts-alb-sg --description "Security group for ALB" --vpc-id $vpc_id --query 'GroupId' --output text)
   
   # Configure security group rules
   aws ec2 authorize-security-group-ingress --group-id $alb_sg --protocol tcp --port 80 --cidr 0.0.0.0/0
   aws ec2 authorize-security-group-ingress --group-id $alb_sg --protocol tcp --port 443 --cidr 0.0.0.0/0
   aws ec2 authorize-security-group-ingress --group-id $ecs_sg --protocol tcp --port 5000 --source-group $alb_sg
   aws ec2 authorize-security-group-ingress --group-id $db_sg --protocol tcp --port 5432 --source-group $ecs_sg
   ```

## Step 2: Create AWS Secrets Manager Secrets

1. Store application secrets:
   ```bash
   # Store database credentials
   aws secretsmanager create-secret \
     --name contacts/db-url \
     --description "Connection string for the contacts database" \
     --secret-string "postgresql://dbadmin:PASSWORD@contacts-db.cluster-identifier.region.rds.amazonaws.com:5432/contacts_db"
   
   # Store application secret key
   aws secretsmanager create-secret \
     --name contacts/secret-key \
     --description "Secret key for the Flask application" \
     --secret-string "your-secret-key-here"
   
   # Store JWT secret key
   aws secretsmanager create-secret \
     --name contacts/jwt-secret \
     --description "JWT secret key for authentication" \
     --secret-string "your-jwt-secret-key-here"
   ```

## Step 3: Set Up Amazon RDS for PostgreSQL

1. Create a DB subnet group:
   ```bash
   aws rds create-db-subnet-group \
     --db-subnet-group-name contacts-db-subnet \
     --db-subnet-group-description "Subnet group for contacts DB" \
     --subnet-ids "$private_subnet_1 $private_subnet_2"
   ```

2. Create the RDS instance:
   ```bash
   aws rds create-db-instance \
     --db-instance-identifier contacts-db \
     --db-instance-class db.t3.medium \
     --engine postgres \
     --engine-version 16.1 \
     --allocated-storage 20 \
     --max-allocated-storage 100 \
     --master-username dbadmin \
     --master-user-password "PASSWORD" \
     --db-subnet-group-name contacts-db-subnet \
     --vpc-security-group-ids $db_sg \
     --backup-retention-period 7 \
     --multi-az \
     --storage-type gp2 \
     --no-publicly-accessible
   ```

## Step 4: Set Up S3 Bucket for File Storage

1. Create an S3 bucket:
   ```bash
   aws s3api create-bucket \
     --bucket contacts-app-files-$(aws sts get-caller-identity --query Account --output text) \
     --region us-east-1
   
   # Enable server-side encryption
   aws s3api put-bucket-encryption \
     --bucket contacts-app-files-$(aws sts get-caller-identity --query Account --output text) \
     --server-side-encryption-configuration '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'
   ```

## Step 5: Deploy the Backend to ECS

1. Create an ECR repository:
   ```bash
   aws ecr create-repository --repository-name contacts-api
   ```

2. Build and push Docker image:
   ```bash
   # Get login token
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com
   
   # Build and tag the image
   cd /Users/imac/contacts/backend
   docker build -t contacts-api .
   docker tag contacts-api:latest $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/contacts-api:latest
   
   # Push the image
   docker push $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/contacts-api:latest
   ```

3. Create IAM roles:
   ```bash
   # Create ECS task execution role
   aws iam create-role \
     --role-name ecsTaskExecutionRole \
     --assume-role-policy-document file://ecs-task-execution-role.json
   
   aws iam attach-role-policy \
     --role-name ecsTaskExecutionRole \
     --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
   
   # Create role for the task to access other AWS resources
   aws iam create-role \
     --role-name contacts-api-task-role \
     --assume-role-policy-document file://ecs-task-role.json
   
   aws iam attach-role-policy \
     --role-name contacts-api-task-role \
     --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
   
   aws iam attach-role-policy \
     --role-name contacts-api-task-role \
     --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite
   ```

4. Create task definition (save the following as `task-definition.json`):
   ```json
   {
     "family": "contacts-api",
     "executionRoleArn": "arn:aws:iam::ACCOUNT_ID:role/ecsTaskExecutionRole",
     "taskRoleArn": "arn:aws:iam::ACCOUNT_ID:role/contacts-api-task-role",
     "networkMode": "awsvpc",
     "containerDefinitions": [
       {
         "name": "contacts-api",
         "image": "ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/contacts-api:latest",
         "essential": true,
         "portMappings": [
           {
             "containerPort": 5000,
             "hostPort": 5000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "FLASK_ENV",
             "value": "production"
           }
         ],
         "secrets": [
           {
             "name": "DATABASE_URL",
             "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:contacts/db-url"
           },
           {
             "name": "SECRET_KEY",
             "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:contacts/secret-key"
           },
           {
             "name": "JWT_SECRET_KEY",
             "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:contacts/jwt-secret"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/contacts-api",
             "awslogs-region": "REGION",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ],
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "512",
     "memory": "1024"
   }
   ```

   ```bash
   # Replace placeholders in the task definition
   sed -i "s/ACCOUNT_ID/$(aws sts get-caller-identity --query Account --output text)/g" task-definition.json
   sed -i "s/REGION/us-east-1/g" task-definition.json
   
   # Register the task definition
   aws ecs register-task-definition --cli-input-json file://task-definition.json
   ```

5. Create a CloudWatch log group:
   ```bash
   aws logs create-log-group --log-group-name /ecs/contacts-api
   ```

6. Create an Application Load Balancer:
   ```bash
   # Create ALB
   alb_arn=$(aws elbv2 create-load-balancer \
     --name contacts-alb \
     --subnets $public_subnet_1 $public_subnet_2 \
     --security-groups $alb_sg \
     --query 'LoadBalancers[0].LoadBalancerArn' \
     --output text)
   
   # Create target group
   tg_arn=$(aws elbv2 create-target-group \
     --name contacts-api-tg \
     --protocol HTTP \
     --port 5000 \
     --vpc-id $vpc_id \
     --target-type ip \
     --health-check-path "/api/health" \
     --health-check-interval-seconds 30 \
     --health-check-timeout-seconds 5 \
     --healthy-threshold-count 2 \
     --unhealthy-threshold-count 3 \
     --query 'TargetGroups[0].TargetGroupArn' \
     --output text)
   
   # Create HTTP listener (redirect to HTTPS)
   aws elbv2 create-listener \
     --load-balancer-arn $alb_arn \
     --protocol HTTP \
     --port 80 \
     --default-actions Type=redirect,RedirectConfig='{Protocol=HTTPS,Port=443,StatusCode=HTTP_301}'
   
   # Create HTTPS listener
   aws elbv2 create-listener \
     --load-balancer-arn $alb_arn \
     --protocol HTTPS \
     --port 443 \
     --certificates CertificateArn=arn:aws:acm:REGION:ACCOUNT_ID:certificate/your-certificate-id \
     --default-actions Type=forward,TargetGroupArn=$tg_arn
   ```

7. Create an ECS cluster:
   ```bash
   aws ecs create-cluster --cluster-name contacts-cluster
   ```

8. Create an ECS service:
   ```bash
   aws ecs create-service \
     --cluster contacts-cluster \
     --service-name contacts-api-service \
     --task-definition contacts-api:1 \
     --desired-count 2 \
     --launch-type FARGATE \
     --platform-version LATEST \
     --network-configuration "awsvpcConfiguration={subnets=[$private_subnet_1,$private_subnet_2],securityGroups=[$ecs_sg],assignPublicIp=DISABLED}" \
     --load-balancers "targetGroupArn=$tg_arn,containerName=contacts-api,containerPort=5000" \
     --health-check-grace-period-seconds 60 \
     --deployment-configuration "minimumHealthyPercent=100,maximumPercent=200" \
     --enable-execute-command
   ```

## Step 6: Set Up Database Migrations

1. Create a migration task definition:
   ```bash
   # Create a JSON file named migrations-task-definition.json with similar config as the main task, but with a different command
   cat > migrations-task-definition.json << 'EOF'
   {
     "family": "contacts-api-migrations",
     "executionRoleArn": "arn:aws:iam::ACCOUNT_ID:role/ecsTaskExecutionRole",
     "taskRoleArn": "arn:aws:iam::ACCOUNT_ID:role/contacts-api-task-role",
     "networkMode": "awsvpc",
     "containerDefinitions": [
       {
         "name": "migrations",
         "image": "ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/contacts-api:latest",
         "essential": true,
         "command": ["flask", "db", "upgrade"],
         "environment": [
           {
             "name": "FLASK_ENV",
             "value": "production"
           }
         ],
         "secrets": [
           {
             "name": "DATABASE_URL",
             "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:contacts/db-url"
           },
           {
             "name": "SECRET_KEY",
             "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:contacts/secret-key"
           },
           {
             "name": "JWT_SECRET_KEY",
             "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:contacts/jwt-secret"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/contacts-api-migrations",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ],
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "256",
     "memory": "512"
   }
   EOF
   
   # Replace placeholders
   sed -i "s/ACCOUNT_ID/$(aws sts get-caller-identity --query Account --output text)/g" migrations-task-definition.json
   
   # Register the task definition
   aws ecs register-task-definition --cli-input-json file://migrations-task-definition.json
   
   # Create a log group for migrations
   aws logs create-log-group --log-group-name /ecs/contacts-api-migrations
   
   # Run the migrations task
   aws ecs run-task \
     --cluster contacts-cluster \
     --task-definition contacts-api-migrations:1 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[$private_subnet_1],securityGroups=[$ecs_sg],assignPublicIp=DISABLED}"
   ```

## Step 7: Deploy Frontend to AWS Amplify

1. Create an amplify.yml file in the root of your frontend directory:
   ```yaml
   version: 1
   frontend:
     phases:
       preBuild:
         commands:
           - cd frontend
           - yarn install
       build:
         commands:
           - yarn build
     artifacts:
       baseDirectory: frontend/.next
       files:
         - '**/*'
     cache:
       paths:
         - frontend/node_modules/**/*
   ```

2. Deploy via the AWS Amplify Console:
   - Go to the AWS Amplify Console in your browser
   - Click "Connect app"
   - Select GitHub as the repository source
   - Authenticate with GitHub and select your repository
   - Set the base directory to `frontend` 
   - Set the build settings using the amplify.yml file
   - Add environment variables:
     - `NEXT_PUBLIC_API_URL`: The URL of your ALB (e.g., https://contacts-alb-12345.us-east-1.elb.amazonaws.com)
   - Click "Save and deploy"

## Step 8: Configure CloudFront Distribution for Frontend

1. Create a CloudFront distribution:
   ```bash
   aws cloudfront create-distribution \
     --origin-domain-name $(aws amplify get-app --app-id YOUR_AMPLIFY_APP_ID --query 'app.defaultDomain' --output text) \
     --default-root-object index.html \
     --enabled \
     --default-cache-behavior '{"TargetOriginId":"amplify","ViewerProtocolPolicy":"redirect-to-https","AllowedMethods":{"Quantity":3,"Items":["HEAD","GET","OPTIONS"],"CachedMethods":{"Quantity":2,"Items":["HEAD","GET"]}},"ForwardedValues":{"QueryString":true,"Cookies":{"Forward":"none"},"Headers":{"Quantity":1,"Items":["Origin"]}},"MinTTL":0,"DefaultTTL":3600,"MaxTTL":86400}' \
     --price-class PriceClass_100
   ```

## Step 9: Set Up Auto-Scaling

1. Configure auto-scaling for ECS:
   ```bash
   # Create an auto-scaling target
   aws application-autoscaling register-scalable-target \
     --service-namespace ecs \
     --scalable-dimension ecs:service:DesiredCount \
     --resource-id service/contacts-cluster/contacts-api-service \
     --min-capacity 2 \
     --max-capacity 10
   
   # Create a scaling policy based on CPU utilization
   aws application-autoscaling put-scaling-policy \
     --service-namespace ecs \
     --scalable-dimension ecs:service:DesiredCount \
     --resource-id service/contacts-cluster/contacts-api-service \
     --policy-name cpu-tracking-scaling-policy \
     --policy-type TargetTrackingScaling \
     --target-tracking-scaling-policy-configuration '{"TargetValue":70.0,"PredefinedMetricSpecification":{"PredefinedMetricType":"ECSServiceAverageCPUUtilization"},"ScaleOutCooldown":60,"ScaleInCooldown":60}'
   ```

## Step 10: Set Up Monitoring and Alarms

1. Create CloudWatch alarms:
   ```bash
   # CPU Utilization alarm
   aws cloudwatch put-metric-alarm \
     --alarm-name contacts-api-high-cpu \
     --alarm-description "Alarm when CPU exceeds 80% for 5 minutes" \
     --metric-name CPUUtilization \
     --namespace AWS/ECS \
     --statistic Average \
     --period 300 \
     --threshold 80 \
     --comparison-operator GreaterThanThreshold \
     --dimensions Name=ClusterName,Value=contacts-cluster Name=ServiceName,Value=contacts-api-service \
     --evaluation-periods 1 \
     --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:alerts-topic
   
   # 5XX Error Rate alarm
   aws cloudwatch put-metric-alarm \
     --alarm-name contacts-api-high-5xx \
     --alarm-description "Alarm when 5XX error rate exceeds 5% for 5 minutes" \
     --metric-name HTTPCode_Target_5XX_Count \
     --namespace AWS/ApplicationELB \
     --statistic Sum \
     --period 300 \
     --threshold 5 \
     --comparison-operator GreaterThanThreshold \
     --dimensions Name=LoadBalancer,Value=$alb_arn Name=TargetGroup,Value=$tg_arn \
     --evaluation-periods 1 \
     --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:alerts-topic
   ```

## Step 11: Set Up CI/CD Pipeline with AWS CodePipeline

1. Create a CodePipeline for automated deployments:
   ```bash
   # Create S3 bucket for pipeline artifacts
   aws s3api create-bucket \
     --bucket contacts-pipeline-artifacts-$(aws sts get-caller-identity --query Account --output text) \
     --region us-east-1
   
   # Create IAM role for CodePipeline
   aws iam create-role \
     --role-name contacts-codepipeline-role \
     --assume-role-policy-document file://codepipeline-role.json
   
   aws iam attach-role-policy \
     --role-name contacts-codepipeline-role \
     --policy-arn arn:aws:iam::aws:policy/AWSCodeBuildAdminAccess
   
   aws iam attach-role-policy \
     --role-name contacts-codepipeline-role \
     --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
   
   aws iam attach-role-policy \
     --role-name contacts-codepipeline-role \
     --policy-arn arn:aws:iam::aws:policy/AmazonECR-FullAccess
   
   aws iam attach-role-policy \
     --role-name contacts-codepipeline-role \
     --policy-arn arn:aws:iam::aws:policy/AmazonECS-FullAccess
   
   # Create codebuild project (backend)
   aws codebuild create-project \
     --name contacts-api-build \
     --source type=GITHUB,location=https://github.com/username/contacts.git \
     --artifacts type=CODEPIPELINE \
     --environment type=LINUX_CONTAINER,image=aws/codebuild/amazonlinux2-x86_64-standard:3.0,computeType=BUILD_GENERAL1_SMALL,privilegedMode=true \
     --service-role codebuild-service-role
   
   # Create pipeline
   aws codepipeline create-pipeline \
     --pipeline-name contacts-pipeline \
     --role-arn arn:aws:iam::ACCOUNT_ID:role/contacts-codepipeline-role \
     --artifact-store type=S3,location=contacts-pipeline-artifacts-$(aws sts get-caller-identity --query Account --output text) \
     --stages '[
       {
         "name": "Source",
         "actions": [
           {
             "name": "Source",
             "actionTypeId": {
               "category": "Source",
               "owner": "AWS",
               "provider": "CodeStarSourceConnection",
               "version": "1"
             },
             "configuration": {
               "ConnectionArn": "arn:aws:codestar-connections:us-east-1:ACCOUNT_ID:connection/your-connection-id",
               "FullRepositoryId": "username/contacts",
               "BranchName": "main"
             },
             "outputArtifacts": [
               {
                 "name": "SourceCode"
               }
             ]
           }
         ]
       },
       {
         "name": "BuildBackend",
         "actions": [
           {
             "name": "BuildAndPushImage",
             "actionTypeId": {
               "category": "Build",
               "owner": "AWS",
               "provider": "CodeBuild",
               "version": "1"
             },
             "configuration": {
               "ProjectName": "contacts-api-build"
             },
             "inputArtifacts": [
               {
                 "name": "SourceCode"
               }
             ],
             "outputArtifacts": [
               {
                 "name": "BuildOutput"
               }
             ]
           }
         ]
       },
       {
         "name": "DeployBackend",
         "actions": [
           {
             "name": "DeployToECS",
             "actionTypeId": {
               "category": "Deploy",
               "owner": "AWS",
               "provider": "ECS",
               "version": "1"
             },
             "configuration": {
               "ClusterName": "contacts-cluster",
               "ServiceName": "contacts-api-service",
               "FileName": "imagedefinitions.json"
             },
             "inputArtifacts": [
               {
                 "name": "BuildOutput"
               }
             ]
           }
         ]
       }
     ]'
   ```

## Verification Steps

After deployment, verify that everything is working:

1. Test the backend API:
   ```bash
   curl -X GET https://your-alb-domain.us-east-1.elb.amazonaws.com/api/health
   ```

2. Browse to the frontend Amplify URL
   ```
   https://main.your-app-id.amplifyapp.com
   ```

3. Check CloudWatch logs for any errors
   ```bash
   aws logs get-log-events --log-group-name /ecs/contacts-api --log-stream-name the-latest-log-stream
   ```

4. Monitor CPU and memory usage of your ECS tasks
   ```bash
   aws cloudwatch get-metric-statistics --namespace AWS/ECS --metric-name CPUUtilization --dimensions Name=ClusterName,Value=contacts-cluster Name=ServiceName,Value=contacts-api-service --start-time $(date -d '1 hour ago' -u +%Y-%m-%dT%H:%M:%SZ) --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) --period 300 --statistics Average
   ```

These steps provide a comprehensive deployment process for your Contact Management Application on AWS according to the specification. Remember to replace placeholder values like ACCOUNT_ID, REGION, and connection/certificate ARNs with your actual values.
