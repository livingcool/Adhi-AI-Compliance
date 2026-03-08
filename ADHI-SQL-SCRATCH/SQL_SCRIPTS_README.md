# Adhi Compliance AI - SQL Scripts Documentation

Complete SQL script collection for setting up the Adhi Compliance AI database from scratch.

## 📦 What's Included

### Individual Scripts (Execute in Order)
1. **01_drop_all_tables.sql** - Clean wipe of all existing tables
2. **02_create_types_and_functions.sql** - Custom types and utility functions  
3. **03_create_core_tables.sql** - User management and authentication
4. **04_create_compliance_tables.sql** - Compliance frameworks and monitoring
5. **05_create_risk_tables.sql** - Risk management and assessments
6. **06_create_ai_governance_tables.sql** - AI model governance and data governance
7. **07_create_alerts_reporting_tables.sql** - Alerts, notifications, and reporting
8. **08_create_indexes_and_performance.sql** - Performance indexes and optimization
9. **09_create_triggers_and_audit.sql** - Audit trails and automated triggers
10. **10_insert_sample_data.sql** - Sample data and admin users

### Master Scripts
- **00_EXECUTE_ALL.sql** - Master script that runs all scripts in order (PostgreSQL \i syntax)
- **ADHI_COMPLETE_DATABASE_SETUP.sql** - Single combined script with all SQL

## 🚀 Quick Start

### Option 1: Single Combined Script (Recommended)
```sql
-- Connect to your database and execute:
\i ADHI_COMPLETE_DATABASE_SETUP.sql
```

### Option 2: Master Script with Individual Files
```sql
-- Make sure all scripts are in the same directory, then:
\i 00_EXECUTE_ALL.sql
```

### Option 3: Manual Step-by-Step
Execute each script individually in numerical order:
```sql
\i 01_drop_all_tables.sql
\i 02_create_types_and_functions.sql
-- ... continue with all scripts in order
```

## 🔧 Database Setup Requirements

### Prerequisites
- **PostgreSQL 12+** (recommended 14+)
- **Database permissions:** CREATE, DROP, ALTER, INSERT
- **Extensions needed:** None (all standard PostgreSQL)

### Compatible With
- ✅ Supabase
- ✅ AWS RDS PostgreSQL
- ✅ Google Cloud SQL
- ✅ Azure Database for PostgreSQL
- ✅ Local PostgreSQL

## 🎯 What Gets Created

### 21 Core Tables
- **User Management** (5 tables): users, user_sessions, user_roles, password_reset_tokens, email_verification_tokens
- **Compliance** (5 tables): compliance_frameworks, regulation_requirements, compliance_checks, compliance_evidence, compliance_test_results
- **Risk Management** (6 tables): risk_categories, risk_assessments, risk_mitigations, risk_incidents, risk_monitoring, risk_monitoring_data
- **AI Governance** (3 tables): ai_model_governance, ai_model_monitoring, data_governance, data_processing_activities
- **Alerts & Reporting** (4 tables): compliance_alerts, user_notifications, notification_templates, compliance_reports, document_attachments, audit_trails

### Built-in Features
- **Complete audit trail** on all changes
- **Automatic timestamps** with triggers
- **Performance indexes** for fast queries
- **Data validation** with constraints and triggers
- **Notification system** with templates
- **Role-based access control**
- **AI bias monitoring** and model governance
- **GDPR compliance** features

### Default Admin Accounts
| Email | Password | Role |
|-------|----------|------|
| admin@adhi.com | admin123 | admin |
| compliance@adhi.com | admin123 | compliance_officer |
| auditor@adhi.com | admin123 | auditor |
| manager@adhi.com | admin123 | manager |
| demo@adhi.com | admin123 | user |

⚠️ **Change passwords immediately in production!**

## 📊 Sample Data Included

### Compliance Frameworks
- ✅ GDPR (General Data Protection Regulation)
- ✅ SOX (Sarbanes-Oxley Act)
- ✅ HIPAA (Health Insurance Portability and Accountability Act)
- ✅ ISO 27001 (Information Security Management)
- ✅ PCI DSS (Payment Card Industry Data Security Standard)
- ✅ CCPA (California Consumer Privacy Act)
- ✅ EU AI Act (European Union AI Regulation)
- ✅ NIST AI RMF (AI Risk Management Framework)

### Risk Categories
- Data Privacy Risk
- Cybersecurity Risk
- AI/ML Risk
- Regulatory Compliance Risk
- Financial Risk
- Operational Risk

### Notification Templates
- Compliance deadline reminders
- Risk escalation alerts
- Audit notifications
- Data breach alerts
- AI model drift warnings

## 🔍 Verification Queries

After setup, run these queries to verify everything worked:

```sql
-- Check table creation
SELECT COUNT(*) as total_tables 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Check sample data
SELECT 'users' as table_name, COUNT(*) as records FROM users
UNION ALL
SELECT 'compliance_frameworks', COUNT(*) FROM compliance_frameworks
UNION ALL
SELECT 'regulation_requirements', COUNT(*) FROM regulation_requirements;

-- Check admin users
SELECT email, role, is_active 
FROM users 
WHERE role = 'admin';

-- Test login (verify password hashing works)
SELECT email, first_name, last_name 
FROM users 
WHERE email = 'admin@adhi.com';
```

## 🚨 Important Notes

### Security
- All passwords are bcrypt hashed
- Audit trail captures all changes
- Role-based permissions system
- Sensitive data flagging

### Performance
- 100+ optimized indexes
- Partial indexes for common filters
- JSONB GIN indexes for flexible queries
- Query performance optimizations

### Compliance
- GDPR-ready with data governance
- SOX compliance features
- AI governance and bias monitoring
- Complete audit trail for regulations

## 🔧 Customization

### Adding New Compliance Frameworks
```sql
INSERT INTO compliance_frameworks (name, short_name, description, category, status) 
VALUES ('Your Framework', 'YF', 'Framework description', 'Category', 'active');
```

### Adding New Risk Categories
```sql
INSERT INTO risk_categories (category_name, description, risk_factors, typical_controls)
VALUES ('New Risk Type', 'Description', ARRAY['factor1', 'factor2'], ARRAY['control1', 'control2']);
```

### Creating Custom Users
```sql
INSERT INTO users (email, password_hash, first_name, last_name, role)
VALUES ('user@company.com', '$2b$12$...', 'First', 'Last', 'user');
```

## 📈 Performance Tips

### For Large Datasets
- Partition audit_trails table by date
- Archive old records regularly
- Monitor query performance
- Use connection pooling

### Index Maintenance
```sql
-- Reindex if needed
REINDEX DATABASE your_database_name;

-- Update statistics
ANALYZE;
```

## 🐛 Troubleshooting

### Common Issues

**Error: "relation does not exist"**
- Ensure scripts run in correct order
- Check you're connected to the right database

**Error: "permission denied"**
- Verify database user has CREATE/ALTER permissions
- Check if connected as superuser for system functions

**Error: "function does not exist"**
- Run script 02 first (creates utility functions)
- Ensure PostgreSQL version supports used features

**Slow Performance**
- Run ANALYZE after data insertion
- Check if indexes were created properly
- Consider adjusting PostgreSQL memory settings

### Getting Help

1. Check PostgreSQL logs for detailed error messages
2. Verify all scripts completed without errors
3. Run verification queries to confirm setup
4. Check table/index counts match expectations

## 🎯 Next Steps

After successful setup:

1. **Change default passwords**
2. **Configure your application connection**
3. **Set up regular backups**
4. **Configure monitoring alerts**
5. **Customize frameworks for your needs**
6. **Train users on the system**

## 📞 Production Deployment

### Before Go-Live
- [ ] Change all default passwords
- [ ] Review and customize compliance frameworks
- [ ] Set up backup procedures
- [ ] Configure SSL connections
- [ ] Set up monitoring and alerting
- [ ] Train administrator users
- [ ] Perform security audit
- [ ] Test disaster recovery

---

**Built for Adhi Compliance AI - Complete enterprise compliance management platform**

*Ready for production deployment with full audit trail, risk management, and AI governance capabilities.*