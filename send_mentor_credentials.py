"""
Script to send mentor login credentials via email from Excel file.

Usage:
    python send_mentor_credentials.py [excel_file_path]

If no file path is provided, it will use the default file:
    E:\All\mentee_tracker_mca\MENTORSHIP 17-10-2025.xlsx

Example:
    python send_mentor_credentials.py
    python send_mentor_credentials.py mentors.xlsx

Excel file should contain columns:
    - MENTORID (or Employee ID)
    - MENTORNAME (or Name of the Faculty)
    - MENTOREMAIL (or University Mail ID)
    - MENTORPASSWORD (optional - will be auto-generated if missing)
"""

import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import sys
import os
from typing import Dict, List
import time

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ============================================================================
# SMTP CONFIGURATION
# ============================================================================
SMTP_SERVER = "smtp.zeptomail.in"
SMTP_PORT = 587
SMTP_USERNAME = "emailapikey"
SMTP_PASSWORD = "Zoho-enczapikey PHtE6r0NQr/tgjUv+0RS5qC6QpalMo4uqe1jeFVCsI5FWPYCGk1Sqd4ukmfhr00jXPURHKHKwN9v4OmZserXdDy5YWxOD2qyqK3sx/VYSPOZsbq6x00Zsl4afkLeUYHvcdZo1ifSvdvdNA=="
SENDER_EMAIL = "jgi@menteetracker.com"  # Sender email address
SENDER_NAME = "JGI Mentee Tracker"  # Display name for sender

# Logo URLs
LOGO_URL = "https://jgi-menteetrackers.s3.ap-south-1.amazonaws.com/black.png"
JAIN_LOGO_URL = "https://jgi-menteetrackers.s3.ap-south-1.amazonaws.com/Jain-Logo.png"

# ============================================================================
# EMAIL TEMPLATE
# ============================================================================

def create_email_body(mentor_name: str, mentor_id: str, password: str) -> str:
    """
    Create HTML email body with login credentials.
    
    Args:
        mentor_name: Name of the mentor
        mentor_id: Mentor ID for login
        password: Password for login
    
    Returns:
        HTML formatted email body
    """
    body = f"""
    <div style="padding: 20px;">
        <h2 style="color: #333; margin-bottom: 20px;">Welcome to Mentee Tracker!</h2>
        
        <p style="color: #555; line-height: 1.6; font-size: 16px;">
            Dear <strong>{mentor_name}</strong>,
        </p>
        
        <p style="color: #555; line-height: 1.6; font-size: 16px;">
            Your account has been successfully created on the Mentee Tracker platform. 
            Please find your login credentials below:
        </p>
        
        <div style="background-color: #f8f9fa; border-left: 4px solid #007bff; padding: 20px; margin: 20px 0; border-radius: 4px;">
            <p style="margin: 10px 0; font-size: 16px; color: #333;">
                <strong>Mentor ID:</strong> <span style="color: #007bff; font-family: monospace; font-size: 18px;">{mentor_id}</span>
            </p>
            <p style="margin: 10px 0; font-size: 16px; color: #333;">
                <strong>Password:</strong> <span style="color: #007bff; font-family: monospace; font-size: 18px;">{password}</span>
            </p>
        </div>
        
        <p style="color: #555; line-height: 1.6; font-size: 16px;">
            <strong>Important:</strong> For security reasons, please change your password after your first login.
        </p>
        
        <div style="margin: 30px 0; text-align: center;">
            <a href="https://www.menteetracker.com/" 
               style="background-color: #007bff; color: white; padding: 12px 30px; 
                      text-decoration: none; border-radius: 5px; font-size: 16px; 
                      display: inline-block; font-weight: bold;">
                Login to Mentee Tracker
            </a>
        </div>
        
        <p style="color: #555; line-height: 1.6; font-size: 16px;">
            If you have any questions or need assistance, please don't hesitate to contact our support team.
        </p>
        
        <p style="color: #555; line-height: 1.6; font-size: 16px; margin-top: 30px;">
            Best regards,<br>
            <strong>JGI Mentee Tracker Team</strong>
        </p>
    </div>
    """
    return body


def create_html_email(mentor_name: str, mentor_id: str, password: str) -> str:
    """
    Create complete HTML email with styling.
    
    Args:
        mentor_name: Name of the mentor
        mentor_id: Mentor ID for login
        password: Password for login
    
    Returns:
        Complete HTML email content
    """
    body_content = create_email_body(mentor_name, mentor_id, password)
    
    html_email = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                text-align: center; 
                margin: 0;
                padding: 0;
                background-color: #f4f4f4;
            }}
            .container {{ 
                max-width: 600px; 
                padding: 20px; 
                border-radius: 8px; 
                box-shadow: 0 0 10px rgba(0,0,0,0.1); 
                margin: 20px auto; 
                text-align: left; 
                background-color: #ffffff;
            }}
            .header-container {{ 
                width: 100%; 
                max-width: 600px; 
                margin: 0 auto; 
                display: flex; 
                justify-content: space-between; 
                align-items: center; 
                padding: 20px 0; 
            }}
            img {{ 
                max-width: 100%; 
                height: 50px; 
            }}
            .small-img {{ 
                height: 40px; 
                margin-left: auto; 
            }}
        </style>
    </head>
    <body>
        <div style="padding: 40px 0;">
            <div class="header-container">
                <a href="https://www.menteetracker.com/">
                    <img src="{LOGO_URL}" width="125" alt="Mentee Tracker Logo">
                </a>
                <img class="small-img" src="{JAIN_LOGO_URL}" width="125" alt="Jain University Logo"> 
            </div>
            <div class="container">
                {body_content}
            </div>
            <div style="text-align: center; font-size: 12px; color: #777; margin-top: 20px;">
                <p>&copy; 2025 <a href="https://www.menteetracker.com/" style="color: #333;">Mentee Tracker</a>. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_email


# ============================================================================
# EMAIL SENDING FUNCTION
# ============================================================================

def send_credential_email(to_email: str, mentor_name: str, mentor_id: str, password: str) -> bool:
    """
    Send login credentials email to mentor.
    
    Args:
        to_email: Recipient email address
        mentor_name: Name of the mentor
        mentor_id: Mentor ID for login
        password: Password for login
    
    Returns:
        True if email sent successfully, False otherwise
    """
    # Validate email address
    if not to_email or not isinstance(to_email, str) or '@' not in to_email:
        print(f"[ERROR] Invalid email address: {to_email}")
        return False
    
    subject = "Your Mentee Tracker Login Credentials"
    html_content = create_html_email(mentor_name, mentor_id, password)
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg["From"] = formataddr((SENDER_NAME, SENDER_EMAIL))
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_content, "html"))
        
        # Connect to SMTP server
        print(f"[SENDING] Sending email to {to_email}...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        
        try:
            # Start TLS
            server.starttls()
            
            # Login
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            
            # Send email
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
            
            print(f"[SUCCESS] Email successfully sent to {to_email} ({mentor_name})")
            return True
            
        finally:
            # Always close the connection
            try:
                server.quit()
            except:
                pass
    
    except smtplib.SMTPAuthenticationError as e:
        print(f"[ERROR] SMTP Authentication Error for {to_email}: {str(e)}")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"[ERROR] SMTP Connection Error for {to_email}: {str(e)}")
        return False
    except smtplib.SMTPSenderRefused as e:
        print(f"[ERROR] Sender address refused for {to_email}: {str(e)}")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        print(f"[ERROR] Recipient address refused for {to_email}: {str(e)}")
        return False
    except Exception as e:
        print(f"[ERROR] Error sending email to {to_email}: {str(e)}")
        return False


# ============================================================================
# EXCEL FILE PROCESSING
# ============================================================================

def read_excel_file(file_path: str) -> pd.DataFrame:
    """
    Read mentor data from Excel file with flexible column name handling.
    
    Args:
        file_path: Path to Excel file
    
    Returns:
        DataFrame containing mentor data with standardized column names
    """
    try:
        # Read Excel file
        df = pd.read_excel(file_path, engine='openpyxl')
        
        # Create a mapping for flexible column name matching
        column_mapping = {}
        original_columns = [col.strip() for col in df.columns]
        
        # Map various column name formats to standard names
        for col in original_columns:
            col_upper = col.upper()
            # Map MENTORID / EMPLOYEE ID
            if 'EMPLOYEE ID' in col_upper or 'MENTORID' in col_upper or 'MENTOR ID' in col_upper:
                column_mapping[col] = 'MENTORID'
            # Map MENTOREMAIL / UNIVERSITY MAIL ID / EMAIL
            elif 'UNIVERSITY MAIL' in col_upper or 'MENTOREMAIL' in col_upper or 'MENTOR EMAIL' in col_upper or ('EMAIL' in col_upper and 'MAIL' in col_upper):
                column_mapping[col] = 'MENTOREMAIL'
            # Map MENTORNAME / NAME OF THE FACULTY / NAME
            elif 'NAME OF THE FACULTY' in col_upper or 'MENTORNAME' in col_upper or 'MENTOR NAME' in col_upper or (col_upper == 'NAME'):
                column_mapping[col] = 'MENTORNAME'
            # Map MENTORPASSWORD / PASSWORD
            elif 'MENTORPASSWORD' in col_upper or 'MENTOR PASSWORD' in col_upper or col_upper == 'PASSWORD':
                column_mapping[col] = 'MENTORPASSWORD'
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Check for required columns
        if 'MENTORID' not in df.columns:
            raise ValueError("Missing required column: Employee ID / Mentor ID")
        if 'MENTOREMAIL' not in df.columns:
            raise ValueError("Missing required column: University Mail ID / Mentor Email")
        
        # Get MENTORNAME if available, otherwise use empty string
        if 'MENTORNAME' not in df.columns:
            df['MENTORNAME'] = ''
            print("[WARNING] Name column not found. Using empty name.")
        
        # Generate passwords if not present (format: EmployeeID@FirstName)
        if 'MENTORPASSWORD' not in df.columns:
            print("[INFO] Password column not found. Generating passwords automatically...")
            def generate_password(row):
                mentor_id = str(row['MENTORID']).strip()
                mentor_name = str(row.get('MENTORNAME', '')).strip()
                # Extract first name (first word before space)
                first_name = mentor_name.split()[0] if mentor_name else ''
                # Generate password: EmployeeID@FirstName
                password = f"{mentor_id}@{first_name}" if first_name else mentor_id
                return password
            df['MENTORPASSWORD'] = df.apply(generate_password, axis=1)
            print("[INFO] Passwords generated in format: EmployeeID@FirstName")
        
        return df
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Excel file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading Excel file: {str(e)}")


def process_and_send_emails(excel_file_path: str, delay_seconds: float = 1.0) -> Dict[str, int]:
    """
    Process Excel file and send emails to all mentors.
    
    Args:
        excel_file_path: Path to Excel file
        delay_seconds: Delay between emails (to avoid rate limiting)
    
    Returns:
        Dictionary with success and failure counts
    """
    # Read Excel file
    print(f"\n[INFO] Reading Excel file: {excel_file_path}\n")
    df = read_excel_file(excel_file_path)
    
    print(f"[INFO] Found {len(df)} mentor(s) in the file\n")
    print("=" * 60)
    
    # Statistics
    success_count = 0
    failure_count = 0
    skipped_count = 0
    
    # Process each mentor
    for index, row in df.iterrows():
        mentor_id = str(row['MENTORID']).strip()
        mentor_email = str(row['MENTOREMAIL']).strip()
        mentor_password = str(row['MENTORPASSWORD']).strip()
        mentor_name = str(row.get('MENTORNAME', '')).strip() if 'MENTORNAME' in row else ''
        
        # Skip if email is invalid
        if pd.isna(mentor_email) or '@' not in mentor_email:
            print(f"[SKIP] Skipping row {index + 1}: Invalid email address")
            skipped_count += 1
            continue
        
        # Skip if mentor_id or password is missing
        if pd.isna(mentor_id) or pd.isna(mentor_password) or not mentor_id or not mentor_password:
            print(f"[SKIP] Skipping row {index + 1}: Missing mentor_id or password")
            skipped_count += 1
            continue
        
        # Send email
        if send_credential_email(mentor_email, mentor_name, mentor_id, mentor_password):
            success_count += 1
        else:
            failure_count += 1
        
        # Delay between emails to avoid rate limiting
        if index < len(df) - 1:  # Don't delay after last email
            time.sleep(delay_seconds)
    
    print("\n" + "=" * 60)
    print("\n[SUMMARY]")
    print(f"   [SUCCESS] Successfully sent: {success_count}")
    print(f"   [FAILED] Failed: {failure_count}")
    print(f"   [SKIPPED] Skipped: {skipped_count}")
    print(f"   [TOTAL] Total processed: {len(df)}\n")
    
    return {
        'success': success_count,
        'failure': failure_count,
        'skipped': skipped_count,
        'total': len(df)
    }


# ============================================================================
# MAIN FUNCTION
# ============================================================================

# Default Excel file path
DEFAULT_EXCEL_FILE = r"E:/All/mentee_tracker_mca/Forensic Science Newly Joined Employee ID  (1).xlsx"

def main():
    """Main function to run the script."""
    print("\n" + "=" * 60)
    print("   MENTOR CREDENTIALS EMAIL SENDER")
    print("=" * 60)
    
    # Get Excel file path from command line or use default
    if len(sys.argv) >= 2:
        excel_file_path = sys.argv[1]
    else:
        excel_file_path = DEFAULT_EXCEL_FILE
        print(f"\n[INFO] No file path provided. Using default: {excel_file_path}")
    
    # Check if file exists
    if not os.path.exists(excel_file_path):
        print(f"\n[ERROR] File not found: {excel_file_path}")
        sys.exit(1)
    
    # Confirm before sending
    print(f"\n[INFO] Sender Email: {SENDER_EMAIL}")
    print(f"[INFO] Excel File: {excel_file_path}")
    print("\n[WARNING] This will send emails to all mentors in the Excel file.")
    
    response = input("\nDo you want to continue? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("\n[INFO] Operation cancelled.")
        sys.exit(0)
    
    # Process and send emails
    try:
        results = process_and_send_emails(excel_file_path, delay_seconds=1.0)
        
        if results['failure'] == 0 and results['skipped'] == 0:
            print("\n[SUCCESS] All emails sent successfully!\n")
        elif results['success'] > 0:
            print(f"\n[WARNING] Completed with {results['failure']} failure(s) and {results['skipped']} skipped.\n")
        else:
            print("\n[ERROR] No emails were sent successfully.\n")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n[ERROR] Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

