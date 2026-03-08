# ðŸ—„ï¸ Supabase Schema Setup for Adhi Compliance

## ðŸŽ¯ Issue Identified
Your current Supabase database has a **generic schema**, but Adhi Compliance needs its **specific compliance schema** with tables like:
- `users` (for authentication)
- `ai_systems` (for AI system management)  
- `compliance_checks` (for compliance tracking)
- `bias_audits` (for fairness monitoring)
- `incidents` (for issue management)
- `regulations` (for regulatory frameworks)

## ðŸš€ Complete Database Setup

### Step 1: Create Adhi Compliance Schema

1. **Go to Supabase Dashboard**
   - URL: https://supabase.com/dashboard/project/[REDACTED_PROJECT_ID]
   - Login to your account

2. **Open SQL Editor**
   - Click: **SQL Editor** (left sidebar)
   - Click: **"New query"**

3. **Run Schema Creation Script**
   - Copy the complete schema from: `C:\Users\Admin\.openclaw\workspace\supabase_schema.sql`
   - Paste into SQL Editor
   - Click: **"Run"**

### Step 2: Add Demo Data

1. **Run Seed Data Script**
   - Copy from: `C:\Users\Admin\.openclaw\workspace\adhi_seed_data.sql`
   - Paste into SQL Editor  
   - Click: **"Run"**

### Step 3: Create Authentication User

1. **Go to Authentication**
   - Click: **Authentication â†’ Users**
   - Click: **"Add user"**
   - Email: `ganeshkhovalan2203@gmail.com`
   - Password: `[REDACTED_PASSWORD]`
   - âœ… Check "Auto Confirm User"
   - Click: **"Create user"**

2. **Link Auth User to Database User**
   - Get Auth User ID:
   ```sql
   SELECT id, email FROM auth.users 
   WHERE email = 'ganeshkhovalan2203@gmail.com';
   ```
   - Update Database User (replace `YOUR_AUTH_USER_ID`):
   ```sql
   UPDATE users 
   SET 
     id = 'YOUR_AUTH_USER_ID',
     email = 'ganeshkhovalan2203@gmail.com'
   WHERE email = 'ganesh@rootedai.co.in';
   ```

## ðŸ“‹ Required Tables for Adhi Compliance

After setup, you should have these tables:

### Core Tables
- âœ… **users** - User authentication and profiles
- âœ… **organizations** - Organization management  
- âœ… **service_providers** - Service provider data

### Compliance Tables
- âœ… **ai_systems** - AI system registry
- âœ… **compliance_checks** - Compliance monitoring
- âœ… **bias_audits** - Fairness assessments
- âœ… **incidents** - Issue tracking
- âœ… **regulations** - Regulatory frameworks

### Supporting Tables
- âœ… **model_cards** - AI model documentation
- âœ… **documents** - File management
- âœ… **notifications** - Alert system
- âœ… **audit_logs** - Activity tracking

## ðŸ§ª Verification Queries

After setup, run these to verify everything is correct:

```sql
-- 1. Check all tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- 2. Verify demo data loaded
SELECT COUNT(*) as ai_systems_count FROM ai_systems;
SELECT COUNT(*) as users_count FROM users;
SELECT COUNT(*) as compliance_checks_count FROM compliance_checks;

-- 3. Check authentication user
SELECT id, email, name, role FROM users 
WHERE email = 'ganeshkhovalan2203@gmail.com';
```

**Expected Results:**
- **15+ tables** created
- **5 AI systems** in database
- **1 user** with correct email
- **25+ compliance checks** 

## ðŸ”§ Quick Setup Commands

**Copy these files to Supabase SQL Editor in order:**

1. **Schema Setup:**
```sql
-- Copy entire content from:
-- C:\Users\Admin\.openclaw\workspace\supabase_schema.sql
```

2. **Demo Data:**
```sql  
-- Copy entire content from:
-- C:\Users\Admin\.openclaw\workspace\adhi_seed_data.sql
```

3. **Auth User Linking:**
```sql
-- After creating auth user in dashboard:
UPDATE users 
SET 
  id = (SELECT id FROM auth.users WHERE email = 'ganeshkhovalan2203@gmail.com'),
  email = 'ganeshkhovalan2203@gmail.com'
WHERE email = 'ganesh@rootedai.co.in';
```

## ðŸš¨ Important Notes

1. **Order Matters**: Run schema first, then seed data, then auth linking
2. **Existing Data**: This will add to your current schema (won't delete existing tables)
3. **Auth User**: Must be created via Dashboard with "Auto Confirm User" checked
4. **IDs Must Match**: Database user ID must equal Supabase auth user ID

## âœ… Success Indicators

After completing all steps:
- âœ… All Adhi Compliance tables exist
- âœ… Demo data populated (5 AI systems, etc.)
- âœ… Auth user exists and is confirmed  
- âœ… Database user linked to auth user
- âœ… Login API returns JWT token
- âœ… Frontend login works

## ðŸ§ª Final Test

Run this test after setup:
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

---

**This complete setup will give you the full Adhi Compliance database structure ready for production! ðŸš€**
