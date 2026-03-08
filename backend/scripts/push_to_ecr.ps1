# Push Adhi backend Docker image to Amazon ECR
# Run from: e:\RootedAI\SAAS\Adhi-AI-Compliance\backend\
# Prerequisites: Docker Desktop running, AWS CLI installed and configured (aws configure)
#
# Usage: .\scripts\push_to_ecr.ps1 -AccountId 123456789012 -Region ap-south-2

param(
    [Parameter(Mandatory=$true)]
    [string]$AccountId,
    [string]$Region = "ap-south-2",
    [string]$RepoName = "adhi-backend",
    [string]$Tag = "latest"
)

$ECR_URI = "$AccountId.dkr.ecr.$Region.amazonaws.com"
$IMAGE   = "$ECR_URI/${RepoName}:$Tag"

Write-Host "`n===================================================" -ForegroundColor Cyan
Write-Host "  Adhi Backend — ECR Push Script" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Account : $AccountId"
Write-Host "  Region  : $Region"
Write-Host "  Image   : $IMAGE"
Write-Host ""

# Step 1 — Create ECR repo (safe to run if already exists)
Write-Host "[1] Creating ECR repository (skipped if already exists)..." -ForegroundColor Yellow
aws ecr create-repository --repository-name $RepoName --region $Region 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "    ✅ Repository created" -ForegroundColor Green
} else {
    Write-Host "    ℹ️  Repository already exists — continuing" -ForegroundColor DarkCyan
}

# Step 2 — Docker login to ECR
Write-Host "[2] Logging in to ECR..." -ForegroundColor Yellow
$loginPwd = aws ecr get-login-password --region $Region
$loginPwd | docker login --username AWS --password-stdin $ECR_URI
if ($LASTEXITCODE -ne 0) { Write-Host "❌ ECR login failed" -ForegroundColor Red; exit 1 }
Write-Host "    ✅ Logged in" -ForegroundColor Green

# Step 3 — Build Docker image
Write-Host "[3] Building Docker image..." -ForegroundColor Yellow
docker build -t "${RepoName}:$Tag" .
if ($LASTEXITCODE -ne 0) { Write-Host "❌ Docker build failed" -ForegroundColor Red; exit 1 }
Write-Host "    ✅ Image built" -ForegroundColor Green

# Step 4 — Tag and push
Write-Host "[4] Tagging and pushing to ECR..." -ForegroundColor Yellow
docker tag "${RepoName}:$Tag" $IMAGE
docker push $IMAGE
if ($LASTEXITCODE -ne 0) { Write-Host "❌ Docker push failed" -ForegroundColor Red; exit 1 }

Write-Host ""
Write-Host "===================================================" -ForegroundColor Green
Write-Host "  ✅ Image pushed successfully!" -ForegroundColor Green
Write-Host "  ECR URI: $IMAGE" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Next: Create App Runner service in AWS Console" -ForegroundColor Cyan
Write-Host "  Container image URI: $IMAGE" -ForegroundColor Cyan
Write-Host "  Port: 8080" -ForegroundColor Cyan
