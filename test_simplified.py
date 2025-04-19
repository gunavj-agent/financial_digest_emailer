#!/usr/bin/env python3
"""
Simplified test script for the Financial Digest Emailer workflow.
This script tests the core components directly without using the DigestRequest model.
"""

import json
import os
import asyncio
import logging
from datetime import datetime, date
from dotenv import load_dotenv

# Import only the models we need directly
from src.models import EmailData, EmailNotification, EmailType, AdvisorDigest, MarginCall, RetirementContribution, CorporateAction
from src.email_processor import process_emails
from src.digest_builder import build_digest, store_notifications
from src.ai_insights import generate_insights
from src.email_sender import send_digest_email

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_workflow")

# Load environment variables
load_dotenv()

# Print loaded environment variables for debugging
logger = logging.getLogger("test_workflow")
logger.info(f"ANTHROPIC_API_KEY set: {os.getenv('ANTHROPIC_API_KEY') is not None}")
logger.info(f"SMTP_SERVER: {os.getenv('SMTP_SERVER')}")
logger.info(f"SMTP_USERNAME: {os.getenv('SMTP_USERNAME')}")
logger.info(f"EMAIL_FROM: {os.getenv('EMAIL_FROM')}")

async def test_workflow():
    """Test the entire Financial Digest Emailer workflow"""
    try:
        # Step 1: Load sample email data
        logger.info("Loading sample email data...")
        with open("data/sample_email_data.json", "r") as f:
            email_data_dict = json.load(f)
        
        # Convert to EmailData model
        email_data = EmailData.parse_obj(email_data_dict)
        logger.info(f"Loaded {len(email_data.emails)} email notifications")
        
        # Step 2: Process emails
        logger.info("Processing emails...")
        processed_data = process_emails(email_data)
        logger.info(f"Processed emails for {len(processed_data)} advisors")
        
        # Store notifications for each advisor
        for advisor_id, notifications in processed_data.items():
            for notification_type, items in notifications.items():
                store_notifications(advisor_id, notification_type, items)
                logger.info(f"Stored {len(items)} {notification_type} notifications for advisor {advisor_id}")
        
        # Step 3: Build digest for advisor A001
        logger.info("Building digest for advisor A001...")
        advisor_id = "A001"
        digest_date = date.today()
        digest = build_digest(advisor_id, digest_date)
        
        # Update the advisor email to match the one in .env
        digest.advisor_email = "gunaconfid@gmail.com"
        logger.info(f"Built digest with {len(digest.margin_calls)} margin calls, "
                   f"{len(digest.retirement_contributions)} retirement contributions, and "
                   f"{len(digest.corporate_actions)} corporate actions")
        
        # Step 4: Generate AI insights
        logger.info("Generating AI insights...")
        insights = generate_insights(digest)
        digest.ai_insights = insights
        logger.info(f"Generated {len(insights)} AI insights")
        
        # Step 5: Send digest email
        logger.info("Sending digest email...")
        result = await send_digest_email(digest)
        
        if result.success:
            logger.info(f"Successfully sent digest email to {result.advisor_email}")
            logger.info(f"Message: {result.message}")
        else:
            logger.error(f"Failed to send digest email: {result.message}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error in workflow: {str(e)}")
        raise

if __name__ == "__main__":
    # Run the test workflow
    result = asyncio.run(test_workflow())
    
    # Print final result
    if result.success:
        print("\n✅ Workflow test completed successfully!")
        print(f"Digest email sent to {result.advisor_email}")
    else:
        print("\n❌ Workflow test failed!")
        print(f"Error: {result.message}")
