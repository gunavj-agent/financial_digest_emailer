import os
import logging
from typing import Dict, Any
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import jinja2
from dotenv import load_dotenv

from .models import AdvisorDigest, EmailDeliveryResult
from .ai_insights import generate_executive_summary

# Configure logging
logger = logging.getLogger("financial_digest")

# Load environment variables
load_dotenv()

# Get SMTP configuration from environment variables
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))  # Use the port from .env
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "gunasekaran@gmail.com")

# Get password and remove any spaces (app passwords should be entered without spaces)
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").replace(" ", "") if os.getenv("SMTP_PASSWORD") else ""

EMAIL_FROM = os.getenv("EMAIL_FROM", "gunaconfid@gmail.com")

# Log SMTP configuration status
logger.info(f"SMTP_SERVER: {SMTP_SERVER}")
logger.info(f"SMTP_PORT: {SMTP_PORT}")
logger.info(f"SMTP_USERNAME: {SMTP_USERNAME}")
logger.info(f"EMAIL_FROM: {EMAIL_FROM}")
logger.info(f"SMTP_PASSWORD set: {bool(SMTP_PASSWORD)}")

# Set up Jinja2 template environment
template_loader = jinja2.FileSystemLoader("templates")
template_env = jinja2.Environment(loader=template_loader)

async def send_digest_email(digest: AdvisorDigest) -> EmailDeliveryResult:
    """
    Send a digest email to an advisor
    
    Args:
        digest: The advisor digest to send
        
    Returns:
        EmailDeliveryResult object with the result of the email delivery
    """
    logger.info(f"Sending digest email to advisor {digest.advisor_id} ({digest.advisor_email})")
    
    try:
        # Generate HTML email content
        html_content = _generate_html_content(digest)
        
        # Create email message
        message = MIMEMultipart("alternative")
        message["Subject"] = f"Financial Digest for {digest.date}"
        message["From"] = EMAIL_FROM
        message["To"] = digest.advisor_email
        
        # Add HTML content
        message.attach(MIMEText(html_content, "html"))
        
        # Send email
        if not all([SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD]):
            logger.warning("SMTP configuration not complete, skipping email send")
            return EmailDeliveryResult(
                advisor_id=digest.advisor_id,
                advisor_email=digest.advisor_email,
                success=False,
                message="SMTP configuration not complete"
            )
        
        try:
            if SMTP_PORT == 465:
                # For SSL (port 465)
                await aiosmtplib.send(
                    message,
                    hostname=SMTP_SERVER,
                    port=SMTP_PORT,
                    username=SMTP_USERNAME,
                    password=SMTP_PASSWORD,
                    use_tls=True
                )
            else:
                # For STARTTLS (port 587)
                await aiosmtplib.send(
                    message,
                    hostname=SMTP_SERVER,
                    port=SMTP_PORT,
                    username=SMTP_USERNAME,
                    password=SMTP_PASSWORD,
                    start_tls=True
                )
            
            logger.info(f"Email sent successfully to {digest.advisor_email}")
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return EmailDeliveryResult(
                advisor_id=digest.advisor_id,
                advisor_email=digest.advisor_email,
                success=False,
                message=f"Error sending email: {str(e)}"
            )
        
        logger.info(f"Successfully sent digest email to {digest.advisor_email}")
        
        return EmailDeliveryResult(
            advisor_id=digest.advisor_id,
            advisor_email=digest.advisor_email,
            success=True,
            message="Email sent successfully"
        )
        
    except Exception as e:
        logger.error(f"Error sending digest email: {str(e)}")
        
        return EmailDeliveryResult(
            advisor_id=digest.advisor_id,
            advisor_email=digest.advisor_email,
            success=False,
            message=f"Error sending email: {str(e)}"
        )

def _generate_html_content(digest: AdvisorDigest) -> str:
    """Generate HTML content for the digest email"""
    try:
        # Load base template
        template = template_env.get_template("base_digest.html")
        
        # Generate executive summary using Claude
        executive_summary = generate_executive_summary(digest)
        
        # Render template with digest data
        html_content = template.render(
            advisor_name=digest.advisor_name,
            date=digest.date,
            margin_calls=digest.margin_calls,
            retirement_contributions=digest.retirement_contributions,
            corporate_actions=digest.corporate_actions,
            outgoing_account_transfers=digest.outgoing_account_transfers,
            ai_insights=digest.ai_insights,
            summary_stats=digest.summary_stats,
            has_high_priority=digest.has_high_priority,
            current_year=datetime.now().year,
            executive_summary=executive_summary
        )
        
        return html_content
        
    except jinja2.exceptions.TemplateError as e:
        logger.error(f"Template error: {str(e)}")
        # Fallback to basic HTML if template fails
        return _generate_fallback_html(digest)

def _generate_fallback_html(digest: AdvisorDigest) -> str:
    """Generate basic HTML content as a fallback"""
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #333; }}
            h1, h2, h3 {{ color: #2c3e50; }}
            .high-priority {{ color: #e74c3c; font-weight: bold; }}
            .section {{ margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            .insight {{ background-color: #f8f9fa; padding: 10px; margin-bottom: 10px; border-left: 4px solid #3498db; }}
        </style>
    </head>
    <body>
        <h1>Financial Digest for {digest.date}</h1>
        <p>Hello {digest.advisor_name},</p>
        <p>Here is your financial digest for {digest.date}.</p>
        
        <div class="section">
            <h2>Summary</h2>
            <p>Total notifications: {digest.summary_stats.get('total_notifications', 0)}</p>
            <p>Margin calls: {len(digest.margin_calls)}</p>
            <p>Retirement contributions: {len(digest.retirement_contributions)}</p>
            <p>Corporate actions: {len(digest.corporate_actions)}</p>
            <p>Outgoing account transfers: {len(digest.outgoing_account_transfers)}</p>
            
            <!-- Generate executive summary if possible -->
            {generate_executive_summary(digest) if 'generate_executive_summary' in globals() else ''}
        </div>
    """
    
    # Add margin calls section
    if digest.margin_calls:
        html += f"""
        <div class="section">
            <h2>Margin Calls</h2>
        """
        for call in digest.margin_calls:
            priority_class = "high-priority" if call.priority >= 4 else ""
            html += f"""
            <div class="{priority_class}">
                <h3>{call.client_name} - ${call.call_amount:,.2f}</h3>
                <p>Account: {call.account_number}</p>
                <p>Due date: {call.due_date}</p>
                <p>Current margin: {call.current_margin_percentage}%</p>
                <p>Required margin: {call.required_margin_percentage}%</p>
            </div>
            """
        html += "</div>"
    
    # Add retirement contributions section
    if digest.retirement_contributions:
        html += f"""
        <div class="section">
            <h2>Retirement Contributions</h2>
        """
        for contrib in digest.retirement_contributions:
            html += f"""
            <div>
                <h3>{contrib.client_name} - ${contrib.contribution_amount:,.2f}</h3>
                <p>Account: {contrib.account_number}</p>
                <p>Type: {contrib.contribution_type}</p>
                <p>Tax year: {contrib.tax_year}</p>
            </div>
            """
        html += "</div>"
    
    # Add corporate actions section
    if digest.corporate_actions:
        html += f"""
        <div class="section">
            <h2>Corporate Actions</h2>
        """
        for action in digest.corporate_actions:
            priority_class = "high-priority" if action.priority >= 4 else ""
            html += f"""
            <div class="{priority_class}">
                <h3>{action.client_name} - {action.security_name}</h3>
                <p>Account: {action.account_number}</p>
                <p>Action type: {action.action_type}</p>
                <p>Deadline: {action.deadline_date}</p>
                <p>{action.description}</p>
            </div>
            """
        html += "</div>"
    
    # Add outgoing account transfers section
    if digest.outgoing_account_transfers:
        html += f"""
        <div class="section">
            <h2>Outgoing Account Transfers</h2>
        """
        for transfer in digest.outgoing_account_transfers:
            priority_class = "high-priority" if transfer.priority >= 4 else ""
            html += f"""
            <div class="{priority_class}">
                <h3>{transfer.client_name} - ${transfer.net_amount:,.2f}</h3>
                <p>Account: {transfer.account_number}</p>
                <p>Account Type: {transfer.account_type}</p>
                <p>Transfer Type: {transfer.transfer_type}</p>
                <p>Status: {transfer.status}</p>
                <p>Entry Date: {transfer.entry_date}</p>
                <p>Payment Date: {transfer.payment_date}</p>
                <p>{transfer.description}</p>
            </div>
            """
        html += "</div>"
    
    # Add AI insights section
    if digest.ai_insights:
        html += f"""
        <div class="section">
            <h2>AI Insights</h2>
        """
        for insight in digest.ai_insights:
            html += f"""
            <div class="insight">
                <h3>{insight.title}</h3>
                <p>{insight.content}</p>
                {f"<p><strong>Recommendation:</strong> {insight.recommendation}</p>" if insight.recommendation else ""}
                {f"<p><strong>Related clients:</strong> {', '.join(insight.related_clients)}</p>" if insight.related_clients else ""}
            </div>
            """
        html += "</div>"
    
    # Close HTML
    html += f"""
        <p>This is an automated digest email. Please do not reply to this email.</p>
        <p>&copy; {datetime.now().year} Financial Digest Emailer</p>
    </body>
    </html>
    """
    
    return html
