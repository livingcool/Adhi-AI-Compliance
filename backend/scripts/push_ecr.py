"""
ECR Push Script (boto3-based, no AWS CLI required in PATH)
Run from backend/ directory:  py scripts/push_ecr.py
"""
import os, sys, subprocess, base64, json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env", override=True)

ACCOUNT_ID = "247129201143"
REGION     = "ap-south-2"      # Your RDS/resources region
REPO_NAME  = "adhi-backend"
TAG        = "latest"
ECR_URI    = f"{ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com"
IMAGE_FULL = f"{ECR_URI}/{REPO_NAME}:{TAG}"

import boto3
access_key = os.environ.get("AWS_ACCESS_KEY_ID")
secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
creds = {}
if access_key and secret_key:
    creds = {"aws_access_key_id": access_key, "aws_secret_access_key": secret_key}

def run(cmd, **kw):
    print(f"  $ {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, shell=isinstance(cmd, str), **kw)
    if result.returncode != 0:
        print(f"  ❌ Failed (exit {result.returncode})")
        sys.exit(result.returncode)
    return result

print("\n" + "=" * 55)
print("  Adhi Backend — ECR Push (boto3)")
print("=" * 55)
print(f"  Image: {IMAGE_FULL}\n")

ecr = boto3.client("ecr", region_name=REGION, **creds)

# 1. Create repo (ignore if exists)
print("[1] Ensuring ECR repository exists...")
try:
    ecr.create_repository(repositoryName=REPO_NAME)
    print("    ✅ Repository created")
except ecr.exceptions.RepositoryAlreadyExistsException:
    print("    ℹ️  Repository already exists")

# 2. Get ECR login token via boto3
print("[2] Getting ECR login token...")
token_resp = ecr.get_authorization_token()
auth_data  = token_resp["authorizationData"][0]
token_b64  = auth_data["authorizationToken"]
user, pwd  = base64.b64decode(token_b64).decode().split(":", 1)
registry   = auth_data["proxyEndpoint"]
run(["docker", "login", "--username", user, "--password", pwd, registry])
print("    ✅ Logged in to ECR")

# 3. Build image
print("[3] Building Docker image (lean AWS build — no PyTorch/torch)...")
backend_dir = str(Path(__file__).parent.parent)
run(["docker", "build", "-f", "Dockerfile.aws", "-t", f"{REPO_NAME}:{TAG}", backend_dir])
print("    ✅ Image built")

# 4. Tag and push
print("[4] Pushing to ECR...")
run(["docker", "tag", f"{REPO_NAME}:{TAG}", IMAGE_FULL])
run(["docker", "push", IMAGE_FULL])

print("\n" + "=" * 55)
print("  ✅ Image pushed to ECR!")
print(f"  URI: {IMAGE_FULL}")
print("=" * 55)
print("\n  Next steps:")
print("  1. AWS Console → App Runner → Create service")
print(f"  2. Container image URI: {IMAGE_FULL}")
print("  3. Port: 8080")
print("  4. Add environment variables (from backend/.env)")
