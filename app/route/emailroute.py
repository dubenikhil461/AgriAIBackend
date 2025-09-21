from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
EMAIL_USER = os.getenv("EMAIL_USER")  # Your Gmail
EMAIL_PASS = os.getenv("EMAIL_PASS")  # App Password

router = APIRouter()

# ---------- Request model ----------
class ContactForm(BaseModel):
    name: str
    email: EmailStr
    message: str

# List of members to send email to
MEMBERS = [
    "nikhildubey461@gmail.com",
    "Mayankpandey892899@gmail.com",
    "pplsolutionsprateek7@gmail.com"
]

# ---------- Email sending function ----------
def send_email_to_members(client_name: str, client_email: str, message: str):
    sender_email = EMAIL_USER
    password = EMAIL_PASS

    for receiver_email in MEMBERS:
        msg = MIMEMultipart('alternative')
        msg['From'] = f"Contact Form <{sender_email}>"
        msg['To'] = receiver_email
        msg['Subject'] = f"AgriAI Inquiry from {client_name}"
        msg.add_header('Reply-To', client_email)  # So members can reply to the client

        # Create both plain text and HTML versions
        text_body = create_text_body(client_name, client_email, message)
        html_body = create_html_body(client_name, client_email, message)
        
        # Attach both versions
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            server.quit()
            print(f"Email sent to {receiver_email}")
        except Exception as e:
            print(f"Failed to send to {receiver_email}: {e}")
            return False
    return True

def create_text_body(client_name: str, client_email: str, message: str) -> str:
    """Create a well-formatted plain text email body"""
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                          🌱 AGRI-AI INQUIRY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 CONTACT INFORMATION:
   • Name: {client_name}
   • Email: {client_email}
   • Submitted: {timestamp}

🌾 INQUIRY DETAILS:
{'-' * 60}
{message}
{'-' * 60}

💡 NEXT STEPS:
   • Reply directly to this email to respond to {client_name}
   • Their inquiry will be automatically forwarded to: {client_email}
   • Consider their interest in AgriAI solutions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌱 This inquiry was submitted through the AgriAI platform.
Someone is interested in your agricultural technology solutions!
"""

def create_html_body(client_name: str, client_email: str, message: str) -> str:
    """Create a well-formatted HTML email body"""
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>New Contact Form Submission</title>
</head>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; background-color: #f4f4f4; padding: 20px;">
    
    <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%); color: white; padding: 20px; margin: -30px -30px 30px -30px; border-radius: 10px 10px 0 0; text-align: center;">
            <h1 style="margin: 0; font-size: 24px; font-weight: 300;">🌱 AgriAI - New Inquiry</h1>
        </div>
        
        <!-- Contact Information -->
        <div style="background-color: #f1f8e9; padding: 20px; border-radius: 8px; margin-bottom: 25px; border-left: 4px solid #4CAF50;">
            <h2 style="margin-top: 0; color: #2E7D32; font-size: 18px;">👤 Contact Information</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #555; width: 80px;">Name:</td>
                    <td style="padding: 8px 0; color: #333;">{client_name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #555;">Email:</td>
                    <td style="padding: 8px 0;"><a href="mailto:{client_email}" style="color: #4CAF50; text-decoration: none;">{client_email}</a></td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #555;">Date:</td>
                    <td style="padding: 8px 0; color: #666;">{timestamp}</td>
                </tr>
            </table>
        </div>
        
        <!-- Message -->
        <div style="margin-bottom: 25px;">
            <h2 style="color: #2E7D32; font-size: 18px; border-bottom: 2px solid #e9ecef; padding-bottom: 10px;">💬 Inquiry Details</h2>
            <div style="background-color: #ffffff; padding: 20px; border: 1px solid #e9ecef; border-radius: 8px; white-space: pre-wrap; font-size: 15px; line-height: 1.7;">
{message}
            </div>
        </div>
        
        <!-- Action Buttons -->
        <div style="text-align: center; margin: 30px 0;">
            <a href="mailto:{client_email}?subject=Re: Your AgriAI Inquiry" 
               style="background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%); 
                      color: white; 
                      padding: 12px 25px; 
                      text-decoration: none; 
                      border-radius: 25px; 
                      font-weight: bold; 
                      display: inline-block; 
                      transition: transform 0.2s;">
                🌾 Respond to Inquiry
            </a>
        </div>
        
        <!-- Footer -->
        <div style="border-top: 1px solid #e9ecef; padding-top: 20px; text-align: center; color: #666; font-size: 13px;">
            <p style="margin: 0;">🌱 This inquiry was submitted via the AgriAI contact form.</p>
            <p style="margin: 5px 0 0 0;">Someone is interested in learning more about your agricultural AI solutions!</p>
        </div>
        
    </div>
    
</body>
</html>
"""

# ---------- FastAPI endpoint ----------
@router.post("/contact")
async def contact_endpoint(form: ContactForm):
    success = send_email_to_members(form.name, form.email, form.message)
    if success:
        return {"message": "Your message has been sent to all members successfully!"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send email to all members")