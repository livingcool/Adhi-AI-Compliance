# Adhi AI Compliance Platform

Enterprise AI-powered compliance management platform for comprehensive governance, risk management, and regulatory compliance.

## 🚀 Features

- **Complete Compliance Management** - GDPR, SOX, HIPAA, ISO 27001, PCI DSS
- **AI-Powered Risk Assessment** - Automated risk scoring and mitigation
- **Real-time Monitoring** - Continuous compliance monitoring and alerts
- **Document Management** - Secure evidence collection and retention
- **Audit Trail** - Complete audit trail for all system changes
- **AI Model Governance** - Bias monitoring and model oversight
- **Data Governance** - Privacy impact assessments and data protection
- **Automated Reporting** - Generate compliance reports automatically

## 🏗️ Tech Stack

- **Frontend**: Next.js 16, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python
- **Database**: PostgreSQL + Supabase
- **AI/ML**: OpenAI GPT, Claude, Gemini
- **Authentication**: Supabase Auth + JWT
- **File Storage**: Local/Cloud storage
- **Monitoring**: Custom analytics

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.9+
- PostgreSQL 14+
- Supabase account

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd Adhi-AI-Compliance
```

2. **Set up environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Install dependencies:**
```bash
# Frontend
npm install

# Backend
cd backend && pip install -r requirements.txt
```

4. **Set up database:**
```bash
# Run the SQL scripts to set up your database
# Use the provided SQL scripts in the /sql folder
```

5. **Start development servers:**
```bash
# Frontend
npm run dev

# Backend (in another terminal)
cd backend && python -m uvicorn main:app --reload
```

## 📁 Project Structure

```
Adhi-AI-Compliance/
├── frontend/           # Next.js frontend application
├── backend/           # FastAPI backend application  
├── database/          # Database scripts and migrations
├── docs/             # Documentation
├── sql/              # SQL setup scripts
├── uploads/          # File uploads directory
└── README.md
```

## ⚙️ Configuration

Key environment variables to configure:

- `DATABASE_URL` - PostgreSQL connection string
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase anonymous key
- `OPENAI_API_KEY` - OpenAI API key for AI features
- `CLAUDE_API_KEY` - Anthropic Claude API key
- `GEMINI_API_KEY` - Google Gemini API key

## 🔐 Security

- All passwords are bcrypt hashed
- JWT tokens for authentication
- Role-based access control
- Complete audit trail
- Data encryption at rest
- Secure file uploads

## 📊 Compliance Features

### Supported Frameworks
- ✅ GDPR (General Data Protection Regulation)
- ✅ SOX (Sarbanes-Oxley Act)
- ✅ HIPAA (Health Insurance Portability and Accountability Act)
- ✅ ISO 27001 (Information Security Management)
- ✅ PCI DSS (Payment Card Industry Data Security Standard)
- ✅ CCPA (California Consumer Privacy Act)
- ✅ EU AI Act (European Union AI Regulation)

### Key Capabilities
- Automated compliance checks
- Risk assessment and scoring
- Evidence collection and management
- Real-time alerts and notifications
- Comprehensive reporting
- AI model bias monitoring
- Data governance workflows

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is proprietary software owned by RootedAI.

## 🆘 Support

For support and questions:
- Email: support@rootedai.co.in
- Documentation: /docs
- Issues: Create an issue in this repository

---

**Built with ❤️ by RootedAI Team**
*Enterprise AI Solutions for Compliance and Risk Management*