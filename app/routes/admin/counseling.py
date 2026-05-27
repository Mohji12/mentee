from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from app.db.database import get_db
from app.db.models.counseling import CounselingSession, CounselingEscalation
from app.db.models.students import Student
from app.db.models.mentors import Mentor
from app.core.dependencies import get_current_admin
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict
from pydantic import BaseModel, Field

router = APIRouter()


class EscalationCreate(BaseModel):
    session_id: str = Field(..., description="Counseling session ID to escalate")
    escalated_to: str = Field(..., description="Person or role to escalate to")
    reason: Optional[str] = Field(None, description="Reason for escalation")
    priority: str = Field(default="normal", description="Priority: low, normal, high, critical")

class EscalationUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Status: open, acknowledged, resolved")
    resolution_notes: Optional[str] = Field(None, description="Resolution notes")


@router.get("/counseling/overview")
async def get_counseling_overview(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get overall counseling statistics across all mentors."""
    total_sessions = db.query(CounselingSession).count()
    scheduled_sessions = db.query(CounselingSession).filter(CounselingSession.status == "scheduled").count()
    completed_sessions = db.query(CounselingSession).filter(CounselingSession.status == "completed").count()
    cancelled_sessions = db.query(CounselingSession).filter(CounselingSession.status == "cancelled").count()
    referred_sessions = db.query(CounselingSession).filter(CounselingSession.status == "referred").count()
    urgent_sessions = db.query(CounselingSession).filter(
        and_(
            CounselingSession.is_urgent == True,
            CounselingSession.status == "scheduled"
        )
    ).count()
    
    needs_followup = db.query(CounselingSession).filter(
        and_(
            CounselingSession.outcome_status == "needs_followup",
            CounselingSession.followup_scheduled == False
        )
    ).count()
    
    today = datetime.utcnow().date()
    overdue_followups = db.query(CounselingSession).filter(
        and_(
            CounselingSession.outcome_status == "needs_followup",
            CounselingSession.followup_scheduled == False,
            CounselingSession.followup_date < today
        )
    ).count()
    
    open_escalations = db.query(CounselingEscalation).filter(
        CounselingEscalation.status == "open"
    ).count()
    
    total_mentors = db.query(func.count(func.distinct(CounselingSession.mentor_id))).scalar()
    total_students = db.query(func.count(func.distinct(CounselingSession.student_usn))).scalar()

    return {
        "total_sessions": total_sessions,
        "scheduled_sessions": scheduled_sessions,
        "completed_sessions": completed_sessions,
        "cancelled_sessions": cancelled_sessions,
        "referred_sessions": referred_sessions,
        "urgent_pending": urgent_sessions,
        "needs_followup": needs_followup,
        "overdue_followups": overdue_followups,
        "open_escalations": open_escalations,
        "active_mentors": total_mentors,
        "students_with_sessions": total_students,
        "completion_rate": round((completed_sessions / total_sessions * 100), 1) if total_sessions > 0 else 0
    }


@router.get("/counseling/sessions")
async def get_all_sessions(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None, description="Filter by status"),
    mentor_id: Optional[str] = Query(None, description="Filter by mentor"),
    is_urgent: Optional[bool] = Query(None, description="Filter by urgency"),
    outcome_status: Optional[str] = Query(None, description="Filter by outcome status"),
    limit: int = Query(50, description="Number of sessions to return"),
    offset: int = Query(0, description="Number of sessions to skip")
):
    """Get all counseling sessions with optional filters."""
    query = db.query(CounselingSession)
    
    if status:
        query = query.filter(CounselingSession.status == status)
    if mentor_id:
        query = query.filter(CounselingSession.mentor_id == mentor_id)
    if is_urgent is not None:
        query = query.filter(CounselingSession.is_urgent == is_urgent)
    if outcome_status:
        query = query.filter(CounselingSession.outcome_status == outcome_status)
    
    total = query.count()
    sessions = query.order_by(desc(CounselingSession.created_at)).offset(offset).limit(limit).all()
    
    result = []
    for session in sessions:
        student = db.query(Student).filter(Student.student_usn == session.student_usn).first()
        mentor = db.query(Mentor).filter(Mentor.mentor_id == session.mentor_id).first()
        
        result.append({
            "id": session.id,
            "counseling_id": session.counseling_id,
            "student_usn": session.student_usn,
            "student_name": student.student_name if student else None,
            "mentor_id": session.mentor_id,
            "mentor_name": mentor.mentor_name if mentor else None,
            "session_date": session.session_date,
            "venue": session.venue,
            "reason": session.reason,
            "status": session.status,
            "is_urgent": session.is_urgent,
            "outcome_status": session.outcome_status,
            "outcome_notes": session.outcome_notes,
            "followup_date": session.followup_date,
            "followup_scheduled": session.followup_scheduled,
            "parent_session_id": session.parent_session_id,
            "created_at": session.created_at
        })
    
    return {
        "total": total,
        "sessions": result,
        "limit": limit,
        "offset": offset
    }


@router.get("/counseling/mentor-stats")
async def get_mentor_stats(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get per-mentor counseling statistics."""
    mentors = db.query(Mentor).all()
    
    stats = []
    for mentor in mentors:
        total = db.query(CounselingSession).filter(CounselingSession.mentor_id == mentor.mentor_id).count()
        if total == 0:
            continue
            
        completed = db.query(CounselingSession).filter(
            and_(
                CounselingSession.mentor_id == mentor.mentor_id,
                CounselingSession.status == "completed"
            )
        ).count()
        
        scheduled = db.query(CounselingSession).filter(
            and_(
                CounselingSession.mentor_id == mentor.mentor_id,
                CounselingSession.status == "scheduled"
            )
        ).count()
        
        urgent = db.query(CounselingSession).filter(
            and_(
                CounselingSession.mentor_id == mentor.mentor_id,
                CounselingSession.is_urgent == True,
                CounselingSession.status == "scheduled"
            )
        ).count()
        
        pending_followups = db.query(CounselingSession).filter(
            and_(
                CounselingSession.mentor_id == mentor.mentor_id,
                CounselingSession.outcome_status == "needs_followup",
                CounselingSession.followup_scheduled == False
            )
        ).count()
        
        unique_students = db.query(func.count(func.distinct(CounselingSession.student_usn))).filter(
            CounselingSession.mentor_id == mentor.mentor_id
        ).scalar()
        
        stats.append({
            "mentor_id": mentor.mentor_id,
            "mentor_name": mentor.mentor_name,
            "mentor_email": mentor.mentor_email,
            "department": mentor.mentor_department,
            "total_sessions": total,
            "completed_sessions": completed,
            "scheduled_sessions": scheduled,
            "urgent_pending": urgent,
            "pending_followups": pending_followups,
            "unique_students": unique_students,
            "completion_rate": round((completed / total * 100), 1) if total > 0 else 0
        })
    
    stats.sort(key=lambda x: x["total_sessions"], reverse=True)
    return stats


@router.get("/counseling/urgent-pending")
async def get_urgent_pending(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get sessions needing immediate attention (urgent or overdue)."""
    today = datetime.utcnow().date()
    
    urgent_sessions = db.query(CounselingSession).filter(
        and_(
            CounselingSession.is_urgent == True,
            CounselingSession.status == "scheduled"
        )
    ).all()
    
    overdue_followups = db.query(CounselingSession).filter(
        and_(
            CounselingSession.outcome_status == "needs_followup",
            CounselingSession.followup_scheduled == False,
            CounselingSession.followup_date < today
        )
    ).all()
    
    open_escalations = db.query(CounselingEscalation).filter(
        CounselingEscalation.status == "open"
    ).all()
    
    result = {
        "urgent_sessions": [],
        "overdue_followups": [],
        "open_escalations": []
    }
    
    for session in urgent_sessions:
        student = db.query(Student).filter(Student.student_usn == session.student_usn).first()
        mentor = db.query(Mentor).filter(Mentor.mentor_id == session.mentor_id).first()
        result["urgent_sessions"].append({
            "counseling_id": session.counseling_id,
            "student_name": student.student_name if student else None,
            "student_usn": session.student_usn,
            "mentor_name": mentor.mentor_name if mentor else None,
            "session_date": session.session_date,
            "reason": session.reason,
            "created_at": session.created_at
        })
    
    for session in overdue_followups:
        student = db.query(Student).filter(Student.student_usn == session.student_usn).first()
        mentor = db.query(Mentor).filter(Mentor.mentor_id == session.mentor_id).first()
        days_overdue = (today - session.followup_date).days
        result["overdue_followups"].append({
            "counseling_id": session.counseling_id,
            "student_name": student.student_name if student else None,
            "student_usn": session.student_usn,
            "mentor_name": mentor.mentor_name if mentor else None,
            "followup_date": session.followup_date,
            "days_overdue": days_overdue,
            "outcome_notes": session.outcome_notes
        })
    
    for escalation in open_escalations:
        session = db.query(CounselingSession).filter(
            CounselingSession.counseling_id == escalation.session_id
        ).first()
        result["open_escalations"].append({
            "id": escalation.id,
            "session_id": escalation.session_id,
            "escalated_by": escalation.escalated_by,
            "escalated_to": escalation.escalated_to,
            "reason": escalation.reason,
            "priority": escalation.priority,
            "created_at": escalation.created_at,
            "session_date": session.session_date if session else None
        })
    
    return result


@router.post("/counseling/escalations")
async def create_escalation(
    escalation_data: EscalationCreate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new escalation for a counseling session."""
    session = db.query(CounselingSession).filter(
        CounselingSession.counseling_id == escalation_data.session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Counseling session not found")
    
    admin_name = current_admin.get("admin_name", current_admin.get("email", "Admin"))
    
    escalation = CounselingEscalation(
        session_id=escalation_data.session_id,
        escalated_by=admin_name,
        escalated_to=escalation_data.escalated_to,
        reason=escalation_data.reason,
        priority=escalation_data.priority,
        status="open",
        created_at=datetime.utcnow()
    )
    
    db.add(escalation)
    db.commit()
    db.refresh(escalation)
    
    return {
        "success": True,
        "message": "Escalation created successfully",
        "escalation_id": escalation.id
    }


@router.get("/counseling/escalations")
async def get_escalations(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None, description="Filter by status")
):
    """Get all escalations with optional status filter."""
    query = db.query(CounselingEscalation)
    
    if status:
        query = query.filter(CounselingEscalation.status == status)
    
    escalations = query.order_by(desc(CounselingEscalation.created_at)).all()
    
    result = []
    for escalation in escalations:
        session = db.query(CounselingSession).filter(
            CounselingSession.counseling_id == escalation.session_id
        ).first()
        
        student = mentor = None
        if session:
            student = db.query(Student).filter(Student.student_usn == session.student_usn).first()
            mentor = db.query(Mentor).filter(Mentor.mentor_id == session.mentor_id).first()
        
        result.append({
            "id": escalation.id,
            "session_id": escalation.session_id,
            "escalated_by": escalation.escalated_by,
            "escalated_to": escalation.escalated_to,
            "reason": escalation.reason,
            "status": escalation.status,
            "priority": escalation.priority,
            "created_at": escalation.created_at,
            "acknowledged_at": escalation.acknowledged_at,
            "resolved_at": escalation.resolved_at,
            "resolution_notes": escalation.resolution_notes,
            "student_name": student.student_name if student else None,
            "mentor_name": mentor.mentor_name if mentor else None,
            "session_date": session.session_date if session else None
        })
    
    return result


@router.put("/counseling/escalations/{escalation_id}")
async def update_escalation(
    escalation_id: int,
    update_data: EscalationUpdate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update an escalation status."""
    escalation = db.query(CounselingEscalation).filter(
        CounselingEscalation.id == escalation_id
    ).first()
    
    if not escalation:
        raise HTTPException(status_code=404, detail="Escalation not found")
    
    if update_data.status:
        if update_data.status not in ["open", "acknowledged", "resolved"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        escalation.status = update_data.status
        
        if update_data.status == "acknowledged" and not escalation.acknowledged_at:
            escalation.acknowledged_at = datetime.utcnow()
        elif update_data.status == "resolved":
            escalation.resolved_at = datetime.utcnow()
    
    if update_data.resolution_notes:
        escalation.resolution_notes = update_data.resolution_notes
    
    db.commit()
    db.refresh(escalation)
    
    return {
        "success": True,
        "message": "Escalation updated successfully",
        "escalation": {
            "id": escalation.id,
            "status": escalation.status,
            "acknowledged_at": escalation.acknowledged_at,
            "resolved_at": escalation.resolved_at
        }
    }


@router.get("/counseling/analytics")
async def get_admin_analytics(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
    months: int = Query(6, description="Number of months to analyze")
):
    """Get comprehensive counseling analytics for admin oversight."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=months * 30)
    
    all_sessions = db.query(CounselingSession).filter(
        CounselingSession.created_at >= start_date
    ).all()
    
    total = len(all_sessions)
    completed = len([s for s in all_sessions if s.status == 'completed'])
    scheduled = len([s for s in all_sessions if s.status == 'scheduled'])
    cancelled = len([s for s in all_sessions if s.status == 'cancelled'])
    referred = len([s for s in all_sessions if s.status == 'referred'])
    
    sessions_by_month = defaultdict(int)
    for session in all_sessions:
        month_key = session.created_at.strftime('%Y-%m')
        sessions_by_month[month_key] += 1
    
    sorted_months = sorted(sessions_by_month.keys())
    sessions_trend = [{"month": m, "count": sessions_by_month[m]} for m in sorted_months]
    
    status_by_month = defaultdict(lambda: defaultdict(int))
    for session in all_sessions:
        month_key = session.created_at.strftime('%Y-%m')
        status_by_month[month_key][session.status] += 1
    
    status_trend = []
    for month in sorted_months:
        status_trend.append({
            "month": month,
            "completed": status_by_month[month].get('completed', 0),
            "scheduled": status_by_month[month].get('scheduled', 0),
            "cancelled": status_by_month[month].get('cancelled', 0),
            "referred": status_by_month[month].get('referred', 0)
        })
    
    outcome_counts = defaultdict(int)
    for session in all_sessions:
        if session.outcome_status:
            outcome_counts[session.outcome_status] += 1
    
    outcome_distribution = [
        {"status": "Fully Resolved", "value": outcome_counts.get('fully_resolved', 0)},
        {"status": "Partially Resolved", "value": outcome_counts.get('partially_resolved', 0)},
        {"status": "Unresolved", "value": outcome_counts.get('unresolved', 0)},
        {"status": "Needs Follow-up", "value": outcome_counts.get('needs_followup', 0)}
    ]
    
    mentor_sessions = defaultdict(lambda: {"total": 0, "completed": 0, "name": ""})
    for session in all_sessions:
        mentor_sessions[session.mentor_id]["total"] += 1
        if session.status == 'completed':
            mentor_sessions[session.mentor_id]["completed"] += 1
    
    for mentor_id in mentor_sessions:
        mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
        if mentor:
            mentor_sessions[mentor_id]["name"] = mentor.mentor_name
    
    mentor_performance = []
    for mentor_id, data in mentor_sessions.items():
        if data["total"] > 0:
            mentor_performance.append({
                "mentor_id": mentor_id,
                "mentor_name": data["name"] or mentor_id,
                "total": data["total"],
                "completed": data["completed"],
                "completion_rate": round(data["completed"] / data["total"] * 100, 1)
            })
    
    mentor_performance.sort(key=lambda x: x["total"], reverse=True)
    
    unique_students = len(set(s.student_usn for s in all_sessions))
    urgent_count = len([s for s in all_sessions if s.is_urgent])
    followup_sessions = [s for s in all_sessions if s.parent_session_id]
    
    student_session_counts = defaultdict(int)
    for session in all_sessions:
        student_session_counts[session.student_usn] += 1
    
    repeat_students = len([usn for usn, count in student_session_counts.items() if count > 1])
    
    ratings = [s.mentor_rating for s in all_sessions if s.mentor_rating]
    avg_mentor_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0
    
    student_ratings = [s.student_rating for s in all_sessions if s.student_rating]
    avg_student_rating = round(sum(student_ratings) / len(student_ratings), 1) if student_ratings else 0
    
    return {
        "summary": {
            "total_sessions": total,
            "completed": completed,
            "scheduled": scheduled,
            "cancelled": cancelled,
            "referred": referred,
            "completion_rate": round(completed / total * 100, 1) if total > 0 else 0,
            "urgent_sessions": urgent_count,
            "followup_sessions": len(followup_sessions),
            "unique_students": unique_students,
            "repeat_students": repeat_students,
            "active_mentors": len(mentor_sessions)
        },
        "trends": {
            "sessions_by_month": sessions_trend,
            "status_by_month": status_trend
        },
        "outcomes": {
            "distribution": outcome_distribution
        },
        "mentor_performance": mentor_performance[:10],
        "ratings": {
            "avg_mentor_rating": avg_mentor_rating,
            "avg_student_rating": avg_student_rating,
            "total_rated_sessions": len(ratings)
        },
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "months_analyzed": months
        }
    }
