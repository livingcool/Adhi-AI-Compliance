"""
Quick Bedrock + S3 connectivity test.
Run from backend/ directory:  py scripts/test_aws.py
"""
import os, sys, json, boto3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env", override=True)

region      = os.environ.get("AWS_BEDROCK_REGION", "ap-south-1")
chat_model  = os.environ.get("AWS_BEDROCK_CHAT_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
embed_model = os.environ.get("AWS_BEDROCK_EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")
s3_bucket   = os.environ.get("AWS_S3_BUCKET", "")
access_key  = os.environ.get("AWS_ACCESS_KEY_ID")
secret_key  = os.environ.get("AWS_SECRET_ACCESS_KEY")

creds = {}
if access_key and secret_key:
    creds = {"aws_access_key_id": access_key, "aws_secret_access_key": secret_key}

print("=" * 55)
print("  Adhi AI Compliance — AWS Connectivity Test")
print("=" * 55)

# ── 1. Bedrock Chat (Claude) ──────────────────────────────
print(f"\n[1] Bedrock Chat → {chat_model}")
try:
    client = boto3.client("bedrock-runtime", region_name=region, **creds)
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 60,
        "messages": [{"role": "user", "content": "Say: Adhi AI Compliance is live on AWS Bedrock!"}]
    })
    r = client.invoke_model(modelId=chat_model, body=body,
                            contentType="application/json", accept="application/json")
    reply = json.loads(r["body"].read())["content"][0]["text"]
    print(f"   ✅ Claude replied: {reply}")
except Exception as e:
    print(f"   ❌ Claude failed: {e}")

# ── 2. Bedrock Embeddings (Titan) ─────────────────────────
print(f"\n[2] Bedrock Embeddings → {embed_model}")
try:
    r = client.invoke_model(
        modelId=embed_model,
        body=json.dumps({"inputText": "compliance document test"}),
        contentType="application/json", accept="application/json"
    )
    embedding = json.loads(r["body"].read())["embedding"]
    print(f"   ✅ Titan embedding: {len(embedding)}-dim vector")
except Exception as e:
    print(f"   ❌ Titan failed: {e}")

# ── 3. S3 bucket ──────────────────────────────────────────
print(f"\n[3] S3 Bucket → {s3_bucket or '(AWS_S3_BUCKET not set)'}")
if s3_bucket:
    try:
        s3 = boto3.client("s3", region_name=os.environ.get("AWS_REGION", "ap-south-1"), **creds)
        s3.put_object(Bucket=s3_bucket, Key="healthcheck.txt", Body=b"adhi-aws-ok")
        s3.delete_object(Bucket=s3_bucket, Key="healthcheck.txt")
        print(f"   ✅ S3 upload/delete successful")
    except Exception as e:
        print(f"   ❌ S3 failed: {e}")
else:
    print("   ⚠️  AWS_S3_BUCKET not set in .env — skipping")

print("\n" + "=" * 55)
