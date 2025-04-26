import smtplib
from email.mime.text import MIMEText
import os

# ✅ Use Gmail's SMTP settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "matthewgorbett@gmail.com"  # Replace with your Gmail address
SMTP_PASSWORD = "jnszmtomgzjubmon"  # ✅ Use your App Password
DOMAIN= os.getenv('DOMAIN', "localhost:5173")

def send_invite_email(email: str, token: str, is_admin: bool):
    """Sends an email invite for user/admin registration."""
    role_text = "admin" if is_admin else "user"
    subject = f"Your {role_text.capitalize()} Invite"
    
    invite_link = f"https://{DOMAIN}/register?token={token}"
    body = (
        f"Hello,\n\nYou have been invited as a {role_text}. Click below to complete signup:\n"
        f"{invite_link}\n\nThis link expires in 2 days."
    )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # ✅ Secure the connection
            server.login(SMTP_USER, SMTP_PASSWORD)  # ✅ Authenticate
            server.sendmail(SMTP_USER, email, msg.as_string())  # ✅ Send email
        print(f"✅ Email sent successfully to {email}")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

def send_password_reset_email(email: str, token: str):
    """Sends a password reset email to the user."""
    subject = "Reset Your Password"
    
    # Construct the password reset link
    reset_link = f"https://{DOMAIN}/newpassword?token={token}"
    
    body = (
        f"Hello,\n\n"
        f"You requested a password reset. Click the link below to set a new password:\n"
        f"{reset_link}\n\n"
        f"If you did not request this, please ignore this email.\n"
        f"This link is valid for 1 hour."
    )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, email, msg.as_string())
        print(f"✅ Password reset email sent successfully to {email}")
    except Exception as e:
        print(f"❌ Error sending password reset email: {e}")
        # It's important to handle this potential failure, maybe log it 
        # but avoid raising an exception back to the user request path
        # to prevent revealing if an email address exists.
        pass # Silently fail for security reasons
