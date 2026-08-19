import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import logging
import traceback
from typing import Optional

# Set up logging
logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, body: str):
    """
    Send email using SMTP
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body (HTML content)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # SMTP Configuration
    SMTP_SERVER = "smtp.zeptomail.in"
    SMTP_PORT = 587
    SMTP_USERNAME = "emailapikey"
    SMTP_PASSWORD = "Zoho-enczapikey PHtE6r1ZSuG52jQp9UIEt/LuFMWgPYwtrOJgKQBGt4lBCvMHHk1c+dguk2Li+B1+VfJGFqSewNg7tO/Ks+nQcWa+MGtLCWqyqK3sx/VYSPOZsbq6x00UsVQZdEDbUoPocNNi3CbQudzbNA=="
    SENDER_EMAIL = "noreply@bengaluruhealthcommunity.in"

    # Logo URL
    LOGO_URL = "https://res.cloudinary.com/dvlitilou/image/upload/v1779924617/logo_mentee-removebg-preview_coyhds.png"

    # Validate email address
    if not to_email or not isinstance(to_email, str) or '@' not in to_email:
        logger.error(f"Invalid email address: {to_email}")
        return False

    # HTML Email Template
    html_body = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; text-align: center; }}
        .container {{ max-width: 600px; padding: 20px; border-radius: 8px; 
                     box-shadow: 0 0 60px rgba(0,0,0,0.5); margin: 20px auto; text-align: left; }}
        .header-container {{ width: 100%; max-width: 600px; margin: 0 auto; display: flex; 
                            justify-content: space-between; align-items: center; padding: 0; }}
        img {{ max-width: 100%; height: 50px; }}
        .small-img {{ height: 40px; margin-left: auto; }} /* Push to extreme right */
    </style>
</head>
<body>
    <div style="padding: 40px 0;">
        <div class="header-container">
        <a href="https://jgi.menteetracker.com">
            <img src={LOGO_URL} width="125">
        </a>
        <img class="small-img" src="https://res.cloudinary.com/dvlitilou/image/upload/v1779924616/Jain-Logo_jix84i.png" width="125"> 
        </div>
        <div class="container">
        {body}
        </div>
        <div style="text-align: center; font-size: 12px; color: #777;">
            <p>&copy; 2025 <a href="https://jgi.menteetracker.com" style="color: #333;">Mentee Tracker</a>. All rights reserved.</p>
        </div>
    </div>
</body>
</html>"""

    try:
        logger.info(f"Attempting to send email to {to_email} with subject: {subject}")
        
        # Create message
        msg = MIMEMultipart()
        msg["From"] = formataddr(("JGIMENTEETRACKER", SENDER_EMAIL))
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))

        # Connect to SMTP server with timeout
        logger.info(f"Connecting to SMTP server: {SMTP_SERVER}:{SMTP_PORT}")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        
        try:
            # Start TLS
            logger.info("Starting TLS connection...")
            server.starttls()
            
            # Login
            logger.info("Authenticating with SMTP server...")
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            
            # Send email
            logger.info(f"Sending email to {to_email}...")
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
            
            logger.info(f"Email successfully sent to {to_email}")
            print(f"Email successfully sent to {to_email}")
            return True
            
        finally:
            # Always close the connection
            try:
                server.quit()
                logger.info("SMTP connection closed")
            except:
                pass

    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"SMTP Authentication Error: {str(e)}"
        logger.error(error_msg)
        print(f"Failed to send email: {error_msg}")
        return False
    except smtplib.SMTPConnectError as e:
        error_msg = f"SMTP Connection Error: {str(e)}"
        logger.error(error_msg)
        print(f"Failed to send email: {error_msg}")
        return False
    except smtplib.SMTPSenderRefused as e:
        error_msg = f"Sender address refused: {str(e)}"
        logger.error(error_msg)
        print(f"Failed to send email: {error_msg}")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        error_msg = f"Recipient address refused: {str(e)}"
        logger.error(error_msg)
        print(f"Failed to send email: {error_msg}")
        return False
    except smtplib.SMTPDataError as e:
        error_msg = f"SMTP Data Error: {str(e)}"
        logger.error(error_msg)
        print(f"Failed to send email: {error_msg}")
        return False
    except smtplib.SMTPException as e:
        error_msg = f"SMTP Exception: {str(e)}"
        logger.error(error_msg)
        print(f"Failed to send email: {error_msg}")
        return False
    except Exception as e:
        error_msg = f"Unexpected error sending email: {str(e)}"
        error_trace = traceback.format_exc()
        logger.error(f"{error_msg}\n{error_trace}")
        print(f"Failed to send email: {error_msg}")
        return False


def send_mentor_changed_notification(
    to_email: str,
    student_name: str,
    new_mentor_name: Optional[str] = None,
    new_mentor_email: Optional[str] = None,
    new_mentor_phoneno: Optional[str] = None,
) -> bool:
    """
    Notify a mentee that their mentor was assigned, changed, or removed.
    Uses the standard send_email wrapper (logo, container). Returns send_email result.
    """
    subject = "Your mentor has been updated – Mentee Tracker"
    if new_mentor_name:
        body = f"""
        <h2 style="color: #2c3e50; margin-bottom: 20px;">Mentor Update</h2>
        <p>Dear {student_name},</p>
        <p>Your mentor has been changed to <strong>{new_mentor_name}</strong>.</p>
        """
        if new_mentor_email or new_mentor_phoneno:
            body += """
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0;">
                <h3 style="color: #2c3e50; margin-top: 0;">Mentor contact</h3>
            """
            if new_mentor_email:
                body += f"<p><strong>Email:</strong> {new_mentor_email}</p>"
            if new_mentor_phoneno:
                body += f"<p><strong>Phone:</strong> {new_mentor_phoneno}</p>"
            body += "</div>"
        body += "<p>Best regards,<br><strong>Mentee Tracker Team</strong></p>"
    else:
        body = f"""
        <h2 style="color: #2c3e50; margin-bottom: 20px;">Mentor Update</h2>
        <p>Dear {student_name},</p>
        <p>Your mentor has been removed. A new mentor may be assigned to you later.</p>
        <p>Best regards,<br><strong>Mentee Tracker Team</strong></p>
        """
    return send_email(to_email, subject, body)
