#!/bin/bash
# EC2 User Data Script â€” Adhi AI Compliance Backend
# Paste this entire script into: EC2 â†’ Advanced details â†’ User data
# âš ï¸ Replace YOUR_AWS_ACCESS_KEY_ID and YOUR_AWS_SECRET_ACCESS_KEY before pasting!
# Works with: Amazon Linux 2023 (Free tier eligible)

set -e

# 1. System update + install Docker & AWS CLI
dnf update -y
dnf install -y docker aws-cli unzip curl

# 2. Start Docker
systemctl start docker
systemctl enable docker
usermod -aG docker ec2-user

# 3. Write environment file
cat > /home/ec2-user/adhi.env << 'EOF'
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD_HERE@adhi-compliance-db.chq0mqkqaozv.ap-south-2.rds.amazonaws.com:5432/postgres
REDIS_URL=rediss://adhi-cache-plc4pl.serverless.aps1.cache.amazonaws.com:6379
AWS_ACCESS_KEY_ID=REPLACE_WITH_YOUR_KEY
AWS_SECRET_ACCESS_KEY=REPLACE_WITH_YOUR_SECRET
AWS_REGION=ap-south-2
AWS_S3_BUCKET=adhi-compliance-storage
LLM_PROVIDER=bedrock
STORAGE_BACKEND=s3
AWS_BEDROCK_REGION=ap-south-1
AWS_BEDROCK_CHAT_MODEL_ID=apac.anthropic.claude-3-5-sonnet-20241022-v2:0
AWS_BEDROCK_EMBED_MODEL_ID=amazon.titan-embed-text-v2:0
SUPABASE_URL=https://[REDACTED_PROJECT_ID].supabase.co
SUPABASE_ANON_KEY=REPLACE_WITH_YOUR_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY=REPLACE_WITH_YOUR_SERVICE_KEY
SARVAM_API_KEY=REPLACE_WITH_YOUR_SARVAM_API_KEY
ALLOWED_ORIGINS=*
APP_HOST=0.0.0.0
APP_PORT=8080
EOF

chown ec2-user:ec2-user /home/ec2-user/adhi.env

# 4. ECR login + pull image
ECR=247129201143.dkr.ecr.ap-south-2.amazonaws.com
IMAGE=$ECR/adhi-backend:latest

aws configure set aws_access_key_id     REPLACE_WITH_YOUR_KEY
aws configure set aws_secret_access_key REPLACE_WITH_YOUR_SECRET
aws configure set default.region        ap-south-2

aws ecr get-login-password --region ap-south-2 | \
    docker login --username AWS --password-stdin $ECR

docker pull $IMAGE

# 5. Run container
docker run -d \
    --name adhi-backend \
    --restart unless-stopped \
    -p 8000:8080 \
    --env-file /home/ec2-user/adhi.env \
    $IMAGE

echo "âœ… Adhi backend container started on port 8000"

