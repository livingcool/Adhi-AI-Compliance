# Build Pipeline

## BATCH 1+2 (RUNNING NOW - 6 parallel agents)
1. warm-fjord: Security (JWT, multi-tenancy, pagination)
2. calm-mist: Frontend (real API, SWR, auth, responsive, animations)
3. fresh-ember: Infrastructure (Alembic, Celery, logging, Docker)
4. mild-ember: Testing (pytest, 12 test files, CI)
5. amber-tidepool: Quality (repositories, exceptions, notifications)
6. mellow-daisy: UI Components (17 premium components)

## STEP 2: INTEGRATION (after all 6 finish)
- Agent: integration_agent_prompt.txt
- Merge conflicts, wire components into pages, wire repos into routes

## STEP 3: PRODUCTION VALIDATION (after integration)
- Agent: validation_agent_prompt.txt
- Test EVERY endpoint, fix ALL bugs, security verification

## STEP 4: E2E TESTS (parallel with Step 3)
- Agent: e2e_test_prompt.txt
- Playwright tests for all pages, responsive, accessibility

## STEP 5: FINAL BUILD VERIFICATION
- Backend starts clean
- Frontend builds clean
- All pytest tests pass
- Playwright E2E tests pass
- Docker compose up works
