# ðŸ› ï¸ Manual Supabase Setup - Complete Guide

## ðŸ”¥ Network Issue Bypass
Since automated scripts are timing out, let's do this manually via the Supabase Dashboard.

## ðŸŽ¯ One-Time Setup (15 minutes)

### Step 1: Access Supabase Dashboard
1. Go to: https://supabase.com/dashboard/project/[REDACTED_PROJECT_ID]
2. Login to your account

### Step 2: Create Enum Types
1. Click: **SQL Editor** â†’ **New query**
2. Copy & paste this entire block:

```sql
-- Adhi Compliance Enum Types
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role_enum') THEN
        CREATE TYPE user_role_enum AS ENUM ('admin', 'member', 'viewer');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'risk_classification_enum') THEN
        CREATE TYPE risk_classification_enum AS ENUM ('unacceptable', 'high', 'limited', 'minimal', 'unclassified');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'compliance_status_enum') THEN
        CREATE TYPE compliance_status_enum AS ENUM ('compliant', 'non_compliant', 'partial', 'pending');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'check_priority_enum') THEN
        CREATE TYPE check_priority_enum AS ENUM ('critical', 'high', 'medium', 'low');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'audit_status_enum') THEN
        CREATE TYPE audit_status_enum AS ENUM ('pass', 'fail', 'conditional');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'incident_severity_enum') THEN
        CREATE TYPE incident_severity_enum AS ENUM ('critical', 'high', 'medium', 'low');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'incident_status_enum') THEN
        CREATE TYPE incident_status_enum AS ENUM ('investigating', 'mitigating', 'resolved', 'closed');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'ingesttype') THEN
        CREATE TYPE ingesttype AS ENUM ('pdf', 'video', 'audio', 'image', 'text');
    END IF;
END
$$;
```

3. Click: **Run** â–¶ï¸
4. Should see: "Success. No rows returned"

### Step 3: Create Tables
1. Click: **New query**
2. Copy & paste this entire block:

```sql
-- Adhi Compliance Tables (UUID Compatible)

-- Service Providers
CREATE TABLE IF NOT EXISTS service_providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_name TEXT NOT NULL,
    subscription_plan TEXT,
    admin_email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Organizations
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_provider_id UUID NOT NULL REFERENCES service_providers(id),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    settings TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Users (for Adhi Compliance)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    role user_role_enum DEFAULT 'member',
    org_id UUID REFERENCES organizations(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Regulations
CREATE TABLE IF NOT EXISTS regulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    short_name TEXT NOT NULL,
    jurisdiction TEXT NOT NULL,
    effective_date DATE,
    enforcement_date DATE,
    full_text TEXT,
    category TEXT,
    url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- AI Systems
CREATE TABLE IF NOT EXISTS ai_systems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    purpose TEXT,
    description TEXT,
    model_provider TEXT,
    data_types JSONB,
    deployment_regions JSONB,
    risk_classification risk_classification_enum DEFAULT 'unclassified',
    is_high_risk BOOLEAN DEFAULT false,
    compliance_score DECIMAL(5,2),
    org_id UUID REFERENCES organizations(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Company Profiles
CREATE TABLE IF NOT EXISTS company_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    industry TEXT,
    size TEXT,
    website TEXT,
    jurisdictions JSONB,
    risk_appetite TEXT,
    org_id UUID REFERENCES organizations(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Compliance Checks
CREATE TABLE IF NOT EXISTS compliance_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ai_system_id UUID REFERENCES ai_systems(id),
    regulation_id UUID REFERENCES regulations(id),
    status compliance_status_enum DEFAULT 'pending',
    gap_description TEXT,
    remediation_steps TEXT,
    priority check_priority_enum DEFAULT 'medium',
    deadline DATE,
    checked_at TIMESTAMP,
    org_id UUID REFERENCES organizations(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Bias Audits
CREATE TABLE IF NOT EXISTS bias_audits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ai_system_id UUID REFERENCES ai_systems(id),
    audit_date DATE NOT NULL,
    dataset_description TEXT,
    demographic_parity_score DECIMAL(5,3),
    disparate_impact_ratio DECIMAL(5,3),
    overall_status audit_status_enum DEFAULT 'pass',
    findings JSONB,
    org_id UUID REFERENCES organizations(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Incidents
CREATE TABLE IF NOT EXISTS incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ai_system_id UUID REFERENCES ai_systems(id),
    severity incident_severity_enum DEFAULT 'low',
    incident_type TEXT NOT NULL,
    description TEXT NOT NULL,
    detected_at TIMESTAMP DEFAULT NOW(),
    status incident_status_enum DEFAULT 'investigating',
    timeline JSONB,
    filing_status TEXT,
    filing_deadline DATE,
    org_id UUID REFERENCES organizations(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Model Cards
CREATE TABLE IF NOT EXISTS model_cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ai_system_id UUID REFERENCES ai_systems(id),
    content JSONB NOT NULL,
    version TEXT,
    generated_at TIMESTAMP DEFAULT NOW(),
    org_id UUID REFERENCES organizations(id)
);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    org_id UUID REFERENCES organizations(id),
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT NOT NULL,
    read BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    org_id UUID REFERENCES organizations(id),
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT,
    details JSONB,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_compliance_checks_ai_system ON compliance_checks(ai_system_id);
CREATE INDEX IF NOT EXISTS idx_compliance_checks_regulation ON compliance_checks(regulation_id);
CREATE INDEX IF NOT EXISTS idx_bias_audits_ai_system ON bias_audits(ai_system_id);
CREATE INDEX IF NOT EXISTS idx_incidents_ai_system ON incidents(ai_system_id);
CREATE INDEX IF NOT EXISTS idx_users_org ON users(org_id);
CREATE INDEX IF NOT EXISTS idx_ai_systems_org ON ai_systems(org_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_org ON audit_logs(org_id);
```

3. Click: **Run** â–¶ï¸
4. Should see: "Success. No rows returned"

### Step 4: Add Demo Data
1. Click: **New query**
2. Copy & paste this entire block:

```sql
-- Adhi Compliance Demo Data (UUID Compatible)

-- 1. Service Provider
INSERT INTO service_providers (id, business_name, subscription_plan, admin_email, created_at)
VALUES ('12345678-1234-5678-9012-123456789001'::uuid, 'RootedAI', 'enterprise', 'info@rootedai.co.in', NOW())
ON CONFLICT (id) DO NOTHING;

-- 2. Organization
INSERT INTO organizations (id, service_provider_id, name, slug, settings, created_at)
VALUES ('12345678-1234-5678-9012-123456789002'::uuid, '12345678-1234-5678-9012-123456789001'::uuid, 'RootedAI', 'rooted-ai', '{"compliance_level": "enterprise", "auto_audit": true}', NOW())
ON CONFLICT (id) DO NOTHING;

-- 3. Users
INSERT INTO users (id, email, name, role, org_id, created_at, updated_at) VALUES
('12345678-1234-5678-9012-123456789003'::uuid, 'ganesh@rootedai.co.in', 'Ganesh Khovalan', 'admin', '12345678-1234-5678-9012-123456789002'::uuid, NOW(), NOW()),
('12345678-1234-5678-9012-123456789004'::uuid, 'compliance@rootedai.co.in', 'Compliance Officer', 'member', '12345678-1234-5678-9012-123456789002'::uuid, NOW(), NOW()),
('12345678-1234-5678-9012-123456789005'::uuid, 'auditor@rootedai.co.in', 'AI Auditor', 'member', '12345678-1234-5678-9012-123456789002'::uuid, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 4. Sample Regulations
INSERT INTO regulations (id, name, short_name, jurisdiction, effective_date, enforcement_date, full_text, category, url) VALUES
('12345678-1234-5678-9012-123456789010'::uuid, 'European Union Artificial Intelligence Act', 'EU AI Act', 'European Union', '2024-08-01', '2025-08-01', 'The EU AI Act establishes a comprehensive regulatory framework for AI systems...', 'AI Regulation', 'https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689'),
('12345678-1234-5678-9012-123456789011'::uuid, 'General Data Protection Regulation', 'GDPR', 'European Union', '2018-05-25', '2018-05-25', 'Regulation on the protection of natural persons with regard to the processing of personal data...', 'Data Protection', 'https://gdpr.eu/'),
('12345678-1234-5678-9012-123456789012'::uuid, 'NIST AI Risk Management Framework', 'NIST AI RMF', 'United States', '2023-01-26', '2023-01-26', 'A voluntary framework to better manage risks to individuals, organizations, and society...', 'AI Standards', 'https://www.nist.gov/itl/ai-risk-management-framework'),
('12345678-1234-5678-9012-123456789013'::uuid, 'California Consumer Privacy Act', 'CCPA', 'California', '2020-01-01', '2020-07-01', 'Provides California residents with rights regarding their personal information...', 'Privacy Rights', 'https://oag.ca.gov/privacy/ccpa'),
('12345678-1234-5678-9012-123456789014'::uuid, 'Algorithmic Accountability Act', 'AAA', 'United States', '2024-01-01', '2024-01-01', 'Proposed legislation requiring impact assessments for automated decision systems...', 'Algorithm Governance', 'https://www.congress.gov/bill/117th-congress/house-bill/6580')
ON CONFLICT (id) DO NOTHING;

-- 5. AI Systems
INSERT INTO ai_systems (id, name, purpose, description, model_provider, data_types, deployment_regions, risk_classification, is_high_risk, compliance_score, org_id, created_at, updated_at) VALUES
('12345678-1234-5678-9012-123456789020'::uuid, 'Voter Verification System', 'Identity Verification', 'AI-powered voter identity verification system using OCR and facial recognition for electoral processes', 'OpenAI', '["facial_images", "government_ids", "biometric_data"]', '["India", "Tamil_Nadu"]', 'high', true, 87.5, '12345678-1234-5678-9012-123456789002'::uuid, NOW(), NOW()),
('12345678-1234-5678-9012-123456789021'::uuid, 'Resume Screening AI', 'HR Automation', 'Automated resume screening and candidate ranking system for recruitment processes', 'Google', '["resumes", "personal_data", "employment_history"]', '["India", "United_States"]', 'limited', true, 92.3, '12345678-1234-5678-9012-123456789002'::uuid, NOW(), NOW()),
('12345678-1234-5678-9012-123456789022'::uuid, 'Fraud Detection Engine', 'Financial Security', 'Machine learning system for detecting fraudulent transactions and suspicious patterns', 'Anthropic', '["transaction_data", "user_behavior", "financial_records"]', '["Global"]', 'limited', true, 89.7, '12345678-1234-5678-9012-123456789002'::uuid, NOW(), NOW()),
('12345678-1234-5678-9012-123456789023'::uuid, 'Content Moderation AI', 'Safety', 'AI system for automatically detecting and moderating harmful content on digital platforms', 'OpenAI', '["text_content", "images", "user_reports"]', '["Global"]', 'minimal', false, 95.1, '12345678-1234-5678-9012-123456789002'::uuid, NOW(), NOW()),
('12345678-1234-5678-9012-123456789024'::uuid, 'Predictive Analytics Platform', 'Business Intelligence', 'AI-driven analytics platform for predicting customer behavior and market trends', 'Microsoft', '["customer_data", "sales_data", "market_data"]', '["India", "Southeast_Asia"]', 'minimal', false, 91.8, '12345678-1234-5678-9012-123456789002'::uuid, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 6. Compliance Checks
INSERT INTO compliance_checks (id, ai_system_id, regulation_id, status, gap_description, remediation_steps, priority, deadline, checked_at, org_id) VALUES
('12345678-1234-5678-9012-123456789040'::uuid, '12345678-1234-5678-9012-123456789020'::uuid, '12345678-1234-5678-9012-123456789010'::uuid, 'partial', 'High-risk AI system lacks comprehensive impact assessment', 'Conduct AI impact assessment, implement bias testing, enhance documentation', 'critical', '2024-03-15', NOW(), '12345678-1234-5678-9012-123456789002'::uuid),
('12345678-1234-5678-9012-123456789041'::uuid, '12345678-1234-5678-9012-123456789020'::uuid, '12345678-1234-5678-9012-123456789011'::uuid, 'compliant', 'GDPR compliance verified for voter data processing', '', 'high', '2024-04-01', NOW(), '12345678-1234-5678-9012-123456789002'::uuid),
('12345678-1234-5678-9012-123456789042'::uuid, '12345678-1234-5678-9012-123456789021'::uuid, '12345678-1234-5678-9012-123456789014'::uuid, 'non_compliant', 'Resume screening lacks algorithmic impact assessment', 'Implement bias testing, document decision logic, establish appeal process', 'high', '2024-03-30', NOW(), '12345678-1234-5678-9012-123456789002'::uuid),
('12345678-1234-5678-9012-123456789043'::uuid, '12345678-1234-5678-9012-123456789022'::uuid, '12345678-1234-5678-9012-123456789012'::uuid, 'compliant', 'Fraud detection system aligns with NIST framework', '', 'medium', '2024-05-01', NOW(), '12345678-1234-5678-9012-123456789002'::uuid),
('12345678-1234-5678-9012-123456789044'::uuid, '12345678-1234-5678-9012-123456789023'::uuid, '12345678-1234-5678-9012-123456789013'::uuid, 'partial', 'Content moderation needs enhanced privacy controls for CA users', 'Implement data minimization, add user consent mechanisms', 'medium', '2024-04-15', NOW(), '12345678-1234-5678-9012-123456789002'::uuid)
ON CONFLICT (id) DO NOTHING;

-- 7. Bias Audits
INSERT INTO bias_audits (id, ai_system_id, audit_date, dataset_description, demographic_parity_score, disparate_impact_ratio, overall_status, findings, org_id) VALUES
('12345678-1234-5678-9012-123456789050'::uuid, '12345678-1234-5678-9012-123456789020'::uuid, '2024-01-15', 'Test dataset with 10,000 voter records across diverse demographics', 0.85, 0.88, 'conditional', '{"bias_detected": true, "affected_groups": ["elderly", "rural_voters"], "recommendations": ["Improve model training on underrepresented groups", "Implement demographic balancing"]}', '12345678-1234-5678-9012-123456789002'::uuid),
('12345678-1234-5678-9012-123456789051'::uuid, '12345678-1234-5678-9012-123456789021'::uuid, '2024-01-20', 'Resume dataset with 5,000 applications across gender and ethnicity', 0.92, 0.95, 'pass', '{"bias_detected": false, "performance": "excellent", "recommendations": ["Continue regular monitoring", "Expand test dataset"]}', '12345678-1234-5678-9012-123456789002'::uuid),
('12345678-1234-5678-9012-123456789052'::uuid, '12345678-1234-5678-9012-123456789022'::uuid, '2024-02-01', 'Transaction data covering 100,000 transactions across customer segments', 0.89, 0.91, 'conditional', '{"bias_detected": true, "affected_groups": ["young_customers"], "recommendations": ["Adjust risk thresholds", "Implement fairness constraints"]}', '12345678-1234-5678-9012-123456789002'::uuid)
ON CONFLICT (id) DO NOTHING;

-- 8. Incidents
INSERT INTO incidents (id, ai_system_id, severity, incident_type, description, detected_at, status, timeline, filing_status, filing_deadline, org_id) VALUES
('12345678-1234-5678-9012-123456789060'::uuid, '12345678-1234-5678-9012-123456789020'::uuid, 'high', 'Bias Detection', 'Voter verification system showing lower accuracy for elderly voters', '2024-01-10', 'mitigating', '{"reported": "2024-01-10", "investigated": "2024-01-12", "mitigation_started": "2024-01-15"}', 'filed', '2024-01-25', '12345678-1234-5678-9012-123456789002'::uuid),
('12345678-1234-5678-9012-123456789061'::uuid, '12345678-1234-5678-9012-123456789021'::uuid, 'medium', 'Performance Degradation', 'Resume screening accuracy dropped below threshold for technical roles', '2024-01-25', 'resolved', '{"reported": "2024-01-25", "investigated": "2024-01-26", "resolved": "2024-02-01"}', 'not_required', NULL, '12345678-1234-5678-9012-123456789002'::uuid),
('12345678-1234-5678-9012-123456789062'::uuid, '12345678-1234-5678-9012-123456789022'::uuid, 'low', 'False Positive', 'Increased false positive rate in fraud detection for international transactions', '2024-02-10', 'investigating', '{"reported": "2024-02-10", "investigation_started": "2024-02-11"}', 'pending', '2024-02-25', '12345678-1234-5678-9012-123456789002'::uuid)
ON CONFLICT (id) DO NOTHING;
```

3. Click: **Run** â–¶ï¸
4. Should see: "Success. No rows returned"

### Step 5: Create Auth User (If Not Done)
1. Click: **Authentication** â†’ **Users**
2. Click: **"Add user"**
3. Fill in:
   - Email: `ganeshkhovalan2203@gmail.com`
   - Password: `[REDACTED_PASSWORD]`
   - âœ… Check "Auto Confirm User"
4. Click: **Create user**

### Step 6: Link Auth User to Database
1. Go back to: **SQL Editor** â†’ **New query**
2. Copy & paste this:

```sql
-- Link Auth User to Database User
UPDATE users 
SET 
  id = (SELECT id FROM auth.users WHERE email = 'ganeshkhovalan2203@gmail.com'),
  email = 'ganeshkhovalan2203@gmail.com'
WHERE email = 'ganesh@rootedai.co.in';

-- Verify the linking
SELECT 
    u.id as user_id,
    u.email as user_email, 
    u.name,
    u.role,
    au.email as auth_email
FROM users u
JOIN auth.users au ON u.id = au.id
WHERE u.email = 'ganeshkhovalan2203@gmail.com';

-- Check data counts
SELECT 'ai_systems' as table_name, COUNT(*) FROM ai_systems
UNION ALL
SELECT 'users', COUNT(*) FROM users  
UNION ALL
SELECT 'compliance_checks', COUNT(*) FROM compliance_checks
UNION ALL
SELECT 'bias_audits', COUNT(*) FROM bias_audits
UNION ALL
SELECT 'incidents', COUNT(*) FROM incidents;
```

3. Click: **Run** â–¶ï¸
4. Should see verification results with user info and data counts

## âœ… Verification

After all steps, you should see:
- **User linked**: Same UUID for auth and database user
- **Data loaded**: 5 AI systems, 3 users, 5 compliance checks, 3 bias audits, 3 incidents

## ðŸ§ª Final Test

```bash
cd backend
py test_auth_simple.py
```

**Expected Output:**
```
[OK] Backend server running
[SUCCESS] Authentication working!
Token: eyJhbGciOiJIUzI1NiIs...
```

## ðŸŽ¯ After Success

- âœ… Frontend: http://localhost:3000  
- âœ… Login: `ganeshkhovalan2203@gmail.com` / `[REDACTED_PASSWORD]`
- âœ… Full Adhi Compliance platform operational
- âœ… All API endpoints accessible

---

**This manual method bypasses all network timeout issues and gives you direct control over the setup! ðŸš€**
