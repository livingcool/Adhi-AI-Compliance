# ðŸ” Authentication Setup Guide for Adhi Compliance

## ðŸŽ¯ Setup Summary

**Email**: `ganeshkhovalan2203@gmail.com`  
**Password**: `[REDACTED_PASSWORD]`  
**Status**: âš ï¸ Needs Supabase Auth user creation

## ðŸ”§ Current Situation

âœ… **Backend API**: Running and responding  
âœ… **Supabase Config**: Properly configured with valid keys  
âœ… **Database Schema**: Ready with user tables  
âš ï¸ **Auth User**: Needs to be created in Supabase Auth

## ðŸš€ Setup Methods

### Method 1: Supabase Dashboard (Recommended)

1. **Go to Supabase Dashboard**
   - Visit: https://supabase.com/dashboard
   - Login to your account
   - Select project: `[REDACTED_PROJECT_ID]`

2. **Create Auth User**
   - Go to: **Authentication â†’ Users**
   - Click **"Add user"**
   - Email: `ganeshkhovalan2203@gmail.com`
   - Password: `[REDACTED_PASSWORD]`
   - âœ… Check "Auto Confirm User"
   - Click **"Create user"**

3. **Update Database User**
   - Go to: **SQL Editor**
   - Run this query:
   ```sql
   UPDATE users 
   SET email = 'ganeshkhovalan2203@gmail.com' 
   WHERE email = 'ganesh@rootedai.co.in';
   ```

### Method 2: SQL Editor Direct Insert

If the Python script keeps timing out, use Supabase SQL Editor:

```sql
-- 1. First, create the auth user via Dashboard (Method 1, step 2)
-- 2. Then run this query to update the database user record:

-- Get the new user ID from Auth (run this first to see the new user)
SELECT id, email FROM auth.users WHERE email = 'ganeshkhovalan2203@gmail.com';

-- Update the database user with the new auth user ID
-- Replace 'NEW_USER_ID_HERE' with the actual ID from above query
UPDATE users 
SET 
  id = 'NEW_USER_ID_HERE',  -- Use the UUID from auth.users
  email = 'ganeshkhovalan2203@gmail.com' 
WHERE email = 'ganesh@rootedai.co.in';

-- Verify the update
SELECT id, email, name, role FROM users WHERE email = 'ganeshkhovalan2203@gmail.com';
```

### Method 3: Python Script (When Network is Stable)

If you want to retry the Python script later:

```bash
cd backend
py setup_auth_simple.py
```

**Note**: This may timeout due to network connectivity issues.

## ðŸ§ª Testing Authentication

Once the user is created, test the login:

### API Test
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"ganeshkhovalan2203@gmail.com","password":"[REDACTED_PASSWORD]"}'
```

**Expected Response**:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Frontend Test
1. Start frontend: `npm run dev` (in webapp folder)
2. Go to: http://localhost:3000
3. Login with:
   - Email: `ganeshkhovalan2203@gmail.com`
   - Password: `[REDACTED_PASSWORD]`

## âœ… Verification Checklist

After setup, verify these work:

- [ ] **Supabase Auth User**: Exists and confirmed
- [ ] **Database User**: Email updated to match
- [ ] **API Login**: Returns valid JWT token
- [ ] **Frontend Login**: Redirects to dashboard
- [ ] **Protected Routes**: Accessible with authentication
- [ ] **User Profile**: Shows correct name and role

## ðŸ”§ Configuration Files

### Environment Variables (Already Configured)
```env
SUPABASE_URL=https://[REDACTED_PROJECT_ID].supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
SUPABASE_ANON_KEY=eyJ...
```

### Current Database User Record
```sql
-- This is what needs to be updated:
id: 'user-1' (needs to match Supabase Auth user ID)
email: 'ganesh@rootedai.co.in' (change to: 'ganeshkhovalan2203@gmail.com')
name: 'Ganesh Khovalan'
role: 'admin'
org_id: 'rooted-ai-org'
```

## ðŸ› Troubleshooting

### Issue: "Invalid email or password"
**Cause**: Auth user doesn't exist in Supabase Auth  
**Solution**: Create user via Supabase Dashboard (Method 1)

### Issue: "User record not found"
**Cause**: Database user email doesn't match Auth user email  
**Solution**: Run the UPDATE query to sync emails

### Issue: Connection timeout
**Cause**: Network connectivity to Supabase  
**Solution**: Use Supabase Dashboard instead of Python scripts

### Issue: "Access token expired"
**Cause**: JWT token expired (default: 1 hour)  
**Solution**: Login again or implement refresh token logic

## ðŸŽ¯ Next Steps After Authentication Works

1. âœ… Complete end-to-end testing
2. âœ… Test all API endpoints with authentication
3. âœ… Verify frontend user flows
4. âœ… Test protected routes and authorization
5. âœ… Validate user profile and organization data

## ðŸ“ž Support

**Quick Setup Command**:
```bash
# After creating Auth user in Dashboard, run:
UPDATE users SET email = 'ganeshkhovalan2203@gmail.com' WHERE email = 'ganesh@rootedai.co.in';
```

**Verification Command**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d '{"email":"ganeshkhovalan2203@gmail.com","password":"[REDACTED_PASSWORD]"}'
```

---

**ðŸ” Authentication setup ready! Follow Method 1 for the fastest results.**
