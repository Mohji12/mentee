# Mentee Tracker MCA

A comprehensive mentorship tracking system built with React frontend and FastAPI backend, designed to facilitate student-mentor relationships and track academic progress.

## 🚀 Features

### For Students
- **Profile Management**: Create and manage student profiles
- **Activity Tracking**: Log and submit academic activities
- **Meeting Scheduling**: Request and manage meetings with mentors
- **Progress Reports**: View detailed progress analytics
- **Forms**: Complete psychometric and MCA assessment forms
- **Chatbot Support**: AI-powered assistance for queries

### For Mentors
- **Student Management**: View assigned students and their progress
- **Activity Approval**: Review and approve student submissions
- **Meeting Management**: Schedule and conduct meetings
- **Progress Monitoring**: Track student development over time
- **Reporting**: Generate comprehensive reports

### For Administrators
- **User Management**: Oversee all students and mentors
- **System Analytics**: View system-wide statistics
- **Activity Management**: Manage and configure activities
- **Reporting**: Access comprehensive administrative reports

## 🛠️ Tech Stack

### Frontend
- **React 19.0.0** - Modern React with hooks
- **React Router DOM 7.1.1** - Client-side routing
- **React Icons 5.4.0** - Icon library
- **Axios 1.7.9** - HTTP client
- **React Select 5.10.0** - Enhanced select components
- **Recharts 2.15.1** - Data visualization
- **React Modal 3.16.3** - Modal dialogs

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **Pydantic** - Data validation
- **JWT** - Authentication
- **MySQL** - Database
- **Redis** - Caching
- **AWS S3** - File storage
- **Google AI** - AI services

## 📦 Installation

### Prerequisites
- Node.js (v16 or higher)
- Python (v3.8 or higher)
- MySQL database
- Redis server

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Backend Setup
```bash
# Activate virtual environment
cd mentee
source Scripts/activate  # On Windows: mentee\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
cd app
uvicorn main:app --reload
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=mysql+pymysql://username:password@localhost/mentee_tracker

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS S3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=ap-south-1
S3_BUCKET_NAME=your-bucket-name

# Google AI
GOOGLE_API_KEY=your-google-api-key

# Redis
REDIS_URL=redis://localhost:6379
```

## 🚀 Deployment

### Frontend Deployment
```bash
cd frontend
npm run build
```

### Backend Deployment
```bash
# Using Docker
docker build -t mentee-tracker .
docker run -p 8000:8000 mentee-tracker
```

## 📁 Project Structure

```
mentee_tracker_mca/
├── app/                    # Backend FastAPI application
│   ├── core/              # Core configurations
│   ├── db/                # Database models and connections
│   ├── routes/            # API endpoints
│   ├── schemas/           # Pydantic models
│   ├── services/          # Business logic
│   └── utils/             # Utility functions
├── frontend/              # React frontend application
│   ├── public/            # Static files
│   ├── src/               # Source code
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── utils/         # Utility functions
│   │   └── assets/        # Images and styles
│   └── package.json       # Dependencies
├── mentee/                # Python virtual environment
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

## 🔐 Authentication

The application uses JWT-based authentication with role-based access control:

- **Students**: Access to personal dashboard and activities
- **Mentors**: Access to assigned students and management tools
- **Administrators**: Full system access and management

## 📊 API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🐛 Recent Fixes

This project includes comprehensive fixes for React performance issues:

- **Maximum Update Depth Exceeded**: Fixed infinite re-render issues
- **Navigation Throttling**: Optimized navigation performance
- **Component Optimization**: Added memoization and proper dependency management
- **Error Handling**: Implemented error boundaries and debugging utilities

See `frontend/DEBUG_FIXES.md` for detailed information about the fixes applied.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Contact the development team
- Check the documentation in `/docs` folder

## 🙏 Acknowledgments

- Built with ❤️ for educational institutions
- Powered by modern web technologies
- Designed for optimal user experience 