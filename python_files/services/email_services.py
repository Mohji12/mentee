import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

def send_email(to_email: str, subject: str, body: str):
    # SMTP_SERVER = "smtp-relay.brevo.com"
    # SMTP_PORT = 587
    # SMTP_USERNAME = "84a6ad001@smtp-brevo.com"
    # SMTP_PASSWORD = "gOLTc1vCVKQ9qNUd"
    # SENDER_EMAIL = "noreply@krintix.com"
    SMTP_SERVER = "smtp.zeptomail.in"
    SMTP_PORT = 587
    SMTP_USERNAME = "emailapikey"
    SMTP_PASSWORD = "Zoho-enczapikey PHtE6r0NQr/tgjUv+0RS5qC6QpalMo4uqe1jeFVCsI5FWPYCGk1Sqd4ukmfhr00jXPURHKHKwN9v4OmZserXdDy5YWxOD2qyqK3sx/VYSPOZsbq6x00Zsl4afkLeUYHvcdZo1ifSvdvdNA=="
    SENDER_EMAIL = "jgi@menteetracker.com"

    # Logo URL
    LOGO_URL = "https://res.cloudinary.com/dvlitilou/image/upload/v1779924617/logo_mentee-removebg-preview_coyhds.png"

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
        msg = MIMEMultipart()
        msg["From"] = formataddr(("Mentee Tracker", SENDER_EMAIL))
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))  # Send email as HTML

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())

        print(f"Email successfully sent to {to_email}")

    except smtplib.SMTPAuthenticationError:
        print("Failed to send email: SMTP Authentication Error")
    except smtplib.SMTPConnectError:
        print("Failed to send email: SMTP Connection Error")
    except smtplib.SMTPSenderRefused:
        print("Failed to send email: Sender address refused")
    except Exception as e:
        print(f"Failed to send email: {e}")
