import pytest
from fastapi.testclient import TestClient
from datetime import datetime, date
from typing import Dict, List, Any

# Import app directly to avoid circular imports
from src.main import app
# Import models individually to avoid recursion issues
from src.models import (
    EmailNotification, 
    EmailType,
    MarginCall,
    RetirementContribution,
    CorporateAction,
    AdvisorDigest,
    EmailData
)

@pytest.fixture
def client():
    """Test client for the FastAPI application"""
    return TestClient(app)

@pytest.fixture
def auth_headers():
    """Authentication headers for protected endpoints"""
    client = TestClient(app)
    response = client.post(
        "/token",
        data={"username": "admin", "password": "password"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sample_email_data():
    """Sample email notification data for testing"""
    return EmailData(
        emails=[
            EmailNotification(
                id="email1",
                type=EmailType.MARGIN_CALL,
                subject="Margin Call Notice",
                body="This is a margin call notification.",
                recipient_id="A001",
                recipient_email="john.smith@example.com",
                client_id="C001",
                client_name="Alice Johnson",
                timestamp=datetime.now(),
                metadata={
                    "account_number": "ACC123456",
                    "call_amount": 5000.00,
                    "due_date": date.today().isoformat(),
                    "current_margin_percentage": 15.5,
                    "required_margin_percentage": 25.0
                },
                priority=5
            ),
            EmailNotification(
                id="email2",
                type=EmailType.RETIREMENT_CONTRIBUTION,
                subject="Retirement Contribution Confirmation",
                body="This is a retirement contribution confirmation.",
                recipient_id="A001",
                recipient_email="john.smith@example.com",
                client_id="C002",
                client_name="Bob Williams",
                timestamp=datetime.now(),
                metadata={
                    "account_number": "ACC789012",
                    "contribution_amount": 6000.00,
                    "contribution_type": "IRA",
                    "tax_year": 2025
                },
                priority=3
            ),
            EmailNotification(
                id="email3",
                type=EmailType.CORPORATE_ACTION,
                subject="Corporate Action Required",
                body="This is a corporate action notification.",
                recipient_id="A002",
                recipient_email="sarah.johnson@example.com",
                client_id="C003",
                client_name="Charlie Davis",
                timestamp=datetime.now(),
                metadata={
                    "account_number": "ACC345678",
                    "security_id": "AAPL",
                    "security_name": "Apple Inc.",
                    "action_type": "stock split",
                    "deadline_date": date.today().isoformat(),
                    "description": "2-for-1 stock split requiring shareholder approval."
                },
                priority=4
            )
        ]
    )

@pytest.fixture
def sample_advisor_digest():
    """Sample advisor digest for testing"""
    return AdvisorDigest(
        advisor_id="A001",
        advisor_name="John Smith",
        advisor_email="john.smith@example.com",
        date=date.today(),
        margin_calls=[
            MarginCall(
                id="mc001",
                client_id="C001",
                client_name="Alice Johnson",
                account_number="ACC123456",
                call_amount=5000.00,
                due_date=date.today(),
                current_margin_percentage=15.5,
                required_margin_percentage=25.0,
                timestamp=datetime.now(),
                priority=5
            )
        ],
        retirement_contributions=[
            RetirementContribution(
                id="rc001",
                client_id="C002",
                client_name="Bob Williams",
                account_number="ACC789012",
                contribution_amount=6000.00,
                contribution_type="IRA",
                tax_year=2025,
                timestamp=datetime.now(),
                priority=3
            )
        ],
        corporate_actions=[],
        ai_insights=[],
        summary_stats={
            "total_notifications": 2,
            "margin_calls": {
                "count": 1,
                "total_amount": 5000.00,
                "high_priority_count": 1
            },
            "retirement_contributions": {
                "count": 1,
                "total_amount": 6000.00
            },
            "corporate_actions": {
                "count": 0,
                "by_type": {}
            },
            "has_high_priority": True
        }
    )
