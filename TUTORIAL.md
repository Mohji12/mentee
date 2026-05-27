# Mentee Tracker MCA - Complete Tutorial Guide

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Project Flow](#project-flow)
4. [Prerequisites](#prerequisites)
5. [Installation & Setup](#installation--setup)
6. [Configuration](#configuration)
7. [Running the Application](#running-the-application)
8. [User Roles & Workflows](#user-roles--workflows)
9. [API Documentation](#api-documentation)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

The **Mentee Tracker MCA** is a comprehensive web-based mentorship management system designed for educational institutions. It facilitates student-mentor relationships and tracks academic progress through a modern three-tier architecture.

### Key Features:
- **Multi-role System**: Students, Mentors, and Administrators
- **Activity Tracking**: Complete mentorship activity lifecycle
- **Competency Assessment**: MCA (Mentorship Competency Assessment) system
- **AI Integration**: Google Gemini-powered observation generation
- **Meeting Management**: Scheduling and tracking mentor-student meetings
- **Report Generation**: Comprehensive analytics with radar charts
- **File Management**: AWS S3 integration for document storage

---

## 🏗️ System Architecture

### Three-Tier Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
│                     (React.js Frontend)                     │
├─────────────────────────────────────────────────────────────┤
│                   BUSINESS LOGIC LAYER                      │
│                    (FastAPI Backend)                        │
├─────────────────────────────────────────────────────────────┤
│                      DATA LAYER                             │
│              (MySQL Database + AWS S3)                      │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack:
- **Frontend**: React 19.0.0, React Router, Axios, Recharts
- **Backend**: FastAPI, SQLAlchemy, JWT Authentication
- **Database**: MySQL with Redis caching
- **Cloud**: AWS Lambda, S3, RDS
- **AI**: Google Gemini 2.0
- **Email**: ZeptoMail SMTP

---

## 🔄 Project Flow

### 1. User Authentication Flow
```
User Login → JWT Token Generation → Role-based Access → Dashboard Access
```

### 2. Mentorship Activity Workflow
```
Student Creates Goals → Mentor Reviews → Student Tracks Progress → 
Activity Submission → Final Approval → Completion
```

### 3. Competency Assessment Process
```
MCA Questionnaire → Score Calculation → AI Observation Generation → 
Report Creation → Mentor Review → Feedback
```

### 4. Meeting Management Flow
```
Meeting Request → Scheduling → Documentation → Follow-up → Progress Tracking
```

---

## 📋 Prerequisites

### System Requirements:
- **Node.js**: v16 or higher
- **Python**: v3.8 or higher
- **MySQL**: v8.0 or higher
- **Redis**: v6.0 or higher (optional but recommended)

### Development Tools:
- **Git**: For version control
- **Docker**: For containerization (optional)
- **VS Code**: Recommended IDE

### Cloud Services (Required for full functionality):
- **AWS Account**: For S3, Lambda, RDS
- **Google Cloud**: For Gemini AI API
- **Email Service**: ZeptoMail account

---

## 🚀 Installation & Setup

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd mentee_tracker_mca
```

### Step 2: Backend Setup

#### 2.1 Create Virtual Environment
```bash
# Windows
python -m venv mentee
mentee\Scripts\activate

# Linux/Mac
python3 -m venv mentee
source mentee/bin/activate
```

#### 2.2 Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Frontend Setup
```bash
cd frontend
npm install
```

### Step 4: Database Setup

#### 4.1 Create MySQL Database
```sql
CREATE DATABASE mentee_tracker;
CREATE USER 'mentee_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON mentee_tracker.* TO 'mentee_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 4.2 Run Database Migrations
```bash
cd app
python -c "from db.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

---

## ⚙️ Configuration

### Step 1: Environment Variables
Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL=mysql+pymysql://mentee_user:your_password@localhost/mentee_tracker

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=145

# AWS Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=ap-south-1
S3_BUCKET_NAME=your-s3-bucket-name

# Google AI Configuration
GOOGLE_API_KEY=your-google-gemini-api-key

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379

# Email Configuration
SMTP_HOST=smtp.zeptomail.com
SMTP_PORT=587
SMTP_USERNAME=your-zeptomail-username
SMTP_PASSWORD=your-zeptomail-password

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
CORS_ALLOW_CREDENTIALS=true
```

### Step 2: AWS S3 Bucket Setup
1. Create an S3 bucket in AWS Console
2. Configure bucket permissions for public read access
3. Update the bucket name in `.env` file

### Step 3: Google Gemini API Setup
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add the key to your `.env` file

---

## 🏃‍♂️ Running the Application

### Method 1: Development Mode (Recommended for Development)

#### Start Backend Server:
```bash
# Activate virtual environment
mentee\Scripts\activate  # Windows
# source mentee/bin/activate  # Linux/Mac

# Navigate to app directory
cd app

# Start FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Start Frontend Server:
```bash
# In a new terminal
cd frontend
npm start
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Method 2: Docker Deployment (Production)

#### Build and Run with Docker:
```bash
# Build the Docker image
docker build -t mentee-tracker .

# Run the container
docker run -p 8000:8000 mentee-tracker
```

### Method 3: AWS Lambda Deployment (Serverless)

The application is configured for AWS Lambda deployment using the provided Dockerfile:

```bash
# Build for Lambda
docker build -t mentee-tracker-lambda .

# Deploy to AWS Lambda (requires AWS CLI setup)
aws lambda create-function \
  --function-name mentee-tracker \
  --package-type Image \
  --code ImageUri=mentee-tracker-lambda:latest \
  --role arn:aws:iam::your-account:role/lambda-execution-role
```

---

## 👥 User Roles & Workflows

### 1. Student Workflow

#### Getting Started:
1. **Registration**: Sign up with student credentials
2. **Login**: Access student dashboard
3. **Profile Setup**: Complete personal information

#### Key Activities:
- **Activity Management**: Create and track mentorship activities
- **Meeting Requests**: Schedule meetings with assigned mentor
- **MCA Assessment**: Complete competency questionnaires
- **Progress Tracking**: View personal development reports
- **Query System**: Submit questions to mentors

#### Student Dashboard Features:
- Activity progress overview
- Upcoming meetings
- Recent submissions
- Competency scores
- AI-generated observations

### 2. Mentor Workflow

#### Getting Started:
1. **Admin Assignment**: Assigned students by administrator
2. **Login**: Access mentor dashboard
3. **Student Review**: Review assigned students

#### Key Activities:
- **Student Management**: Monitor assigned students
- **Activity Approval**: Review and approve student activities
- **Meeting Management**: Schedule and conduct meetings
- **Progress Monitoring**: Track student development
- **Report Generation**: Create comprehensive reports

#### Mentor Dashboard Features:
- Assigned students list
- Pending approvals
- Meeting calendar
- Student progress analytics
- Report generation tools

### 3. Administrator Workflow

#### Getting Started:
1. **System Access**: Full administrative privileges
2. **User Management**: Manage all users in the system
3. **System Configuration**: Configure activities and settings

#### Key Activities:
- **User Management**: Create and manage students/mentors
- **Activity Configuration**: Set up mentorship activities
- **System Analytics**: View system-wide statistics
- **Report Management**: Access all reports
- **System Maintenance**: Monitor system health

#### Admin Dashboard Features:
- User management interface
- System analytics
- Activity configuration
- Global reports
- System settings

---

## 📚 API Documentation

### Authentication Endpoints:
- `POST /auth/login` - User login
- `POST /auth/student-signup` - Student registration
- `POST /auth/forgot-password` - Password reset
- `GET /auth/user` - Get user information

### Student Endpoints:
- `GET /student/{usn}/profile` - Get student profile
- `POST /student/{usn}/activities` - Create activity
- `GET /student/{usn}/meetings` - Get meetings
- `POST /student/{usn}/mca` - Submit MCA assessment

### Mentor Endpoints:
- `GET /mentor/{id}/students` - Get assigned students
- `POST /mentor/{id}/activities/approve` - Approve activity
- `GET /mentor/{id}/meetings` - Get mentor meetings

### Admin Endpoints:
- `GET /admin/{id}/students` - Get all students
- `POST /admin/{id}/activities` - Create activity
- `GET /admin/{id}/analytics` - Get system analytics

### Interactive API Documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔧 Troubleshooting

### Common Issues:

#### 1. Database Connection Issues
```bash
# Check MySQL service
sudo systemctl status mysql  # Linux
brew services list | grep mysql  # Mac

# Test connection
mysql -u mentee_user -p mentee_tracker
```

#### 2. Python Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf mentee
python -m venv mentee
mentee\Scripts\activate
pip install -r requirements.txt
```

#### 3. Node.js Dependencies Issues
```bash
# Clear npm cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

#### 4. CORS Issues
- Ensure CORS_ORIGINS in `.env` includes your frontend URL
- Check that frontend is running on the correct port

#### 5. AWS S3 Issues
- Verify AWS credentials are correct
- Check S3 bucket permissions
- Ensure bucket exists and is accessible

#### 6. Google AI API Issues
- Verify API key is valid and active
- Check API quota and billing
- Ensure Gemini API is enabled

### Performance Optimization:

#### Frontend:
- Use React DevTools for performance profiling
- Implement lazy loading for large components
- Optimize bundle size with code splitting

#### Backend:
- Monitor database query performance
- Use Redis caching for frequently accessed data
- Implement connection pooling

#### Database:
- Add proper indexes for frequently queried columns
- Monitor slow query log
- Optimize database configuration

---

## 📞 Support & Resources

### Documentation:
- **API Docs**: http://localhost:8000/docs
- **Architecture Report**: `MENTEE_TRACKER_MCA_ARCHITECTURE_REPORT.txt`
- **Tech Stack Details**: `TECH_STACK_DETAILED_EXPLANATION.txt`

### Debug Information:
- **Frontend Debug**: `frontend/DEBUG_FIXES.md`
- **Test Files**: Various test files in root directory

### Getting Help:
1. Check the troubleshooting section above
2. Review the architecture documentation
3. Check API documentation at `/docs` endpoint
4. Create an issue in the repository

---

## 🎉 Success Checklist

After following this tutorial, you should have:

- ✅ Backend server running on port 8000
- ✅ Frontend application running on port 3000
- ✅ Database connected and tables created
- ✅ Environment variables configured
- ✅ AWS S3 integration working
- ✅ Google AI API connected
- ✅ Email service configured
- ✅ All three user roles accessible
- ✅ API documentation available

---

## 🚀 Next Steps

1. **Customize Configuration**: Adjust settings for your institution
2. **Add Users**: Create student and mentor accounts
3. **Configure Activities**: Set up mentorship activities
4. **Test Workflows**: Verify all user workflows function correctly
5. **Deploy to Production**: Use Docker or AWS Lambda for production deployment

---

*This tutorial provides a comprehensive guide to understanding and running the Mentee Tracker MCA application. For additional support or questions, refer to the troubleshooting section or create an issue in the repository.*
