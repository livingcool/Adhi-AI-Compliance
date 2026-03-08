# AGENT COORDINATION — READ THIS FIRST

## Active Agents & Their Responsibilities

### Agent 1: Security (warm-fjord) — BACKEND
- Creating: app/middleware/auth.py (JWT validation, CurrentUser model, get_current_user, require_admin)
- Modifying: ALL route files to add auth + org_id scoping
- Modifying: app/config.py (SUPABASE_JWT_SECRET, CORS_ORIGINS)
- Modifying: app/main.py (CORS config)
- Creating: proper routes_auth.py (register, login, me, refresh)

### Agent 2: Frontend (calm-mist) — FRONTEND
- Creating: lib/fetcher.ts, lib/hooks.ts, lib/auth.ts
- Creating: app/login/page.tsx, components/AuthGuard.tsx, components/Skeleton.tsx, components/ErrorState.tsx
- Modifying: ALL page files to use real API via SWR hooks
- Modifying: components/Sidebar.tsx (responsive + animations)
- Adding: Framer Motion animations everywhere

### Agent 3: Infrastructure (fresh-ember) — BACKEND
- Creating: alembic/ directory + config
- Creating: app/workers/compliance_tasks.py (Celery background tasks)
- Creating: app/core/logging.py (structured JSON logging)
- Creating: app/services/audit_service.py + AuditLog model in models.py
- Creating: Dockerfile, docker-compose.yml
- Modifying: requirements.txt, README.md

### Agent 4: Testing (mild-ember) — BACKEND
- Creating: tests/ directory with all test files
- Creating: tests/conftest.py (fixtures, factories)
- Creating: .github/workflows/test.yml
- NOT modifying any source files — read only

### Agent 5: Quality (amber-tidepool) — BACKEND
- Creating: app/repositories/ directory (BaseRepository + all repos)
- Creating: app/core/exceptions.py (custom exceptions)
- Creating: app/core/pagination.py (PaginatedResponse)
- Creating: app/services/notification_service.py
- Creating: app/api/routes_regulation_mgmt.py
- Adding: Notification model to models.py
- Adding: database indexes to models.py

### Agent 6: UI Components (mellow-daisy) — FRONTEND
- Creating: components/ui/*.tsx (GlassCard, Modal, Toast, etc.)
- Creating: components/charts/*.tsx (RiskDistribution, ComplianceScore, etc.)
- Creating: components/PageTransition.tsx
- NOT modifying existing page files — only creating new components

## SHARED INTERFACES

### Backend CurrentUser Model (Agent 1 creates, all backend agents must use):
```python
class CurrentUser(BaseModel):
    id: str  # UUID
    email: str
    org_id: str  # UUID
    role: str  # admin | member | viewer
```

### Backend Dependency:
```python
from app.middleware.auth import get_current_user, require_admin, CurrentUser
# Use in routes: current_user: CurrentUser = Depends(get_current_user)
```

### Paginated Response (Agent 5 creates, all should use):
```python
class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int
    has_more: bool
```

### Frontend Auth Header (Agent 2 creates, Agent 6 should know):
```typescript
// lib/auth.ts
export const getToken = (): string | null => localStorage.getItem('adhi_token');
export const getAuthHeaders = () => ({ Authorization: `Bearer ${getToken()}` });
```

### Frontend SWR Fetcher (Agent 2 creates):
```typescript
// lib/fetcher.ts
const fetcher = (url: string) => fetch(url, { headers: getAuthHeaders() }).then(r => r.json());
```

### API Base URL:
- Backend: http://localhost:8000/api/v1
- Frontend proxy: /api/v1/* -> http://localhost:8000/api/v1/*

### Database Models (source of truth: app/store/models.py):
- User, CompanyProfile, AISystem, Regulation, ComplianceCheck, BiasAudit, Incident, ModelCard
- Agent 3 adds: AuditLog
- Agent 5 adds: Notification, database indexes

## CONFLICT RESOLUTION
- If you need to modify a file another agent is also modifying, READ the current state of the file first
- models.py: Agent 3 adds AuditLog, Agent 5 adds Notification + indexes — both should append, not overwrite
- main.py: Multiple agents modify — each should ADD their routers/middleware, not rewrite the whole file
- requirements.txt: Each agent APPENDS their dependencies, don't remove others'
- If unsure, CREATE a new file rather than modify an existing one
