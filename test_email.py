#!/usr/bin/env python3
"""
Simple test script to verify email sending functionality.
This uses a different approach to send emails via Gmail.
"""

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get SMTP configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "gunasekaran@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").replace(" ", "")  # Remove spaces
EMAIL_FROM = os.getenv("EMAIL_FROM", "gunaconfid@gmail.com")

# Print configuration for debugging
print(f"SMTP_SERVER: {SMTP_SERVER}")
print(f"SMTP_PORT: {SMTP_PORT}")
print(f"SMTP_USERNAME: {SMTP_USERNAME}")
print(f"EMAIL_FROM: {EMAIL_FROM}")
print(f"SMTP_PASSWORD set: {bool(SMTP_PASSWORD)}")
print(f"SMTP_PASSWORD length: {len(SMTP_PASSWORD)}")

def send_test_email():
    """Send a test email using standard smtplib."""
    
    # Create message
    message = MIMEMultipart()
    message["From"] = EMAIL_FROM
    message["To"] = "gunaconfid@gmail.com"  # Send to yourself for testing
    message["Subject"] = "Financial Digest Emailer - Test Email"
    
    # Add body
    body = """
    <html>
    <body>
        <h1>Test Email from Financial Digest Emailer</h1>
        <p>This is a test email to verify the SMTP configuration.</p>
        <p>If you're seeing this, the email sending functionality is working!</p>
    </body>
    </html>
    """
    message.attach(MIMEText(body, "html"))
    
    try:
        # Create secure connection with server and send email
        context = ssl.create_default_context()
        
        if SMTP_PORT == 465:
            # SSL connection
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(message)
                print("Test email sent successfully!")
        else:
            # STARTTLS connection
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.ehlo()  # Can be omitted
                server.starttls(context=context)
                server.ehlo()  # Can be omitted
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(message)
                print("Test email sent successfully!")
                
    except Exception as e:
        print(f"Failed to send test email: {str(e)}")
        
        # Print more detailed error information
        if "Username and Password not accepted" in str(e):
            print("\nThis error typically occurs when:")
            print("1. The password is incorrect")
            print("2. You need to use an App Password (if 2FA is enabled)")
            print("3. Less secure app access is disabled in your Google account")
            print("\nTo fix this:")
            print("- Generate an App Password at: https://myaccount.google.com/apppasswords")
            print("- Make sure to use the App Password without spaces")
            print("- If you don't have 2FA enabled, enable 'Less secure app access' in your Google account settings")

if __name__ == "__main__":
    send_test_email()
