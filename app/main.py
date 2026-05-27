from mangum import Mangum
from fastapi import FastAPI
from app.db.database import Base, engine, get_db
from app.db.models import counseling, activities, query, mentors, admin, login, forgot_password, MCA_assignments, meetings, mentee_competency_report, psychometric_responses, report, swot, competencies, activities_tracking, activity_submissions, attendance, committee_member, academic_performance, pf16_responses, ibp_responses, experience_learning, email_logs, internal_marks  # Import all models to register them
from contextlib import asynccontextmanager
from app.routes.auth import forgot_password, login, student_signup, user
from app.routes.admin import profile as admin_profile, activities as admin_activities, students as admin_students, pf16 as admin_pf16, ibp as admin_ibp, counseling as admin_counseling
from app.routes.mentor import activities as mentor_activities, meetings as mentor_meetings, profile as mentor_profile, services as mentor_services, students as mentor_students, counseling as mentor_counseling, attendance as mentor_attendance, pf16 as mentor_pf16, ibp as mentor_ibp, experience_learning as mentor_experience_learning, dashboard as mentor_dashboard
from app.routes.mentor.internal_marks import router as mentor_internal_marks_router
from app.routes.student import activities as student_activities, meetings as student_meetings, profile as student_profile, psychometric, query, swot, reportdownload, mca, counseling as student_counseling, attendance as student_attendance, academic_performance as student_academic_performance, pf16 as student_pf16, ibp as student_ibp, experience_learning, dashboard as student_dashboard
from app.routes.student import competencies
from app.routes.student import generate_observation
from app.routes.leader import dashboard as leader_dashboard
from app.routes.working_committee import dashboard as working_committee_dashboard
from app.routes.department_faculty import dashboard as department_faculty_dashboard
from app.routes.hod import dashboard as hod_dashboard
from app.routes.program_faculty import dashboard as program_faculty_dashboard
from fastapi.middleware.cors import CORSMiddleware
from app.utils.student_services import update_student_semesters
from app.utils.reminder_service import run_reminder_job, run_counseling_reminder_job
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
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
            scheduler.add_job(
                func=run_reminder_job,
                trigger=CronTrigger(hour=9, minute=0),  # Daily at 9:00 AM
                id='reminder_job',
                name='Daily mentee reminder emails',
                replace_existing=True
            )
            scheduler.add_job(
                func=run_counseling_reminder_job,
                trigger=CronTrigger(hour=8, minute=0),  # Daily at 8:00 AM
                id='counseling_reminder_job',
                name='Daily counseling session reminders',
                replace_existing=True
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
app.include_router(admin_pf16.router, prefix="/admin/{admin_id}", tags=["Admin - 16PF"])
app.include_router(admin_ibp.router, prefix="/admin/{admin_id}", tags=["Admin - IBP"])
app.include_router(admin_counseling.router, prefix="/admin/{admin_id}", tags=["Admin - Counseling Oversight"])

# Mentor Routes
app.include_router(mentor_profile.router, prefix="/mentor/{mentor_id}", tags=["Mentor - Profile"])
app.include_router(mentor_activities.router, prefix="/mentor/{mentor_id}", tags=["Mentor - Activities"])
app.include_router(mentor_meetings.router, prefix="/mentor/{mentor_id}", tags=["Mentor - Meetings"])
app.include_router(mentor_students.router, prefix="/mentor/{mentor_id}", tags=["Mentor - Students"])
app.include_router(mentor_pf16.router, prefix="/mentor/{mentor_id}", tags=["Mentor - 16PF"])
app.include_router(mentor_ibp.router, prefix="/mentor/{mentor_id}", tags=["Mentor - IBP"])
app.include_router(mentor_services.router, tags=["Mentor - Services"])
app.include_router(mentor_counseling.router, prefix="/mentor/{mentor_id}", tags=["Mentor - Counseling"])
app.include_router(mentor_attendance.router, prefix="/mentor/{mentor_id}", tags=["Mentor - Attendance"])
app.include_router(mentor_experience_learning.router, prefix="/mentor/{mentor_id}", tags=["Mentor - Experience Learning"])
app.include_router(mentor_dashboard.router, prefix="/mentor/{mentor_id}", tags=["Mentor - Dashboard"])
app.include_router(mentor_internal_marks_router, prefix="/mentor/{mentor_id}", tags=["Mentor - Internal Marks"])

# Student Routes
app.include_router(student_profile.router, prefix="/student/{student_usn}", tags=["Student - Profile"])
app.include_router(student_activities.router, prefix="/student/{student_usn}", tags=["Student - Activities"])
app.include_router(student_meetings.router, prefix="/student/{student_usn}", tags=["Student - Meetings"])
app.include_router(student_dashboard.router, prefix="/student/{student_usn}", tags=["Student - Dashboard"])
app.include_router(psychometric.router, prefix="/student/{student_usn}", tags=["Student - Psychometric"])
app.include_router(query.router, tags=["Student - Query"])
app.include_router(swot.router, prefix="/student/{student_usn}", tags=["Student - Swot"])
app.include_router(reportdownload.router,prefix = "/student/{student_usn}", tags = ["Student - report download"])
app.include_router(mca.router, prefix="/student/{student_usn}", tags=["Student - MCA"])
app.include_router(competencies.router, prefix="/student/{student_usn}", tags=["Student - Competencies"])
app.include_router(generate_observation.router, tags=["Student - Generate Observation"])
app.include_router(student_counseling.router, prefix="/student/{student_usn}", tags=["Student - Counseling"])
app.include_router(student_attendance.router, prefix="/student/{student_usn}", tags=["Student - Attendance"])
app.include_router(student_academic_performance.router, prefix="/student/{student_usn}", tags=["Student - Academic Performance"])
app.include_router(student_pf16.router, prefix="/student/{student_usn}", tags=["Student - 16PF Form"])
app.include_router(student_ibp.router, prefix="/student/{student_usn}", tags=["Student - IBP Form"])
app.include_router(experience_learning.router, prefix="/student/{student_usn}", tags=["Student - Experience Learning"])

# Committee dashboards (leader, working committee, department faculty, program faculty)
app.include_router(leader_dashboard.router, prefix="/leader/{leader_id}", tags=["Leader"])
app.include_router(working_committee_dashboard.router, prefix="/working-committee/{member_id}", tags=["Working Committee"])
app.include_router(department_faculty_dashboard.router, prefix="/department-faculty/{member_id}", tags=["Department Faculty"])
app.include_router(hod_dashboard.router, prefix="/hod/{member_id}", tags=["HOD"])
app.include_router(program_faculty_dashboard.router, prefix="/program-faculty/{member_id}", tags=["Program Faculty"])

# Define the CORS middleware with explicit origins for production
# When allow_credentials=True, cannot use wildcard "*" - must list explicit origins
default_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://www.menteetracker.com",
    "https://menteetracker.com",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
cors_origins = os.getenv('CORS_ORIGINS', '').split(',') if os.getenv('CORS_ORIGINS') else default_origins
cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Hello, Mentee Tracker with MCA. This is V2!"}


@app.get("/health")
async def health_check():
    """Health check for load balancers and monitoring. Returns 200 if API is up."""
    return {"status": "ok", "service": "mentee-tracker-api"}


handler = Mangum(app)