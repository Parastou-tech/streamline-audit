# Cal Poly SLO Audit Management System

A comprehensive Streamlit-based audit management system designed for California Polytechnic State University, San Luis Obispo. This system provides separate dashboards for auditors and auditees, with secure document management, AI-powered analysis, and compliance tracking.

## 🌟 Features

### For Auditors
- **Audit Management**: Create and manage audits for different departments
- **Document Review**: Review uploaded documents with AI-powered analysis
- **Compliance Tracking**: Track document compliance status and generate reports
- **Notification System**: Send notifications to auditees about document requirements
- **Dashboard Analytics**: View audit statistics and progress metrics

### For Auditees
- **Document Upload**: Secure upload of various file types (PDF, Excel, Word, Images)
- **Audit Tracking**: View assigned audits and requirements
- **Status Monitoring**: Track document submission and approval status
- **Notifications**: Receive updates about audit requirements and document status

### Security Features
- **User Authentication**: Secure login system with role-based access
- **File Validation**: Comprehensive file type and size validation
- **Session Management**: Secure session handling with timeout
- **Data Encryption**: Secure storage of sensitive information

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager
- AWS account (optional, for cloud features)

### Installation

1. **Clone or download the project**
   ```bash
   cd cal-poly-audit-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run setup script**
   ```bash
   python setup.py
   ```

4. **Configure environment variables**
   - Edit the `.env` file with your configuration
   - Add AWS credentials if using cloud features
   - Configure email settings for notifications

5. **Start the application**
   ```bash
   streamlit run main.py
   ```

6. **Access the system**
   - Open your browser to `http://localhost:8501`
   - Login with default credentials:
     - **Auditor**: username=`auditor1`, password=`password123`
     - **Auditee**: username=`auditee1`, password=`password123`

## 📁 Project Structure

```
cal-poly-audit-system/
├── main.py                     # Main Streamlit application
├── setup.py                    # Setup and initialization script
├── requirements.txt            # Python dependencies
├── .env.template              # Environment variables template
├── README.md                  # This file
│
├── config/
│   └── settings.py            # Application configuration
│
├── auth/
│   └── authentication.py     # User authentication and management
│
├── dashboards/
│   ├── auditor_dashboard.py   # Auditor interface
│   └── auditee_dashboard.py   # Auditee interface
│
├── services/
│   ├── file_handler.py        # File upload and management
│   ├── aws_services.py        # AWS integration (Textract, S3)
│   ├── ai_services.py         # Claude AI integration
│   └── email_service.py       # Email notifications
│
├── utils/
│   ├── database_manager.py    # Database operations
│   └── session_manager.py     # Session management
│
├── data/                      # Database files
├── uploads/                   # Uploaded files storage
└── logs/                      # Application logs
```

## 🔧 Configuration

### Environment Variables

Edit the `.env` file with your configuration:

```env
# AWS Configuration (optional)
AWS_REGION=us-west-2
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
S3_BUCKET_NAME=your-bucket-name

# Claude AI (optional)
CLAUDE_API_KEY=your_claude_api_key

# Email Configuration
SMTP_SERVER=smtp.calpoly.edu
SMTP_PORT=587
SMTP_USERNAME=your_email_username
SMTP_PASSWORD=your_email_password
FROM_EMAIL=audit-system@calpoly.edu

# Security
SECRET_KEY=your-secure-secret-key
SESSION_TIMEOUT_MINUTES=60
```

### Supported File Types

The system supports the following file types:
- **Documents**: PDF, Word (.doc, .docx)
- **Spreadsheets**: Excel (.xlsx, .xls), CSV
- **Images**: JPEG, PNG, GIF
- **Maximum file size**: 50MB per file

## 👥 User Management

### Default Users

The system comes with default users for testing:

| Username | Password | Role | Department |
|----------|----------|------|------------|
| auditor1 | password123 | Auditor | Administration and Finance |
| auditee1 | password123 | Auditee | Academic Affairs |

### Creating New Users

Auditors can create new user accounts through the system interface, or you can add them directly to the database.

## 🔒 Security Features

### Authentication
- Secure password hashing using bcrypt
- Session-based authentication with timeout
- Role-based access control

### File Security
- File type validation and sanitization
- Virus scanning capability (configurable)
- Secure file storage with unique identifiers
- File integrity checking with SHA-256 hashes

### Data Protection
- SQL injection prevention with parameterized queries
- XSS protection through input sanitization
- Secure session management
- Environment-based configuration

## 🤖 AI Integration

### Claude AI Features (Optional)
- Document content analysis
- Compliance checking automation
- Intelligent document categorization
- Risk assessment and flagging

### AWS Textract Integration (Optional)
- Automatic text extraction from documents
- Form data recognition
- Table extraction from PDFs and images

## 📧 Email Notifications

The system can send email notifications for:
- New audit assignments
- Document upload confirmations
- Compliance status updates
- Deadline reminders

## 🛠️ Development

### Adding New Features

1. **New Dashboard Components**: Add to `dashboards/` directory
2. **New Services**: Add to `services/` directory
3. **Database Changes**: Update `config/settings.py` with new table schemas
4. **New File Types**: Update `ALLOWED_FILE_TYPES` in settings

### Database Schema

The system uses SQLite with the following main tables:
- `users`: User accounts and authentication
- `audits`: Audit information and requirements
- `documents`: Uploaded document metadata
- `notifications`: System notifications
- `audit_assignments`: Audit-to-user assignments

### Testing

Run the setup script to initialize test data:
```bash
python setup.py
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure the `data/` directory exists
   - Run `python setup.py` to initialize the database

2. **File Upload Issues**
   - Check file size (max 50MB)
   - Verify file type is supported
   - Ensure `uploads/` directory has write permissions

3. **Authentication Problems**
   - Verify default users exist in database
   - Check session timeout settings
   - Clear browser cache and cookies

4. **AWS Integration Issues**
   - Verify AWS credentials in `.env` file
   - Check AWS service permissions
   - Ensure S3 bucket exists and is accessible

### Logs

Application logs are stored in the `logs/` directory. Check these files for detailed error information.

## 📞 Support

For technical support or questions:
1. Check the troubleshooting section above
2. Review application logs in the `logs/` directory
3. Verify configuration in the `.env` file
4. Contact your system administrator

## 🔄 Updates and Maintenance

### Regular Maintenance
- Clean up old uploaded files periodically
- Backup the database regularly
- Update dependencies for security patches
- Monitor disk space usage

### Backup Procedures
```bash
# Backup database
cp data/audit_system.db data/audit_system_backup_$(date +%Y%m%d).db

# Backup uploaded files
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/
```

## 📄 License

This project is developed for California Polytechnic State University, San Luis Obispo. All rights reserved.

## 🤝 Contributing

This is an internal system for Cal Poly SLO. For feature requests or bug reports, please contact the development team.

---

**Cal Poly SLO Audit Management System** - Secure, Efficient, Compliant
