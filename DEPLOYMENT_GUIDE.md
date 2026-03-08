# ðŸš€ Adhi Compliance - Deployment Guide

## Overview
Adhi Compliance is a production-ready AI compliance platform built for RootedAI, featuring automated risk classification, compliance monitoring, bias auditing, and regulatory tracking across multiple jurisdictions.

## ðŸ“Š Platform Statistics
- **Backend**: 78 API endpoints across 15 route files
- **Frontend**: 15 pages with responsive design  
- **Database**: 15 tables with proper relationships
- **Security**: JWT authentication, multi-tenancy, audit logging
- **Infrastructure**: Docker, Redis, Celery background tasks

## ðŸ›  Technology Stack

### Backend
- **FastAPI** 0.104.1 - High-performance Python web framework
- **SQLAlchemy** 2.0 - Database ORM with async support
- **Alembic** - Database migrations
- **Celery** + **Redis** - Background task processing
- **Pydantic** v2 - Data validation and serialization
- **PostgreSQL** (Supabase) - Production database

### Frontend  
- **Next.js** 16.1.4 - React framework with Turbopack
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **SWR** - Data fetching and caching
- **Framer Motion** - Smooth animations
- **shadcn/ui** - Premium UI components

## ðŸš€ Quick Start (Production)

### Option 1: Docker Deployment

1. **Clone and Setup**
```bash
git clone <repo>
cd Adhi
```

2. **Create Environment File**
```bash
# Create .env in root
SUPABASE_PASSWORD=your_actual_supabase_password
```

3. **Run with Docker Compose**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

4. **Access Platform**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Cloud Deployment

#### Vercel (Frontend)
```bash
cd webapp
npm install
npx vercel --prod
```

#### Railway/Render (Backend)
```bash
cd backend
# Deploy backend as Docker container
```

## ðŸ“¦ Database Setup

### 1. Create Supabase Tables
1. Go to [Supabase Dashboard](https://supabase.com/dashboard/project/[REDACTED_PROJECT_ID])
2. Click **SQL Editor** â†’ **New query**
3. Copy and run: `workspace/supabase_schema.sql`

### 2. Load Demo Data  
1. In SQL Editor, copy and run: `workspace/adhi_seed_data.sql`
2. This creates sample AI systems, compliance checks, and audit data

## ðŸŽ¯ Platform Features

### Dashboard
- **Compliance Overview** - System-wide compliance status
- **Risk Assessment** - AI system risk classifications  
- **Audit Timeline** - Recent compliance activities
- **Alerts & Notifications** - Critical compliance issues

### AI Systems Management
- **System Registry** - Catalog of all AI systems
- **Risk Classification** - EU AI Act risk categorization
- **Impact Assessment** - Automated compliance scoring
- **Model Cards** - Auto-generated documentation

### Compliance Monitoring
- **Regulation Tracking** - Multi-jurisdiction regulation database
- **Gap Analysis** - Automated compliance gap detection
- **Remediation Plans** - Step-by-step compliance roadmaps
- **Deadline Management** - Compliance timeline tracking

### Bias Auditing  
- **Automated Bias Detection** - Statistical fairness analysis
- **Demographic Analysis** - Protected group impact assessment
- **Audit Reports** - Comprehensive bias audit documentation
- **Remediation Tracking** - Bias mitigation progress monitoring

### Incident Management
- **Incident Reporting** - AI system issue tracking
- **Severity Assessment** - Impact-based incident classification
- **Response Timeline** - Incident resolution tracking
- **Regulatory Filing** - Automated compliance reporting

## ðŸ” Security Features

### Authentication
- **JWT-based authentication** with secure token handling
- **Role-based access control** (Admin, Member, Viewer)
- **Multi-tenancy** - Organization-level data isolation

### Data Protection
- **Audit logging** for all user actions
- **Data encryption** in transit and at rest
- **GDPR compliance** with data subject rights
- **Secure API endpoints** with proper validation

## ðŸ“Š Demo Data

The platform includes comprehensive demo data:

### Organizations
- **RootedAI** - Sample AI company with 5 AI systems

### AI Systems
1. **Voter Verification System** (High Risk)
   - 87.5% compliance score
   - Bias concerns for elderly voters
2. **Resume Screening AI** (Limited Risk)  
   - 92.3% compliance score
   - GDPR compliant
3. **Fraud Detection Engine** (Limited Risk)
   - 89.7% compliance score  
   - Fairness improvements needed
4. **Content Moderation AI** (Minimal Risk)
   - 95.1% compliance score
   - Low bias risk
5. **Predictive Analytics Platform** (Minimal Risk)
   - 91.8% compliance score
   - Business intelligence focus

### Regulations Covered
- **EU AI Act** - Comprehensive AI regulation
- **GDPR** - Data protection compliance
- **NIST AI RMF** - US risk management framework
- **CCPA** - California privacy rights
- **Algorithmic Accountability Act** - US algorithmic governance

## ðŸŽ® User Workflows

### 1. Compliance Manager Workflow
1. **Login** â†’ Dashboard overview
2. **Systems** â†’ Review AI system compliance scores
3. **Compliance** â†’ Check regulation gaps
4. **Reports** â†’ Generate compliance reports

### 2. AI Auditor Workflow  
1. **Bias** â†’ Review bias audit results
2. **Incidents** â†’ Investigate AI system issues
3. **Systems** â†’ Update risk assessments
4. **Monitoring** â†’ Track compliance metrics

### 3. Executive Workflow
1. **Dashboard** â†’ High-level compliance status
2. **Reports** â†’ Export compliance summaries
3. **Incidents** â†’ Review critical issues
4. **Settings** â†’ Manage organization preferences

## ðŸ“ˆ Production Considerations

### Scaling
- **Database**: Use Supabase Pro for production workloads
- **Caching**: Redis for session and API response caching
- **Background Jobs**: Celery workers for heavy processing
- **Monitoring**: Structured logging with JSON format

### Performance
- **Frontend**: Next.js SSR/SSG for optimal loading
- **Backend**: FastAPI async endpoints for concurrency  
- **Database**: Indexed queries and connection pooling
- **CDN**: Static asset delivery optimization

### Monitoring
- **Health Checks**: `/health` endpoint for uptime monitoring
- **Error Tracking**: Structured error logging
- **Performance Metrics**: API response time tracking
- **Compliance Alerts**: Automated deadline notifications

## ðŸš¨ Known Issues & Solutions

### Local Development
- **Server Startup**: If uvicorn crashes, use lightweight Docker deployment
- **Database**: Use Supabase hosted PostgreSQL instead of local
- **AI Models**: Lightweight embeddings implemented for faster startup

### Production Deployment
- **Environment Variables**: Ensure all secrets are properly configured
- **Database Migrations**: Run Alembic migrations in production
- **Static Files**: Configure proper static file serving

## ðŸ“ž Support

### Technical Documentation
- **API Docs**: Available at `/docs` when backend is running
- **Architecture**: See `Adhi_Compliance_Architecture.pdf`
- **Development Plan**: See `Adhi_Compliance_Development_Plan.pdf`

### Contact
- **Email**: info@rootedai.co.in
- **Website**: https://rootedai.co.in
- **Support**: Technical support available for deployment issues

---

## ðŸŽ‰ Platform Highlights

âœ… **Production-Ready**: Full Docker deployment with monitoring
âœ… **Regulatory Coverage**: EU AI Act, GDPR, NIST, CCPA compliance  
âœ… **Automated Auditing**: Bias detection and compliance scoring
âœ… **Multi-Tenant**: Organization-level data isolation
âœ… **Real-Time Monitoring**: Live compliance status tracking
âœ… **Enterprise Security**: JWT auth, audit logs, data encryption

**Adhi Compliance** - Engineering Intelligence for Enterprise AI Governance
