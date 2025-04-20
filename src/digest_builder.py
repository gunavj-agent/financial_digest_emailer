import logging
from typing import Dict, List, Any
from datetime import date, datetime
from collections import defaultdict

from .models import (
    AdvisorDigest,
    MarginCall,
    RetirementContribution,
    CorporateAction,
    OutgoingAccountTransfer
)

logger = logging.getLogger("financial_digest")

# In a real implementation, this would be replaced with a database query
# For this example, we'll use an in-memory store
ADVISOR_DATA = {
    "A001": {
        "name": "John Smith",
        "email": "john.smith@example.com"
    },
    "A002": {
        "name": "Sarah Johnson",
        "email": "sarah.johnson@example.com"
    },
    "A003": {
        "name": "Michael Chen",
        "email": "michael.chen@example.com"
    }
}

# In-memory storage for processed notifications
# In a real implementation, this would be a database
NOTIFICATIONS_STORE = defaultdict(lambda: defaultdict(list))

def build_digest(advisor_id: str, digest_date: date) -> AdvisorDigest:
    """
    Build a digest for a specific advisor for a given date
    
    Args:
        advisor_id: The ID of the advisor
        digest_date: The date for which to build the digest
        
    Returns:
        AdvisorDigest object containing all notifications for the advisor
    """
    logger.info(f"Building digest for advisor {advisor_id} for date {digest_date}")
    
    # In a real implementation, this would query a database
    # For this example, we'll use our in-memory store
    if advisor_id not in ADVISOR_DATA:
        logger.warning(f"Advisor {advisor_id} not found in database")
        raise ValueError(f"Advisor {advisor_id} not found")
    
    advisor_info = ADVISOR_DATA[advisor_id]
    
    # Create the digest object
    digest = AdvisorDigest(
        advisor_id=advisor_id,
        advisor_name=advisor_info["name"],
        advisor_email=advisor_info["email"],
        date=digest_date
    )
    
    # Add notifications from our store
    # In a real implementation, this would filter by date from a database
    if advisor_id in NOTIFICATIONS_STORE:
        advisor_notifications = NOTIFICATIONS_STORE[advisor_id]
        
        # Add margin calls
        if "margin_call" in advisor_notifications:
            digest.margin_calls = advisor_notifications["margin_call"]
            
        # Add retirement contributions
        if "retirement_contribution" in advisor_notifications:
            digest.retirement_contributions = advisor_notifications["retirement_contribution"]
            
        # Add corporate actions
        if "corporate_action" in advisor_notifications:
            digest.corporate_actions = advisor_notifications["corporate_action"]
            
        # Add outgoing account transfers
        if "outgoing account transfer" in advisor_notifications:
            digest.outgoing_account_transfers = advisor_notifications["outgoing account transfer"]
    
    # Generate summary statistics
    digest.summary_stats = _generate_summary_stats(digest)
    
    logger.info(f"Built digest for advisor {advisor_id} with {len(digest.margin_calls)} margin calls, "
                f"{len(digest.retirement_contributions)} retirement contributions, "
                f"{len(digest.corporate_actions)} corporate actions, and "
                f"{len(digest.outgoing_account_transfers)} outgoing account transfers")
    
    return digest

def _generate_summary_stats(digest: AdvisorDigest) -> Dict[str, Any]:
    """Generate summary statistics for a digest"""
    stats = {
        "total_notifications": (
            len(digest.margin_calls) + 
            len(digest.retirement_contributions) + 
            len(digest.corporate_actions) +
            len(digest.outgoing_account_transfers)
        ),
        "margin_calls": {
            "count": len(digest.margin_calls),
            "total_amount": sum(call.call_amount for call in digest.margin_calls),
            "high_priority_count": sum(1 for call in digest.margin_calls if call.priority >= 4)
        },
        "retirement_contributions": {
            "count": len(digest.retirement_contributions),
            "total_amount": sum(contrib.contribution_amount for contrib in digest.retirement_contributions)
        },
        "corporate_actions": {
            "count": len(digest.corporate_actions),
            "by_type": defaultdict(int)
        },
        "outgoing_account_transfers": {
            "count": len(digest.outgoing_account_transfers),
            "total_amount": sum(transfer.net_amount for transfer in digest.outgoing_account_transfers),
            "by_status": defaultdict(int),
            "high_priority_count": sum(1 for transfer in digest.outgoing_account_transfers if transfer.priority >= 4)
        },
        "has_high_priority": digest.has_high_priority
    }
    
    # Count corporate actions by type
    for action in digest.corporate_actions:
        stats["corporate_actions"]["by_type"][action.action_type] += 1
    
    # Count outgoing account transfers by status
    for transfer in digest.outgoing_account_transfers:
        stats["outgoing_account_transfers"]["by_status"][transfer.status] += 1
    
    # Convert defaultdicts to regular dicts for serialization
    stats["corporate_actions"]["by_type"] = dict(stats["corporate_actions"]["by_type"])
    stats["outgoing_account_transfers"]["by_status"] = dict(stats["outgoing_account_transfers"]["by_status"])
    
    return stats

def store_notifications(advisor_id: str, notification_type: str, notifications: List[Any]) -> None:
    """
    Store notifications in our in-memory store
    In a real implementation, this would store to a database
    
    Args:
        advisor_id: The ID of the advisor
        notification_type: The type of notification (margin_call, retirement_contribution, corporate_action)
        notifications: List of notification objects
    """
    NOTIFICATIONS_STORE[advisor_id][notification_type] = notifications
    logger.info(f"Stored {len(notifications)} {notification_type} notifications for advisor {advisor_id}")
