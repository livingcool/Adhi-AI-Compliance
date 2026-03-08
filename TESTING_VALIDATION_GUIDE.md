# 🧪 Adhi Compliance Platform - Testing & Validation Guide

## 📋 Overview

This guide covers comprehensive testing and validation strategies for the Adhi Compliance Platform across all components: backend API, frontend UI, database integrity, security, and performance.

## 🎯 Testing Strategy

### 1. Test Categories
- **Unit Tests** - Individual components and functions
- **Integration Tests** - API endpoints and database interactions  
- **End-to-End Tests** - Complete user workflows
- **Security Tests** - Authentication, authorization, data protection
- **Performance Tests** - Load testing and response times
- **Compliance Tests** - Regulatory requirement validation

### 2. Test Environment Setup

#### Backend Testing
```bash
cd backend
python -m pytest tests/ -v --tb=short
python run_endpoint_tests.py
python test_db.py
```

#### Frontend Testing  
```bash
cd webapp
npm test
npx playwright test
npm run test:e2e
```

#### Full Stack Testing
```bash
docker-compose -f docker-compose.yml up -d
python backend/run_endpoint_tests.py
npx playwright test --config=playwright.config.ts
```

## 🔧 Backend API Testing

### 1. Database Validation Tests

**File: `backend/test_db.py`**
```python
# Run database connectivity and schema validation
python test_db.py

# Expected Results:
✅ Database connection successful
✅ All 15 tables exist
✅ Demo data loaded (5 AI systems, 25+ compliance checks)
✅ Relationships intact
```

**Manual Database Checks:**
```sql
-- 1. Verify table structure
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'public' 
ORDER BY table_name, ordinal_position;

-- 2. Check data integrity
SELECT 
    'ai_systems' as table_name, COUNT(*) as count FROM ai_systems
UNION ALL
SELECT 'compliance_checks', COUNT(*) FROM compliance_checks
UNION ALL  
SELECT 'bias_audits', COUNT(*) FROM bias_audits
UNION ALL
SELECT 'incidents', COUNT(*) FROM incidents;

-- 3. Validate relationships
SELECT ai.name, COUNT(cc.id) as compliance_checks
FROM ai_systems ai
LEFT JOIN compliance_checks cc ON ai.id = cc.ai_system_id  
GROUP BY ai.id, ai.name;
```

### 2. API Endpoint Testing

**File: `backend/run_endpoint_tests.py`**

**Health Check Tests:**
```bash
curl -X GET http://localhost:8000/health
# Expected: {"status": "healthy", "timestamp": "..."}

curl -X GET http://localhost:8000/health/database  
# Expected: {"database": "connected", "tables": 15}
```

**Authentication Tests:**
```bash
# 1. Login with valid credentials
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"ganesh@rootedai.co.in","password":"demo123"}'

# Expected: {"access_token": "...", "token_type": "bearer"}

# 2. Test invalid credentials  
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"invalid","password":"wrong"}'
  
# Expected: 401 Unauthorized

# 3. Test protected endpoint without token
curl -X GET http://localhost:8000/api/ai-systems
# Expected: 401 Unauthorized

# 4. Test protected endpoint with valid token
curl -X GET http://localhost:8000/api/ai-systems \
  -H "Authorization: Bearer <token>"
# Expected: Array of AI systems
```

**CRUD Operations Tests:**

**AI Systems:**
```bash
# List all AI systems
curl -X GET http://localhost:8000/api/ai-systems \
  -H "Authorization: Bearer <token>"

# Get specific AI system
curl -X GET http://localhost:8000/api/ai-systems/1 \
  -H "Authorization: Bearer <token>"

# Create new AI system
curl -X POST http://localhost:8000/api/ai-systems \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test AI System",
    "description": "Test system for validation",
    "risk_category": "Limited Risk",
    "deployment_status": "Testing"
  }'
```

**Compliance Checks:**
```bash
# Get compliance checks for AI system
curl -X GET http://localhost:8000/api/ai-systems/1/compliance \
  -H "Authorization: Bearer <token>"

# Update compliance check status  
curl -X PUT http://localhost:8000/api/compliance/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"status": "Compliant", "notes": "Test update"}'
```

### 3. Dashboard API Tests

```bash
# Overview dashboard
curl -X GET http://localhost:8000/api/dashboard/overview \
  -H "Authorization: Bearer <token>"

# Risk distribution  
curl -X GET http://localhost:8000/api/dashboard/risk-distribution \
  -H "Authorization: Bearer <token>"

# Compliance trends
curl -X GET http://localhost:8000/api/dashboard/compliance-trends \
  -H "Authorization: Bearer <token>"
```

**Expected Dashboard Responses:**
```json
{
  "total_ai_systems": 5,
  "compliance_score": 78.2,
  "high_risk_systems": 1,
  "pending_audits": 2,
  "recent_incidents": 1
}
```

## 🌐 Frontend Testing

### 1. Component Testing

**Authentication Flow:**
- [ ] Login page renders correctly
- [ ] Valid credentials redirect to dashboard
- [ ] Invalid credentials show error message  
- [ ] Logout clears session and redirects
- [ ] Protected routes require authentication
- [ ] Session persistence across browser refresh

**Dashboard Components:**
- [ ] Overview widgets display correct data
- [ ] Charts and graphs render properly
- [ ] Real-time data updates work
- [ ] Responsive design on mobile/tablet
- [ ] Loading states show during API calls
- [ ] Error states handle API failures gracefully

### 2. Navigation Testing

- [ ] Main menu navigation works
- [ ] Breadcrumb navigation accurate
- [ ] URL routing handles all paths
- [ ] Back button functionality
- [ ] Deep links work correctly
- [ ] 404 page for invalid routes

### 3. Data Flow Testing

**AI Systems Page:**
- [ ] Table loads with demo data
- [ ] Search/filter functionality works
- [ ] Sorting by columns works
- [ ] Pagination handles large datasets  
- [ ] Detail view opens correctly
- [ ] Edit/delete operations function
- [ ] Real-time updates from API

**Compliance Dashboard:**
- [ ] Risk charts display correctly
- [ ] Compliance status updates
- [ ] Filter by regulation works
- [ ] Export functionality works
- [ ] Drill-down into details
- [ ] Historical data visualization

### 4. End-to-End Testing

**File: `webapp/e2e/` (Playwright Tests)**

**Complete User Journey:**
```typescript
// 1. Login Flow
test('user can login and access dashboard', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[name="email"]', 'ganesh@rootedai.co.in');
  await page.fill('[name="password"]', 'demo123');
  await page.click('[type="submit"]');
  await expect(page).toHaveURL('/dashboard');
});

// 2. AI System Management  
test('user can create and manage AI systems', async ({ page }) => {
  await loginUser(page);
  await page.goto('/ai-systems');
  await page.click('text=Add AI System');
  await page.fill('[name="name"]', 'E2E Test System');
  await page.selectOption('[name="risk_category"]', 'Limited Risk');
  await page.click('[type="submit"]');
  await expect(page.locator('text=E2E Test System')).toBeVisible();
});

// 3. Compliance Workflow
test('user can complete compliance assessment', async ({ page }) => {
  await loginUser(page);
  await page.goto('/compliance');
  await page.click('text=Start Assessment');
  // Fill compliance form
  await page.click('text=Submit Assessment');  
  await expect(page.locator('text=Assessment Complete')).toBeVisible();
});
```

**Running E2E Tests:**
```bash
cd webapp
npx playwright test
npx playwright test --headed  # Run with browser UI
npx playwright test --debug   # Debug mode
npx playwright show-report    # View test results
```

## 🔒 Security Testing

### 1. Authentication Security

**JWT Token Validation:**
```bash
# 1. Test token expiration
# Login and wait for token to expire (24 hours default)
curl -X GET http://localhost:8000/api/ai-systems \
  -H "Authorization: Bearer <expired_token>"
# Expected: 401 Unauthorized

# 2. Test invalid token format
curl -X GET http://localhost:8000/api/ai-systems \
  -H "Authorization: Bearer invalid.token.here"
# Expected: 401 Unauthorized

# 3. Test token manipulation
curl -X GET http://localhost:8000/api/ai-systems \
  -H "Authorization: Bearer <manipulated_token>"
# Expected: 401 Unauthorized
```

**Password Security:**
```bash
# Test weak password rejection (if implemented)
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"123"}'
# Expected: 400 Password too weak

# Test SQL injection in login
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin'\'' OR 1=1--","password":"anything"}'
# Expected: 401 Unauthorized (not SQL error)
```

### 2. Authorization Testing

**Role-Based Access Control:**
```bash
# Test admin-only endpoints with member token
curl -X DELETE http://localhost:8000/api/ai-systems/1 \
  -H "Authorization: Bearer <member_token>"
# Expected: 403 Forbidden

# Test organization data isolation
curl -X GET http://localhost:8000/api/ai-systems \
  -H "Authorization: Bearer <org2_token>"
# Expected: Only org2 data, not org1 data
```

### 3. Input Validation Testing

**SQL Injection:**
```bash
# Test in search parameters
curl -X GET "http://localhost:8000/api/ai-systems?search='; DROP TABLE ai_systems;--" \
  -H "Authorization: Bearer <token>"
# Expected: Safe query results, no SQL error

# Test in JSON inputs
curl -X POST http://localhost:8000/api/ai-systems \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test'\'' OR 1=1--","description":"hack attempt"}'
# Expected: Validation error or safe storage
```

**XSS Prevention:**
```bash
# Test script injection in inputs
curl -X POST http://localhost:8000/api/ai-systems \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"<script>alert(\"XSS\")</script>","description":"test"}'
# Expected: Script tags escaped or validation error
```

### 4. Rate Limiting Testing

```bash
# Test API rate limiting (if implemented)
for i in {1..100}; do
  curl -X GET http://localhost:8000/api/ai-systems \
    -H "Authorization: Bearer <token>" &
done
wait
# Expected: Some requests return 429 Too Many Requests
```

## ⚡ Performance Testing

### 1. Load Testing

**Using Apache Bench (ab):**
```bash
# Test concurrent users on dashboard
ab -n 1000 -c 10 -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/dashboard/overview

# Test database-heavy endpoint  
ab -n 500 -c 5 -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/ai-systems

# Test POST operations
ab -n 100 -c 2 -p test_data.json -T application/json \
  -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/compliance/assess
```

**Expected Performance Metrics:**
- **Response Time**: < 500ms for 95% of requests
- **Throughput**: > 100 requests/second  
- **Error Rate**: < 1% under normal load
- **Memory Usage**: Stable, no memory leaks
- **Database Connections**: Properly pooled and reused

### 2. Frontend Performance

**Core Web Vitals:**
```bash
# Using Lighthouse CLI
npm install -g lighthouse
lighthouse http://localhost:3000 --output=html --output-path=./performance-report.html

# Using Playwright performance testing
npx playwright test performance.spec.ts
```

**Expected Frontend Metrics:**
- **First Contentful Paint**: < 2 seconds
- **Largest Contentful Paint**: < 3 seconds
- **Time to Interactive**: < 4 seconds
- **Cumulative Layout Shift**: < 0.1
- **Performance Score**: > 90/100

### 3. Database Performance

```sql
-- Check slow queries
SELECT 
  query,
  calls,
  total_time,
  mean_time,
  rows
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Check table sizes
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT 
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes 
ORDER BY idx_scan DESC;
```

## ✅ Validation Checklist

### Pre-Deployment Validation

#### Backend Validation
- [ ] All 78 API endpoints respond correctly
- [ ] Database schema matches expected structure (15 tables)
- [ ] Demo data loads successfully (5 AI systems, 25+ checks)
- [ ] Authentication/authorization working
- [ ] Health checks pass
- [ ] No critical security vulnerabilities
- [ ] Performance meets SLA requirements

#### Frontend Validation  
- [ ] All 15 pages render correctly
- [ ] Authentication flow complete
- [ ] All API integrations working
- [ ] Responsive design tested (mobile/tablet/desktop)
- [ ] No JavaScript errors in console
- [ ] Accessibility requirements met (WCAG 2.1 AA)
- [ ] SEO optimization complete

#### Integration Validation
- [ ] Frontend-Backend API communication working
- [ ] Database transactions working correctly  
- [ ] Real-time updates functioning
- [ ] File upload/download working
- [ ] Email notifications working (if implemented)
- [ ] Background job processing working

### Production Readiness

#### Security Checklist
- [ ] HTTPS/TLS certificates configured
- [ ] Security headers implemented (CSP, HSTS, etc.)
- [ ] Sensitive data encrypted at rest
- [ ] Input validation on all endpoints
- [ ] SQL injection protection verified
- [ ] XSS protection implemented
- [ ] Rate limiting configured
- [ ] Audit logging active

#### Performance Checklist
- [ ] CDN configured for static assets
- [ ] Database queries optimized with indexes
- [ ] Caching strategy implemented
- [ ] Connection pooling configured
- [ ] Memory usage within limits
- [ ] CPU usage optimized
- [ ] Monitoring and alerting setup

#### Operational Checklist
- [ ] Automated backups configured
- [ ] Log aggregation setup
- [ ] Health monitoring active  
- [ ] Incident response procedures
- [ ] Rollback procedures tested
- [ ] Documentation complete
- [ ] Support contacts established

## 🐛 Common Issues & Troubleshooting

### Backend Issues

**Database Connection Errors:**
```bash
# Check database connectivity
python backend/test_db.py

# Common fixes:
# 1. Verify environment variables in .env
# 2. Check Supabase connection string
# 3. Ensure database is accessible from server
# 4. Verify firewall rules
```

**Authentication Issues:**
```bash
# Test JWT token generation
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"ganesh@rootedai.co.in","password":"demo123"}'

# Common fixes:
# 1. Check JWT_SECRET_KEY in environment
# 2. Verify user exists in database
# 3. Check password hashing algorithm
# 4. Ensure token expiration settings
```

**API Response Issues:**
```bash
# Check API documentation
http://localhost:8000/docs

# Common fixes:
# 1. Verify request format matches API spec
# 2. Check required vs optional parameters
# 3. Validate request headers
# 4. Check response status codes
```

### Frontend Issues

**Build Failures:**
```bash
cd webapp
npm run build

# Common fixes:
# 1. Clear node_modules and reinstall: rm -rf node_modules package-lock.json && npm install
# 2. Check TypeScript errors: npx tsc --noEmit
# 3. Update environment variables in .env.local
# 4. Check Next.js configuration in next.config.ts
```

**API Connection Issues:**
```bash
# Check API URL configuration
cat webapp/.env.local | grep API_URL

# Common fixes:
# 1. Verify NEXT_PUBLIC_API_URL points to backend
# 2. Check CORS configuration in backend
# 3. Verify network connectivity between frontend/backend
# 4. Check browser console for CORS errors
```

### Docker Issues

**Container Startup Failures:**
```bash
# Check container logs
docker logs adhi-backend
docker logs adhi-frontend

# Common fixes:
# 1. Verify environment variables in .env file
# 2. Check Dockerfile syntax
# 3. Ensure ports are not already in use
# 4. Check docker-compose.yml configuration
```

**Service Communication Issues:**
```bash
# Test service connectivity
docker exec -it adhi-backend curl http://adhi-frontend:3000
docker exec -it adhi-frontend curl http://adhi-backend:8000/health

# Common fixes:
# 1. Check Docker network configuration
# 2. Verify service names in docker-compose.yml
# 3. Check port mappings
# 4. Ensure services are in same network
```

## 📊 Test Reports

### Automated Test Results

**Backend Tests:**
```bash
cd backend
python -m pytest tests/ --html=reports/backend-test-report.html
```

**Frontend Tests:**  
```bash
cd webapp
npm test -- --coverage --watchAll=false
npx playwright test --reporter=html
```

**Coverage Reports:**
- **Backend**: Target > 80% code coverage
- **Frontend**: Target > 70% code coverage  
- **Integration**: All critical paths tested

### Manual Testing Checklist

**User Acceptance Testing (UAT):**
- [ ] Business stakeholder testing complete
- [ ] All user stories validated
- [ ] Edge cases tested
- [ ] Error scenarios handled
- [ ] User feedback incorporated
- [ ] Final approval received

## 📞 Testing Support

### Development Team
- **Lead**: Ganesh Khovalan (ganeshkhovalan2203@gmail.com)
- **Testing Issues**: Include test logs and error messages
- **Response Time**: < 24 hours for testing blockers

### Resources
- **Test Data**: Demo organization with sample AI systems
- **Test Accounts**: 
  - Admin: `ganesh@rootedai.co.in` / `demo123`
  - Member: Create additional test accounts as needed
- **Test Environment**: Local development or staging environment

---

**✅ Testing complete = Ready for production deployment!**