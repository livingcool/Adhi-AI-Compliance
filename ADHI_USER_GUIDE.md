# 📚 Adhi Compliance Platform - Complete User Guide

## 🌟 Welcome to Adhi Compliance

Adhi Compliance is your comprehensive AI governance platform that automates compliance monitoring, risk assessment, and bias auditing across global regulations including EU AI Act, GDPR, NIST AI RMF, and more.

## 🚀 Getting Started

### 1. Accessing the Platform

**Login Credentials (Demo Account):**
- **URL**: `http://localhost:3000` (local) or your deployed URL
- **Email**: `ganesh@rootedai.co.in`
- **Password**: `demo123`

### 2. First Login Experience

1. **Navigate** to the login page
2. **Enter** your email and password
3. **Click** "Sign In"
4. **Welcome!** You'll land on the main dashboard

### 3. Platform Overview

Upon login, you'll see:
- **Dashboard**: Executive overview of your AI compliance posture
- **Navigation Menu**: Access to all platform features
- **Organization**: RootedAI (demo organization)
- **User Role**: Admin (full access to all features)

## 🏠 Dashboard Overview

### Main Dashboard Widgets

**📊 Compliance Score**
- **Current Score**: 78.2%
- **Trend**: Shows improvement over time
- **Goal**: Aim for >85% for audit readiness

**🤖 AI Systems Summary**
- **Total Systems**: 5 active AI systems
- **Risk Distribution**: High (1), Limited (3), Minimal (1)
- **Status**: Operational, Testing, Development

**⚠️ Risk Alerts**  
- **High Priority**: Systems requiring immediate attention
- **Medium Priority**: Compliance gaps to address
- **Low Priority**: Optimization opportunities

**📈 Compliance Trends**
- **30-day trend**: Compliance score progression
- **Regulation breakdown**: EU AI Act, GDPR, NIST coverage
- **Upcoming deadlines**: Critical dates to track

## 🤖 AI Systems Management

### Viewing AI Systems

**Navigate**: Dashboard → AI Systems

**Current Demo Systems:**
1. **Voter Verification System** (High Risk)
   - Type: Electoral identity verification
   - Status: Production
   - Compliance: 85% complete

2. **Resume Screening AI** (Limited Risk)
   - Type: HR automation and candidate ranking
   - Status: Testing  
   - Compliance: 72% complete

3. **Fraud Detection Engine** (Limited Risk)
   - Type: Financial security and risk assessment
   - Status: Production
   - Compliance: 80% complete

4. **Content Moderation AI** (Minimal Risk)
   - Type: Platform safety and content filtering
   - Status: Production
   - Compliance: 90% complete

5. **Predictive Analytics** (Minimal Risk)
   - Type: Business intelligence and forecasting
   - Status: Development
   - Compliance: 65% complete

### Adding a New AI System

1. **Click** "Add AI System" button
2. **Fill in details**:
   - **Name**: Descriptive system name
   - **Description**: Purpose and functionality
   - **Risk Category**: Select from EU AI Act categories
   - **Deployment Status**: Development/Testing/Production
   - **Data Sources**: Input data types
   - **Use Cases**: Primary applications

3. **Configure** technical details:
   - **Model Type**: ML algorithm used
   - **Training Data**: Dataset information
   - **Performance Metrics**: Accuracy, bias measures
   - **Update Frequency**: Model retraining schedule

4. **Save** and proceed to compliance assessment

### Editing AI System Details

1. **Click** on any AI system in the list
2. **View** detailed information panel
3. **Click** "Edit" to modify details
4. **Update** any fields as needed
5. **Save** changes

## ✅ Compliance Management

### Understanding Compliance Checks

**Navigate**: AI Systems → Select System → Compliance Tab

**Compliance Categories:**

**📋 EU AI Act Compliance**
- Risk classification validation
- Prohibited practice checks
- High-risk system requirements
- Transparency obligations
- Human oversight requirements

**🔒 GDPR Compliance**
- Data processing lawfulness
- Data subject rights
- Privacy by design
- Data protection impact assessment
- Consent management

**🛡️ NIST AI RMF Compliance**  
- AI system governance
- Risk management processes
- Trustworthy AI characteristics
- Continuous monitoring
- Documentation requirements

**🌍 Regional Regulations**
- US state laws (California, Illinois, etc.)
- Canada PIPEDA requirements
- Singapore AI governance
- China AI regulations

### Performing Compliance Assessments

**Starting an Assessment:**

1. **Select** an AI system
2. **Click** "Start Compliance Assessment"
3. **Choose** regulation framework (EU AI Act, GDPR, etc.)
4. **Answer** assessment questions:
   - System purpose and functionality
   - Data processing activities
   - Risk mitigation measures
   - Documentation completeness

5. **Submit** assessment for review

**Assessment Results:**

- **Compliant**: ✅ No action needed
- **Partially Compliant**: ⚠️ Minor gaps identified
- **Non-Compliant**: ❌ Significant issues requiring attention
- **Pending**: ⏳ Assessment in progress

### Managing Compliance Gaps

**Viewing Gaps:**
1. **Navigate** to Compliance Dashboard
2. **Filter** by status: "Non-Compliant" or "Partially Compliant"
3. **Review** identified gaps and requirements

**Addressing Gaps:**
1. **Click** on a compliance check
2. **Review** detailed requirements
3. **Add** remediation notes
4. **Set** target completion date
5. **Assign** responsible team member
6. **Upload** supporting documentation
7. **Mark** as "In Progress" or "Complete"

## ⚖️ Bias Auditing

### Understanding Bias Audits

**Navigate**: Dashboard → Bias Audits

Bias auditing helps identify unfair treatment across demographic groups in your AI systems.

**Current Demo Audits:**

**1. Resume Screening Bias Audit**
- **Status**: Complete
- **Findings**: Gender bias detected (72% male preference)
- **Recommendations**: Rebalance training data, implement fairness constraints

**2. Fraud Detection Fairness Review** 
- **Status**: Complete
- **Findings**: Age bias detected (higher false positives for 65+)
- **Recommendations**: Age-sensitive thresholds, additional validation

**3. Content Moderation Bias Assessment**
- **Status**: In Progress
- **Focus**: Language and cultural bias detection
- **Timeline**: 2 weeks remaining

### Conducting a Bias Audit

**Step 1: Audit Setup**
1. **Select** AI system to audit
2. **Choose** bias audit type:
   - **Demographic Parity**: Equal outcomes across groups
   - **Equalized Odds**: Equal true/false positive rates
   - **Calibration**: Equal prediction accuracy
   - **Individual Fairness**: Similar treatment for similar individuals

3. **Define** protected attributes (gender, age, race, etc.)
4. **Upload** test dataset with demographic labels

**Step 2: Statistical Analysis**
- **Automated analysis** runs fairness metrics
- **Generate reports** with statistical significance
- **Identify bias** patterns and affected groups
- **Calculate** fairness scores across attributes

**Step 3: Review Results**
- **Review** bias metrics and visualizations
- **Analyze** disparate impact across groups  
- **Understand** root causes of bias
- **Prioritize** remediation efforts

**Step 4: Remediation Planning**
1. **Document** findings and recommendations
2. **Create** remediation plan with timelines
3. **Assign** responsible team members
4. **Set** follow-up audit schedule
5. **Track** progress on improvements

### Interpreting Bias Metrics

**Key Metrics Explained:**

**📊 Demographic Parity Ratio**
- **Range**: 0.8 - 1.2 (acceptable)
- **Interpretation**: Ratio of positive outcomes between groups
- **Example**: 0.72 means one group gets 72% the positive rate of another

**📈 Equalized Odds Difference**  
- **Range**: < 0.1 (good), < 0.05 (excellent)
- **Interpretation**: Difference in true positive rates
- **Example**: 0.15 means 15% difference in accuracy between groups

**📋 Calibration Score**
- **Range**: 0-1 (higher is better)
- **Interpretation**: How well predictions match actual outcomes
- **Example**: 0.85 means predictions are 85% calibrated

## 🚨 Incident Management

### Understanding AI Incidents

**Navigate**: Dashboard → Incidents

AI incidents are issues that affect system performance, compliance, or user experience.

**Demo Incidents:**

**1. Voter Verification False Positives**
- **Severity**: High
- **Status**: Resolved  
- **Impact**: 0.3% false rejection rate
- **Resolution**: Algorithm tuning, additional validation

**2. Resume Screening Bias Alert**
- **Severity**: Medium
- **Status**: In Progress
- **Impact**: Gender bias in candidate ranking
- **Action**: Bias audit initiated, training data review

**3. Content Moderation Accuracy Drop**
- **Severity**: Low
- **Status**: Monitoring
- **Impact**: 2% decrease in accuracy
- **Action**: Model performance monitoring increased

### Reporting a New Incident

**Step 1: Incident Detection**
1. **Click** "Report Incident"
2. **Select** affected AI system
3. **Choose** incident type:
   - **Performance Issue**: Accuracy, latency, availability
   - **Bias/Fairness**: Discriminatory outcomes
   - **Privacy/Security**: Data breaches, unauthorized access
   - **Compliance**: Regulatory violations
   - **Ethical**: Harmful or inappropriate outputs

**Step 2: Incident Details**
1. **Describe** the issue in detail
2. **Set** severity level (Low/Medium/High/Critical)
3. **Estimate** impact and affected users
4. **Add** supporting evidence (logs, screenshots, data)
5. **Assign** incident response team

**Step 3: Response Actions**
1. **Immediate containment** measures
2. **Impact assessment** and user notification
3. **Root cause analysis** 
4. **Remediation plan** development
5. **Implementation** and testing
6. **Post-incident review** and lessons learned

### Incident Response Workflow

**🔴 Critical Incidents (P0)**
- **Response Time**: < 1 hour
- **Actions**: Immediate containment, executive notification
- **Examples**: Data breach, system compromise, severe bias

**🟡 High Priority (P1)**  
- **Response Time**: < 4 hours
- **Actions**: Rapid assessment, user communication
- **Examples**: Performance degradation, compliance violation

**🟠 Medium Priority (P2)**
- **Response Time**: < 24 hours  
- **Actions**: Investigation, planned remediation
- **Examples**: Minor bias detection, accuracy drift

**🟢 Low Priority (P3)**
- **Response Time**: < 1 week
- **Actions**: Analysis, optimization planning
- **Examples**: Documentation gaps, minor performance issues

### Regulatory Reporting

For incidents requiring regulatory notification:

1. **Assess** reporting obligations by jurisdiction
2. **Prepare** incident summary and impact analysis
3. **Generate** regulatory filing documentation
4. **Submit** within required timeframes (typically 24-72 hours)
5. **Track** regulatory response and follow-up requirements

## 📊 Analytics & Reporting

### Executive Dashboard

**Navigate**: Dashboard → Executive View

**Key Metrics:**
- **Overall Compliance Score**: Weighted average across all systems
- **Risk Distribution**: Breakdown by EU AI Act risk categories  
- **Trending**: Month-over-month compliance improvements
- **Upcoming Deadlines**: Critical compliance dates

### Detailed Analytics

**Compliance Analytics:**
- **Regulation Coverage**: Gaps across different frameworks
- **System Performance**: Individual AI system compliance scores
- **Historical Trends**: Compliance improvement over time
- **Benchmark Comparison**: Industry and peer comparisons

**Risk Analytics:**
- **Risk Heat Map**: Visual risk distribution across systems
- **Risk Trends**: Risk score changes over time
- **Mitigation Effectiveness**: Success of risk reduction efforts
- **Predictive Risk**: Forecasted risk based on trends

**Bias Analytics:**
- **Fairness Metrics**: Comprehensive bias measurements
- **Group Comparisons**: Performance across demographic groups
- **Bias Trends**: Fairness improvements over time
- **Impact Assessment**: Effect of bias on different populations

### Custom Reports

**Creating Custom Reports:**

1. **Navigate** to Reports section
2. **Select** report type:
   - **Compliance Summary**: High-level status overview
   - **Detailed Assessment**: In-depth compliance analysis
   - **Risk Report**: Risk assessment and mitigation status
   - **Bias Audit Report**: Fairness and bias analysis
   - **Incident Summary**: Incident tracking and resolution

3. **Configure** report parameters:
   - Date range
   - AI systems to include
   - Regulations to cover
   - Stakeholder audience
   - Detail level

4. **Generate** and download report (PDF, Excel, CSV)

### Automated Reporting

**Schedule regular reports:**
- **Weekly**: Operational dashboards for teams
- **Monthly**: Executive summaries for leadership  
- **Quarterly**: Board reports and regulatory updates
- **Annual**: Comprehensive compliance and risk assessments

## 🔧 Settings & Configuration

### User Profile Management

**Navigate**: Top-right user menu → Profile

**Update your profile:**
- **Personal Information**: Name, title, contact details
- **Notification Preferences**: Email alerts, frequency
- **Dashboard Customization**: Widget preferences, layout
- **Security Settings**: Password change, 2FA setup

### Organization Settings  

**Navigate**: Settings → Organization

**Configure organization details:**
- **Company Information**: Name, industry, size
- **Regulatory Scope**: Applicable jurisdictions and regulations
- **Risk Tolerance**: Acceptable risk thresholds
- **Compliance Standards**: Internal policies and procedures

### System Configuration

**AI System Templates:**
- Create templates for common AI system types
- Define standard compliance checklists
- Set default risk assessments
- Configure automated monitoring

**Compliance Frameworks:**
- Enable/disable specific regulations
- Customize compliance criteria
- Set assessment schedules
- Configure gap tracking

## 🔔 Notifications & Alerts

### Understanding Notifications

**Notification Types:**
- **🚨 Critical Alerts**: Immediate attention required
- **⚠️ Warnings**: Important updates and deadlines
- **ℹ️ Information**: Status updates and completions
- **📅 Reminders**: Upcoming tasks and assessments

### Configuring Alerts

**Navigate**: Settings → Notifications

**Alert Categories:**
1. **Compliance Deadlines**: Upcoming assessment and audit dates
2. **Risk Changes**: AI system risk score modifications
3. **Incident Updates**: New incidents and status changes
4. **Bias Alerts**: Fairness metric threshold breaches
5. **System Health**: Performance and availability issues

**Notification Channels:**
- **Email**: Detailed notifications with context
- **In-App**: Real-time dashboard alerts
- **Slack/Teams**: Integration with team communication tools
- **SMS**: Critical alerts for immediate response

### Managing Notification Preferences

**Frequency Settings:**
- **Immediate**: Real-time alerts for critical issues
- **Daily Digest**: Consolidated summary of all notifications
- **Weekly Summary**: High-level status and trend updates
- **Monthly Report**: Comprehensive monthly overview

**Customization Options:**
- Filter by AI system or regulation
- Set severity thresholds
- Define escalation rules
- Configure quiet hours

## 🔒 Security & Privacy

### Data Security

**Platform Security Features:**
- **Encryption**: TLS 1.3 in transit, AES-256 at rest
- **Authentication**: Multi-factor authentication supported
- **Authorization**: Role-based access control (RBAC)
- **Audit Logging**: Comprehensive activity tracking
- **Data Isolation**: Multi-tenant architecture

### Privacy Controls

**Data Processing:**
- **Purpose Limitation**: Data used only for stated purposes
- **Data Minimization**: Collect only necessary information
- **Retention Policies**: Automatic data deletion schedules
- **Right to Erasure**: User data deletion on request

**Consent Management:**
- Clear consent for all data processing
- Granular consent options
- Easy consent withdrawal
- Consent audit trails

### Compliance Certifications

**Current Certifications:**
- **SOC 2 Type II**: Security and availability controls
- **ISO 27001**: Information security management
- **GDPR Compliance**: EU data protection requirements
- **Privacy Shield**: US-EU data transfer framework

## 🆘 Help & Support

### Getting Help

**In-App Help:**
- **Help Icon** (?) throughout the platform
- **Contextual tooltips** on complex features
- **Step-by-step guides** for common tasks
- **Video tutorials** for advanced features

**Support Channels:**
- **Email Support**: info@rootedai.co.in
- **Phone Support**: +91 7904168521
- **Knowledge Base**: Comprehensive documentation
- **Community Forum**: User discussion and tips

### Common Questions

**Q: How do I add a new AI system?**
A: Navigate to AI Systems → Click "Add AI System" → Fill in details → Save

**Q: What if my compliance score is low?**  
A: Review the compliance checks with "Non-Compliant" status, address the gaps, and update the status

**Q: How often should I run bias audits?**
A: Recommended: Quarterly for production systems, after each model update

**Q: What happens if I find a critical incident?**
A: Report immediately, follow the incident response workflow, notify relevant stakeholders

**Q: Can I customize the dashboard?**
A: Yes, go to Profile → Dashboard Preferences to customize widgets and layout

### Training Resources

**Getting Started Guide:**
- 30-minute platform overview
- Key feature demonstrations
- Common workflow walkthroughs
- Best practices and tips

**Advanced Features Training:**
- Custom compliance frameworks
- Advanced bias analysis
- Integration with ML platforms
- Automated reporting setup

**Compliance Specific Training:**
- EU AI Act compliance strategies
- GDPR data governance  
- NIST AI RMF implementation
- Industry-specific regulations

### Troubleshooting

**Common Issues:**

**Login Problems:**
1. Check email/password accuracy
2. Clear browser cache and cookies
3. Try incognito/private browser mode
4. Contact support if issues persist

**Data Loading Issues:**
1. Refresh the page
2. Check internet connection
3. Try different browser
4. Report persistent issues

**Performance Issues:**  
1. Close unnecessary browser tabs
2. Clear browser cache
3. Check system requirements
4. Use supported browsers (Chrome, Firefox, Safari, Edge)

**Missing Data:**
1. Verify you have proper access permissions
2. Check if data exists for selected filters
3. Try broader date ranges or filters
4. Contact administrator for access issues

## 📈 Best Practices

### Getting the Most from Adhi Compliance

**Daily Activities:**
- Review dashboard for new alerts
- Check incident status updates
- Monitor compliance score trends
- Address high-priority gaps

**Weekly Activities:**
- Analyze compliance analytics
- Review bias audit progress
- Update incident resolutions
- Plan upcoming assessments

**Monthly Activities:**
- Conduct comprehensive system reviews
- Generate executive reports
- Plan bias audits for next quarter
- Review and update risk assessments

### Optimization Tips

**Improving Compliance Scores:**
1. **Prioritize high-impact gaps** with quick wins
2. **Automate compliance checks** where possible
3. **Regular assessment schedules** for consistency
4. **Cross-functional collaboration** with legal and technical teams

**Effective Bias Auditing:**
1. **Regular audit schedule** (quarterly minimum)
2. **Diverse test datasets** representing user population
3. **Multiple fairness metrics** for comprehensive analysis
4. **Remediation tracking** with measurable improvements

**Incident Prevention:**
1. **Proactive monitoring** with automated alerts
2. **Regular system health checks**
3. **Bias detection** in production systems
4. **Team training** on incident response

### Regulatory Readiness

**Audit Preparation:**
- Maintain comprehensive documentation
- Regular compliance assessments
- Clear incident tracking and resolution
- Up-to-date risk assessments

**Regulatory Changes:**
- Subscribe to regulatory updates
- Assess impact on current systems
- Plan compliance gap remediation
- Update assessment frameworks

## 🚀 Advanced Features

### API Integration

**Accessing the API:**
- **API Documentation**: Available at `/docs` when backend is running
- **Authentication**: JWT token-based authentication
- **Rate Limits**: 1000 requests/hour per user
- **SDKs**: Python and JavaScript SDKs available

**Common API Use Cases:**
- Automated compliance reporting
- Integration with CI/CD pipelines
- Custom dashboard development
- Bulk data import/export

### Workflow Automation

**Automated Workflows:**
1. **Compliance Assessments**: Scheduled recurring assessments
2. **Bias Audits**: Triggered by model updates or schedules  
3. **Incident Response**: Automated notification and escalation
4. **Report Generation**: Scheduled executive and team reports

### Custom Compliance Frameworks

**Building Custom Frameworks:**
1. Define regulation requirements
2. Create assessment questionnaires
3. Set compliance criteria and scoring
4. Configure remediation workflows

**Industry-Specific Templates:**
- Financial services (PCI DSS, SOX)
- Healthcare (HIPAA, GDPR)
- Government (FedRAMP, FISMA)  
- Automotive (ISO 26262)

## 📞 Contact & Support

### RootedAI Support

**Technical Support:**
- **Email**: info@rootedai.co.in
- **Phone**: +91 7904168521
- **Hours**: 9 AM - 6 PM IST, Monday-Friday
- **Emergency**: 24/7 for critical incidents

**Business Inquiries:**
- **Sales**: info@rootedai.co.in
- **Partnerships**: Available for enterprise integrations
- **Custom Development**: Available for specialized requirements

### Training & Consulting

**Available Services:**
- **Platform Training**: User and administrator training
- **Compliance Consulting**: Regulatory strategy and implementation
- **Custom Development**: Tailored features and integrations
- **Managed Services**: Ongoing compliance management

---

## 🎯 Quick Reference Card

### Daily Checklist
- [ ] Check dashboard alerts
- [ ] Review new incidents
- [ ] Update compliance progress
- [ ] Address urgent gaps

### Weekly Checklist  
- [ ] Analyze compliance trends
- [ ] Review bias audit progress
- [ ] Generate team reports
- [ ] Plan upcoming assessments

### Monthly Checklist
- [ ] Executive report generation
- [ ] Comprehensive system review
- [ ] Bias audit planning
- [ ] Risk assessment updates

### Emergency Contacts
- **Critical Incidents**: info@rootedai.co.in
- **Technical Issues**: +91 7904168521
- **Compliance Questions**: Available via platform chat

---

**Welcome to responsible AI governance with Adhi Compliance! 🚀**

*For the latest updates and features, visit [rootedai.co.in](https://rootedai.co.in)*