#!/usr/bin/env python3
"""
Comprehensive endpoint validation script for Adhi Compliance API.
Tests every endpoint, logs all bugs, and reports results.
"""
import json
import sys
import time
import uuid
import httpx

BASE = "http://localhost:8000/api/v1"
TOKEN = None
ORG_ID = None
USER_ID = None
REGULATION_ID = None

TEST_EMAIL = f"qa-test-{uuid.uuid4().hex[:8]}@adhi-test.com"
TEST_PASSWORD = "Test@12345!Secure"
TEST_ORG = f"Test Org {uuid.uuid4().hex[:6]}"

results = []

def log(status, endpoint, detail=""):
    icon = "OK" if status == "OK" else ("SKIP" if status == "SKIP" else "FAIL")
    results.append({"status": status, "endpoint": endpoint, "detail": detail})
    print(f"  [{icon}]  {endpoint}: {detail}")


def req(method, path, **kwargs):
    global TOKEN
    headers = kwargs.pop("headers", {})
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    timeout = kwargs.pop("timeout", 20)
    try:
        r = httpx.request(method, f"{BASE}{path}", headers=headers, timeout=timeout, **kwargs)
        return r
    except Exception as e:
        print(f"  [ERR]  {method} {path}: {e}")
        return None


# ── PHASE 1: Health check ────────────────────────────────────────────────────
print("\n=== HEALTH CHECK ===")
r = httpx.get("http://localhost:8000/", timeout=5)
if r.status_code == 200:
    log("OK", "GET /", f"app_name={r.json().get('app_name')}")
else:
    log("FAIL", "GET /", f"Status={r.status_code}")

# ── PHASE 2: Auth ────────────────────────────────────────────────────────────
print("\n=== AUTH ===")
print(f"  Registering: {TEST_EMAIL}")

r = httpx.post(f"{BASE}/auth/register", json={
    "email": TEST_EMAIL, "password": TEST_PASSWORD,
    "name": "QA Tester", "org_name": TEST_ORG
}, timeout=25)
if r.status_code == 201:
    data = r.json()
    USER_ID = data.get("id")
    ORG_ID = data.get("org_id")
    log("OK", "POST /auth/register", f"user_id={USER_ID}")
elif r.status_code == 409:
    log("OK", "POST /auth/register", "409 already exists")
else:
    log("FAIL", "POST /auth/register", f"Status={r.status_code}: {r.text[:300]}")

r = httpx.post(f"{BASE}/auth/login", json={
    "email": TEST_EMAIL, "password": TEST_PASSWORD
}, timeout=25)
if r.status_code == 200:
    data = r.json()
    TOKEN = data.get("access_token")
    log("OK", "POST /auth/login", f"token={TOKEN[:20]}...")
else:
    log("FAIL", "POST /auth/login", f"Status={r.status_code}: {r.text[:300]}")
    print("  Cannot proceed without auth token!")
    sys.exit(1)

r = req("GET", "/auth/me")
if r and r.status_code == 200:
    me = r.json()
    USER_ID = me.get("id")
    ORG_ID = me.get("org_id")
    log("OK", "GET /auth/me", f"id={USER_ID}, org_id={ORG_ID}")
elif r:
    log("FAIL", "GET /auth/me", f"Status={r.status_code}: {r.text[:200]}")

# Test 401 without token
r_anon = httpx.get(f"{BASE}/auth/me", timeout=5)
if r_anon.status_code == 401:
    log("OK", "GET /auth/me [no token]", "401 correctly enforced")
else:
    log("FAIL", "GET /auth/me [no token]", f"Expected 401, got {r_anon.status_code}")

print(f"\n  ORG_ID={ORG_ID}")

# ── PHASE 3: Company Profiles ────────────────────────────────────────────────
print("\n=== COMPANY PROFILES ===")

r = req("GET", "/company-profiles")
if r and r.status_code == 200:
    log("OK", "GET /company-profiles", f"{len(r.json())} profiles")
elif r:
    log("FAIL", "GET /company-profiles", f"Status={r.status_code}: {r.text[:200]}")

# ── PHASE 4: AI Systems ──────────────────────────────────────────────────────
print("\n=== AI SYSTEMS ===")

SYSTEM_ID = None
r = req("POST", "/ai-systems", json={
    "name": f"QA System {uuid.uuid4().hex[:6]}",
    "purpose": "Testing", "description": "QA validation system",
    "model_provider": "OpenAI", "data_types": ["PII"],
    "deployment_regions": ["EU"], "risk_classification": "limited"
})
if r and r.status_code in (200, 201):
    SYSTEM_ID = r.json().get("id")
    log("OK", "POST /ai-systems", f"id={SYSTEM_ID}")
elif r:
    log("FAIL", "POST /ai-systems", f"Status={r.status_code}: {r.text[:300]}")

r = req("GET", "/ai-systems")
if r and r.status_code == 200:
    data = r.json()
    items = data.get("items", data) if isinstance(data, dict) else data
    log("OK", "GET /ai-systems", f"{len(items)} systems")
elif r:
    log("FAIL", "GET /ai-systems", f"Status={r.status_code}: {r.text[:200]}")

if SYSTEM_ID:
    r = req("GET", f"/ai-systems/{SYSTEM_ID}")
    if r and r.status_code == 200:
        log("OK", "GET /ai-systems/{id}", f"name={r.json().get('name')}")
    elif r:
        log("FAIL", "GET /ai-systems/{id}", f"Status={r.status_code}: {r.text[:200]}")

    r = req("PATCH", f"/ai-systems/{SYSTEM_ID}", json={"description": "Updated by QA"})
    if r and r.status_code == 200:
        log("OK", "PATCH /ai-systems/{id}", "Updated")
    elif r:
        log("FAIL", "PATCH /ai-systems/{id}", f"Status={r.status_code}: {r.text[:200]}")

# ── PHASE 5: Regulations ─────────────────────────────────────────────────────
print("\n=== REGULATIONS ===")

r = req("POST", "/seed/regulations")
if r and r.status_code in (200, 201):
    log("OK", "POST /seed/regulations", r.text[:100])
elif r:
    log("FAIL", "POST /seed/regulations", f"Status={r.status_code}: {r.text[:200]}")

r = req("GET", "/regulations")
if r and r.status_code == 200:
    regs = r.json()
    items = regs.get("items", regs) if isinstance(regs, dict) else regs
    log("OK", "GET /regulations", f"{len(items)} regulations")
    if items:
        REGULATION_ID = items[0].get("id")
elif r:
    log("FAIL", "GET /regulations", f"Status={r.status_code}: {r.text[:200]}")

r = req("GET", "/regulations?jurisdiction=EU")
if r and r.status_code == 200:
    regs = r.json()
    items = regs.get("items", regs) if isinstance(regs, dict) else regs
    log("OK", "GET /regulations?jurisdiction=EU", f"{len(items)} EU regulations")
elif r:
    log("FAIL", "GET /regulations?jurisdiction=EU", f"Status={r.status_code}: {r.text[:200]}")

# ── PHASE 6: Compliance Checks ───────────────────────────────────────────────
print("\n=== COMPLIANCE CHECKS ===")

CHECK_ID = None
if SYSTEM_ID and REGULATION_ID:
    r = req("POST", "/compliance-checks", json={
        "ai_system_id": SYSTEM_ID, "regulation_id": REGULATION_ID,
        "status": "pending", "priority": "high",
        "gap_description": "QA test gap"
    })
    if r and r.status_code in (200, 201):
        CHECK_ID = r.json().get("id")
        log("OK", "POST /compliance-checks", f"id={CHECK_ID}")
    elif r:
        log("FAIL", "POST /compliance-checks", f"Status={r.status_code}: {r.text[:300]}")
else:
    log("SKIP", "POST /compliance-checks", f"No system_id={SYSTEM_ID} or regulation_id={REGULATION_ID}")

if SYSTEM_ID:
    r = req("GET", f"/compliance-checks?system_id={SYSTEM_ID}")
    if r and r.status_code == 200:
        log("OK", "GET /compliance-checks?system_id=X", r.text[:100])
    elif r:
        log("FAIL", "GET /compliance-checks?system_id=X", f"Status={r.status_code}: {r.text[:200]}")

r = req("GET", "/compliance-summary")
if r and r.status_code == 200:
    log("OK", "GET /compliance-summary", r.text[:100])
elif r:
    log("FAIL", "GET /compliance-summary", f"Status={r.status_code}: {r.text[:200]}")

# ── PHASE 7: Dashboard ───────────────────────────────────────────────────────
print("\n=== DASHBOARD ===")

for ep in ["/dashboard/stats", "/dashboard/risk-distribution", "/dashboard/recent-activity"]:
    r = req("GET", ep)
    if r and r.status_code == 200:
        log("OK", f"GET {ep}", r.text[:80])
    elif r:
        log("FAIL", f"GET {ep}", f"Status={r.status_code}: {r.text[:200]}")
    else:
        log("FAIL", f"GET {ep}", "No response")

# ── PHASE 8: Incidents ───────────────────────────────────────────────────────
print("\n=== INCIDENTS ===")

INCIDENT_ID = None
if SYSTEM_ID:
    r = req("POST", "/incidents", json={
        "ai_system_id": SYSTEM_ID, "severity": "medium",
        "incident_type": "Data Drift",
        "description": "QA test incident"
    })
    if r and r.status_code in (200, 201):
        INCIDENT_ID = r.json().get("id")
        log("OK", "POST /incidents", f"id={INCIDENT_ID}")
    elif r:
        log("FAIL", "POST /incidents", f"Status={r.status_code}: {r.text[:300]}")

r = req("GET", "/incidents")
if r and r.status_code == 200:
    log("OK", "GET /incidents", f"{len(r.json())} incidents")
elif r:
    log("FAIL", "GET /incidents", f"Status={r.status_code}: {r.text[:200]}")

if INCIDENT_ID:
    r = req("PATCH", f"/incidents/{INCIDENT_ID}", json={"status": "mitigating"})
    if r and r.status_code == 200:
        log("OK", "PATCH /incidents/{id}", "Updated")
    elif r:
        log("FAIL", "PATCH /incidents/{id}", f"Status={r.status_code}: {r.text[:200]}")

    r = req("POST", f"/incidents/{INCIDENT_ID}/timeline", json={
        "event": "QA validation event", "timestamp": "2026-02-26T10:00:00Z"
    })
    if r and r.status_code in (200, 201):
        log("OK", "POST /incidents/{id}/timeline", "Added")
    elif r:
        log("FAIL", "POST /incidents/{id}/timeline", f"Status={r.status_code}: {r.text[:200]}")

# ── PHASE 9: Bias Audits ─────────────────────────────────────────────────────
print("\n=== BIAS AUDITS ===")

if SYSTEM_ID:
    r = req("POST", "/bias-audits", json={
        "ai_system_id": SYSTEM_ID,
        "dataset_description": "QA test dataset",
        "demographic_parity_score": 0.85,
        "disparate_impact_ratio": 0.92,
        "overall_status": "pass",
        "findings": {"note": "QA"}
    })
    if r and r.status_code in (200, 201):
        log("OK", "POST /bias-audits", f"id={r.json().get('id')}")
    elif r:
        log("FAIL", "POST /bias-audits", f"Status={r.status_code}: {r.text[:300]}")

    r = req("GET", f"/bias-audits/{SYSTEM_ID}/history")
    if r and r.status_code == 200:
        log("OK", "GET /bias-audits/{system_id}/history", r.text[:100])
    elif r:
        log("FAIL", "GET /bias-audits/{system_id}/history", f"Status={r.status_code}: {r.text[:200]}")

# ── PHASE 10: Model Cards ────────────────────────────────────────────────────
print("\n=== MODEL CARDS ===")

if SYSTEM_ID:
    r = req("POST", f"/model-cards/{SYSTEM_ID}/generate", timeout=30)
    if r and r.status_code in (200, 201):
        log("OK", "POST /model-cards/{id}/generate", r.text[:100])
    elif r:
        log("FAIL", "POST /model-cards/{id}/generate", f"Status={r.status_code}: {r.text[:200]}")

    r = req("GET", f"/model-cards/{SYSTEM_ID}")
    if r and r.status_code == 200:
        log("OK", "GET /model-cards/{id}", r.text[:100])
    elif r:
        log("FAIL", "GET /model-cards/{id}", f"Status={r.status_code}: {r.text[:200]}")

# ── PHASE 11: Monitoring ─────────────────────────────────────────────────────
print("\n=== MONITORING ===")

r = req("GET", "/monitoring/deadlines")
if r and r.status_code == 200:
    log("OK", "GET /monitoring/deadlines", r.text[:100])
elif r:
    log("FAIL", "GET /monitoring/deadlines", f"Status={r.status_code}: {r.text[:200]}")

r = req("POST", "/monitoring/scan")
if r and r.status_code in (200, 201, 202):
    log("OK", "POST /monitoring/scan", r.text[:100])
elif r:
    log("FAIL", "POST /monitoring/scan", f"Status={r.status_code}: {r.text[:200]}")

# ── PHASE 12: Reports ────────────────────────────────────────────────────────
print("\n=== REPORTS ===")

if ORG_ID:
    for path in [f"/reports/compliance/{ORG_ID}", f"/reports/executive-summary/{ORG_ID}"]:
        r = req("GET", path)
        if r and r.status_code == 200:
            log("OK", f"GET {path}", r.text[:100])
        elif r:
            log("FAIL", f"GET {path}", f"Status={r.status_code}: {r.text[:200]}")

# ── PHASE 13: Tasks ──────────────────────────────────────────────────────────
print("\n=== TASKS ===")

TASK_ID = str(uuid.uuid4())
r = req("GET", f"/tasks/{TASK_ID}/status")
if r and r.status_code in (200, 404):
    log("OK", "GET /tasks/{id}/status", f"Status={r.status_code}: {r.text[:100]}")
elif r:
    log("FAIL", "GET /tasks/{id}/status", f"Status={r.status_code}: {r.text[:200]}")

# ── PHASE 14: Notifications ──────────────────────────────────────────────────
print("\n=== NOTIFICATIONS ===")

r = req("GET", "/notifications")
if r and r.status_code == 200:
    log("OK", "GET /notifications", r.text[:100])
elif r:
    log("FAIL", "GET /notifications", f"Status={r.status_code}: {r.text[:200]}")

# ── SUMMARY ──────────────────────────────────────────────────────────────────
print("\n" + "="*60)
ok_count = sum(1 for r in results if r["status"] == "OK")
fail_count = sum(1 for r in results if r["status"] == "FAIL")
skip_count = sum(1 for r in results if r["status"] == "SKIP")
print(f"Results: {ok_count} PASS | {fail_count} FAIL | {skip_count} SKIP")

if fail_count > 0:
    print("\nFAILED ENDPOINTS:")
    for r in results:
        if r["status"] == "FAIL":
            print(f"  - {r['endpoint']}: {r['detail']}")

# Write JSON for further processing
with open("test_results.json", "w") as f:
    json.dump({
        "results": results,
        "system_id": SYSTEM_ID,
        "regulation_id": REGULATION_ID,
        "incident_id": INCIDENT_ID,
        "org_id": ORG_ID,
        "user_id": USER_ID,
    }, f, indent=2)

print("\nResults written to test_results.json")
sys.exit(0 if fail_count == 0 else 1)
