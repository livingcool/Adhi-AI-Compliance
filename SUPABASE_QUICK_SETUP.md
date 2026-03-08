# ðŸš€ Quick Supabase Setup for Adhi Compliance

## âš ï¸ Fixed SQL Scripts Created
The original schema had syntax errors. I've created **fixed versions** that work with Supabase.

## ðŸ“‹ 3-Step Setup Process

### Step 1: Create Types
1. Go to: https://supabase.com/dashboard/project/[REDACTED_PROJECT_ID]
2. Click: **SQL Editor** â†’ **New query**
3. Copy & paste entire content from: `backend/supabase_schema_fixed.sql`
4. Click: **Run** â–¶ï¸

### Step 2: Create Tables  
1. Click: **New query**
2. Copy & paste entire content from: `backend/supabase_tables.sql`
3. Click: **Run** â–¶ï¸

### Step 3: Add Demo Data
1. Click: **New query**
2. Copy & paste entire content from: `backend/supabase_seed_data_fixed.sql`
3. Click: **Run** â–¶ï¸

### Step 4: Create Auth User
1. Click: **Authentication** â†’ **Users** â†’ **Add user**
2. Email: `ganeshkhovalan2203@gmail.com`
3. Password: `[REDACTED_PASSWORD]`
4. âœ… **Auto Confirm User**
5. Click: **Create user**

### Step 5: Link Auth to Database User
1. Click: **SQL Editor** â†’ **New query**
2. Run this query:
```sql
-- Get the auth user ID first
SELECT id as auth_user_id, email FROM auth.users 
WHERE email = 'ganeshkhovalan2203@gmail.com';

-- Copy the ID from above, then run this (replace YOUR_AUTH_USER_ID):
UPDATE users 
SET 
  id = 'YOUR_AUTH_USER_ID',
  email = 'ganeshkhovalan2203@gmail.com'
WHERE email = 'ganesh@rootedai.co.in';

-- Verify it worked
SELECT id, email, name, role FROM users 
WHERE email = 'ganeshkhovalan2203@gmail.com';
```

## âœ… Quick Verification

After setup, run this to verify everything works:
```sql
-- Check tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name IN 
('users', 'ai_systems', 'compliance_checks', 'bias_audits', 'incidents');

-- Check data loaded
SELECT 'ai_systems' as table_name, COUNT(*) FROM ai_systems
UNION ALL
SELECT 'users', COUNT(*) FROM users  
UNION ALL
SELECT 'compliance_checks', COUNT(*) FROM compliance_checks;
```

**Expected Results:**
- âœ… 5 tables found
- âœ… 5 AI systems
- âœ… 3 users 
- âœ… 5+ compliance checks

## ðŸ§ª Test Authentication

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

## ðŸ“ Fixed Files Created

1. **supabase_schema_fixed.sql** - Fixed enum types
2. **supabase_tables.sql** - All Adhi Compliance tables
3. **supabase_seed_data_fixed.sql** - Demo data with proper conflict handling

## ðŸ”§ Key Fixes Made

- âœ… Removed `IF NOT EXISTS` from `CREATE TYPE` (not supported)
- âœ… Used `DO $$` blocks for conditional type creation
- âœ… Changed `VARCHAR` to `TEXT` for better compatibility
- âœ… Added `ON CONFLICT DO NOTHING` for safe re-runs
- âœ… Renamed `documents` table to `adhi_documents` to avoid conflicts

## ðŸš¨ Important Notes

- **Run scripts in order**: Schema â†’ Tables â†’ Seed Data â†’ Auth User
- **Don't skip steps**: Each step depends on the previous one
- **Auth user ID must match**: Database user.id = auth.users.id

---

**This setup will give you the complete Adhi Compliance platform ready for testing! ðŸš€**
