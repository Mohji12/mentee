from mangum import Mangum
from fastapi import FastAPI
from app.db.database import Base, engine, get_db
from app.db.models import counseling, activities, query, mentors, admin, login, forgot_password, MCA_assignments, meetings, mentee_competency_report, psychometric_responses, report, swot, competencies, activities_tracking, activity_submissions  # Import all models to register them
from contextlib import asynccontextmanager
from app.routes.auth import forgot_password, login, student_signup, user
from app.routes.admin import profile as admin_profile, activities as admin_activities, students as admin_students
from app.routes.mentor import activities as mentor_activities, meetings as mentor_meetings, profile as mentor_profile, services as mentor_services, students as mentor_students, counseling as mentor_counseling
from app.routes.student import activities as student_activities, meetings as student_meetings, profile as student_profile, psychometric, query, swot, reportdownload, mca, counseling as student_counseling
from app.routes.student import competencies
from app.routes.student import generate_observation
from fastapi.middleware.cors import CORSMiddleware
from app.utils.student_services import update_student_semesters
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import os
import sys

# Add the parent directory to the Python path for Lambda
sys.path.append('/var/task')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Check if we're in Lambda environment
    is_lambda = os.getenv('AWS_LAMBDA_FUNCTION_NAME') is not None
    
    # Setup scheduler for background tasks (only if not in Lambda or explicitly enabled)
    scheduler = None
    if not is_lambda or os.getenv('SCHEDULER_ENABLED', 'false').lower() == 'true':
        try:
            scheduler = BackgroundScheduler()
            scheduler.add_job(
                func=lambda: update_student_semesters(next(get_db())), 
                trigger=IntervalTrigger(days=7000),  # 180 days ~ 6 months
                id='update_semesters',  # Unique ID for the job
                name='Update student semesters every 6 months', 
                replace_existing=True  # If the job exists, replace it
            )
            scheduler.start()
            print("Background scheduler started")
        except Exception as e:
            print(f"Failed to start scheduler: {e}")
    
    yield
    print("Application shutdown")
    
    # Shut down the scheduler when app shuts down
    if scheduler:
        try:
            scheduler.shutdown()
            print("Background scheduler stopped")
        except Exception as e:
            print(f"Error stopping scheduler: {e}")

# Attach the lifespan context manager
app = FastAPI(lifespan=lifespan)

# Create all tables
Base.metadata.create_all(bind=engine)

# Auth Routes
app.include_router(forgot_password.router, prefix="/auth", tags=["Auth - Forgot Password"])
app.include_router(login.router, prefix="/auth", tags=["Auth - Login"])
app.include_router(student_signup.router, prefix="/auth", tags=["Auth - Student Signup"])
app.include_router(user.router, prefix="/auth", tags=["Auth - User"])

# Admin Routes
app.include_router(admin_profile.router, prefix="/admin/{admin_id}", tags=["Admin - Profile"])
app.include_router(admin_activities.router, prefix="/admin/{admin_id}", tags=["Admin - Activities"])
app.include_router(admin_students.router, prefix="/admin/{admin_id}", tags=["Admin - Students"])

# Mentor Routes
app.include_router(mentor_profile.router, prefix="/mentor/{mentor_id}", tags=["Mentor - Profile"])
app.include_router(mentor_activities.router, prefix="/mentor/{mentor_id}", tags=["Mentor - Activities"])
app.include_router(mentor_meetings.router, prefix="/mentor/{mentor_id}", tags=["Mentor - Meetings"])
app.include_router(mentor_students.router, prefix="/mentor/{mentor_id}", tags=["Mentor - Students"])
app.include_router(mentor_services.router, tags=["Mentor - Services"])
app.include_router(mentor_counseling.router, prefix="/mentor/{mentor_id}", tags=["Mentor - Counseling"])

# Student Routes
app.include_router(student_profile.router, prefix="/student/{student_usn}", tags=["Student - Profile"])
app.include_router(student_activities.router, prefix="/student/{student_usn}", tags=["Student - Activities"])
app.include_router(student_meetings.router, prefix="/student/{student_usn}", tags=["Student - Meetings"])
app.include_router(psychometric.router, prefix="/student/{student_usn}", tags=["Student - Psychometric"])
app.include_router(query.router, tags=["Student - Query"])
app.include_router(swot.router, prefix="/student/{student_usn}", tags=["Student - Swot"])
app.include_router(reportdownload.router,prefix = "/student/{student_usn}", tags = ["Student - report download"])
app.include_router(mca.router, prefix="/student/{student_usn}", tags=["Student - MCA"])
app.include_router(competencies.router, prefix="/student/{student_usn}", tags=["Student - Competencies"])
app.include_router(generate_observation.router, tags=["Student - Generate Observation"])
app.include_router(student_counseling.router, prefix="/student/{student_usn}", tags=["Student - Counseling"])


# Define the CORS middleware with environment-based configuration
cors_origins = os.getenv('CORS_ORIGINS', '*').split(',')
cors_origins = cors_origins if cors_origins != ['*'] else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=os.getenv('CORS_ALLOW_CREDENTIALS', 'true').lower() == 'true',
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def read_root():
    return {"message": "Hello, Mentee Tracker with MCA. This is V2!"}

handler = Mangum(app)