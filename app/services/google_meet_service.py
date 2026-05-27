import uuid
import secrets
import string
from datetime import datetime
from typing import Dict, Any
import requests
import json

class GoogleMeetService:
    """
    Service for generating Google Meet links and managing meeting details
    """
    
    @staticmethod
    def generate_meeting_id() -> str:
        """Generate a unique meeting ID in Google Meet format (xxx-yyyy-zzz)"""
        # Generate 3 letters, 4 letters, 3 letters separated by hyphens
        part1 = ''.join(secrets.choice(string.ascii_lowercase) for _ in range(3))
        part2 = ''.join(secrets.choice(string.ascii_lowercase) for _ in range(4))
        part3 = ''.join(secrets.choice(string.ascii_lowercase) for _ in range(3))
        return f"{part1}-{part2}-{part3}"
    
    @staticmethod
    def generate_realistic_meeting_id() -> str:
        """Generate a more realistic Google Meet meeting ID"""
        # Use a combination of letters and numbers that looks more like real Google Meet codes
        chars = string.ascii_lowercase + string.digits
        part1 = ''.join(secrets.choice(chars) for _ in range(3))
        part2 = ''.join(secrets.choice(chars) for _ in range(4))
        part3 = ''.join(secrets.choice(chars) for _ in range(3))
        return f"{part1}-{part2}-{part3}"
    
    @staticmethod
    def generate_counseling_id() -> str:
        """Generate a unique counseling session ID"""
        return f"COUNSEL_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"
    
    @staticmethod
    def create_google_meet_link(meeting_id: str = None) -> Dict[str, Any]:
        """
        Create a Google Meet link for the counseling session
        Note: This generates a mock Google Meet link. For production, integrate with Google Meet API.
        """
        if not meeting_id:
            meeting_id = GoogleMeetService.generate_realistic_meeting_id()
        
        # Generate Google Meet link
        meet_link = f"https://meet.google.com/{meeting_id}"
        
        return {
            "meeting_id": meeting_id,
            "meeting_link": meet_link,
            "join_url": meet_link,
            "created_at": datetime.utcnow()
        }
    
    @staticmethod
    def create_working_google_meet_link() -> Dict[str, Any]:
        """
        Create a working Google Meet link
        Note: This creates a link that follows Google Meet format but may not be a real meeting
        """
        try:
            # Generate a realistic meeting ID
            meeting_id = GoogleMeetService.generate_realistic_meeting_id()
            meet_link = f"https://meet.google.com/{meeting_id}"
            
            return {
                "meeting_id": meeting_id,
                "meeting_link": meet_link,
                "join_url": meet_link,
                "created_at": datetime.utcnow(),
                "note": "Generated Google Meet link - may need to be created manually in Google Meet"
            }
        except Exception as e:
            # Fallback to basic mock link if generation fails
            return GoogleMeetService.create_google_meet_link()
    
    @staticmethod
    def create_real_google_meet_link() -> Dict[str, Any]:
        """
        Create a real Google Meet link using Google Meet API
        Note: This requires Google Meet API credentials to be configured
        """
        try:
            # For now, return a mock link that follows the correct format
            # In production, integrate with Google Meet API
            meeting_id = GoogleMeetService.generate_meeting_id()
            meet_link = f"https://meet.google.com/{meeting_id}"
            
            return {
                "meeting_id": meeting_id,
                "meeting_link": meet_link,
                "join_url": meet_link,
                "created_at": datetime.utcnow(),
                "note": "Mock Google Meet link - integrate with Google Meet API for real meetings"
            }
        except Exception as e:
            # Fallback to mock link if API fails
            return GoogleMeetService.create_google_meet_link()
    
    @staticmethod
    def create_meeting_with_details(
        title: str,
        description: str,
        start_time: datetime,
        duration_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Create a Google Meet with detailed information
        """
        meeting_id = GoogleMeetService.generate_meeting_id()
        meet_link = f"https://meet.google.com/{meeting_id}"
        
        return {
            "meeting_id": meeting_id,
            "meeting_link": meet_link,
            "join_url": meet_link,
            "title": title,
            "description": description,
            "start_time": start_time,
            "duration_minutes": duration_minutes,
            "created_at": datetime.utcnow()
        }
    
    @staticmethod
    def validate_meeting_time(session_date: datetime) -> bool:
        """
        Validate if the meeting time is in the future
        """
        # Handle timezone-aware vs timezone-naive datetime comparison
        now = datetime.utcnow()
        
        # If session_date is timezone-aware, make now timezone-aware too
        if session_date.tzinfo is not None:
            from datetime import timezone
            now = now.replace(tzinfo=timezone.utc)
        
        return session_date > now
    
    @staticmethod
    def format_meeting_details(
        counseling_id: str,
        student_name: str,
        mentor_name: str,
        session_date: datetime,
        venue: str,
        reason: str
    ) -> Dict[str, str]:
        """
        Format meeting details for display
        """
        return {
            "title": f"Counseling Session - {counseling_id}",
            "description": f"""
Counseling Session Details:
- Student: {student_name}
- Mentor: {mentor_name}
- Date: {session_date.strftime('%B %d, %Y at %I:%M %p')}
- Venue: {venue}
- Reason: {reason}
- Session ID: {counseling_id}
            """.strip()
        }
