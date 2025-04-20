import logging
from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict

from .models import (
    EmailData, 
    EmailNotification, 
    EmailType,
    MarginCall,
    RetirementContribution,
    CorporateAction,
    OutgoingAccountTransfer
)

logger = logging.getLogger("financial_digest")

def process_emails(email_data: EmailData) -> Dict[str, Dict[str, List[Any]]]:
    """
    Process incoming email notifications and organize them by recipient (Financial Advisor)
    
    Args:
        email_data: The incoming batch of email notifications
        
    Returns:
        Dictionary mapping advisor IDs to categorized notifications
    """
    logger.info(f"Processing {len(email_data.emails)} email notifications")
    
    # Group emails by recipient (Financial Advisor)
    advisor_emails = defaultdict(lambda: defaultdict(list))
    
    for email in email_data.emails:
        advisor_id = email.recipient_id
        
        # Convert generic email notification to specific notification type
        if email.type == EmailType.MARGIN_CALL:
            notification = _convert_to_margin_call(email)
        elif email.type == EmailType.RETIREMENT_CONTRIBUTION:
            notification = _convert_to_retirement_contribution(email)
        elif email.type == EmailType.CORPORATE_ACTION:
            notification = _convert_to_corporate_action(email)
        elif email.type == EmailType.OUTGOING_ACCOUNT_TRANSFER:
            notification = _convert_to_outgoing_account_transfer(email)
        else:
            logger.warning(f"Unknown email type: {email.type}")
            continue
            
        # Add to appropriate category for this advisor
        notification_type = email.type.value
        advisor_emails[advisor_id][notification_type].append(notification)
        
        logger.debug(f"Processed {email.type} notification for advisor {advisor_id}")
    
    # Convert defaultdict to regular dict for return
    result = {}
    for advisor_id, notifications in advisor_emails.items():
        result[advisor_id] = dict(notifications)
        
    logger.info(f"Processed emails for {len(result)} advisors")
    return result

def _convert_to_margin_call(email: EmailNotification) -> MarginCall:
    """Convert generic email notification to MarginCall model"""
    metadata = email.metadata
    
    return MarginCall(
        id=email.id,
        client_id=email.client_id,
        client_name=email.client_name,
        account_number=metadata.get("account_number", ""),
        call_amount=float(metadata.get("call_amount", 0)),
        due_date=datetime.fromisoformat(metadata.get("due_date", datetime.now().isoformat())).date(),
        current_margin_percentage=float(metadata.get("current_margin_percentage", 0)),
        required_margin_percentage=float(metadata.get("required_margin_percentage", 0)),
        timestamp=email.timestamp,
        priority=email.priority
    )

def _convert_to_retirement_contribution(email: EmailNotification) -> RetirementContribution:
    """Convert generic email notification to RetirementContribution model"""
    metadata = email.metadata
    
    return RetirementContribution(
        id=email.id,
        client_id=email.client_id,
        client_name=email.client_name,
        account_number=metadata.get("account_number", ""),
        contribution_amount=float(metadata.get("contribution_amount", 0)),
        contribution_type=metadata.get("contribution_type", ""),
        tax_year=int(metadata.get("tax_year", datetime.now().year)),
        timestamp=email.timestamp,
        priority=email.priority
    )

def _convert_to_corporate_action(email: EmailNotification) -> CorporateAction:
    """Convert generic email notification to CorporateAction model"""
    metadata = email.metadata
    
    return CorporateAction(
        id=email.id,
        client_id=email.client_id,
        client_name=email.client_name,
        account_number=metadata.get("account_number", ""),
        security_id=metadata.get("security_id", ""),
        security_name=metadata.get("security_name", ""),
        action_type=metadata.get("action_type", ""),
        deadline_date=datetime.fromisoformat(metadata.get("deadline_date", datetime.now().isoformat())).date(),
        description=metadata.get("description", ""),
        timestamp=email.timestamp,
        priority=email.priority
    )

def _convert_to_outgoing_account_transfer(email: EmailNotification) -> OutgoingAccountTransfer:
    """Convert generic email notification to OutgoingAccountTransfer model"""
    metadata = email.metadata
    
    return OutgoingAccountTransfer(
        id=email.id,
        client_id=email.client_id,
        client_name=email.client_name,
        account_number=metadata.get("account_number", ""),
        account_type=metadata.get("account_type", ""),
        net_amount=float(metadata.get("net_amount", 0)),
        gross_amount=float(metadata.get("gross_amount", 0)),
        transfer_type=metadata.get("transfer_type", ""),
        entry_date=datetime.fromisoformat(metadata.get("entry_date", datetime.now().isoformat())).date(),
        payment_date=datetime.fromisoformat(metadata.get("payment_date", datetime.now().isoformat())).date(),
        status=metadata.get("status", ""),
        description=metadata.get("description", ""),
        timestamp=email.timestamp,
        priority=email.priority
    )
