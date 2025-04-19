import pytest
from datetime import date
from src.digest_builder import build_digest, store_notifications, _generate_summary_stats
from src.models import MarginCall, RetirementContribution, CorporateAction

def test_build_digest():
    """Test building a digest for an advisor"""
    # Store some test notifications first
    advisor_id = "A001"
    margin_calls = [
        MarginCall(
            id="mc001",
            client_id="C001",
            client_name="Alice Johnson",
            account_number="ACC123456",
            call_amount=5000.00,
            due_date=date.today(),
            current_margin_percentage=15.5,
            required_margin_percentage=25.0,
            timestamp=date.today(),
            priority=5
        )
    ]
    retirement_contributions = [
        RetirementContribution(
            id="rc001",
            client_id="C002",
            client_name="Bob Williams",
            account_number="ACC789012",
            contribution_amount=6000.00,
            contribution_type="IRA",
            tax_year=2025,
            timestamp=date.today(),
            priority=3
        )
    ]
    
    # Store the notifications
    store_notifications(advisor_id, "margin_call", margin_calls)
    store_notifications(advisor_id, "retirement_contribution", retirement_contributions)
    
    # Build the digest
    digest = build_digest(advisor_id, date.today())
    
    # Check that the digest contains the expected data
    assert digest.advisor_id == "A001"
    assert digest.advisor_name == "John Smith"
    assert digest.advisor_email == "john.smith@example.com"
    assert len(digest.margin_calls) == 1
    assert len(digest.retirement_contributions) == 1
    assert len(digest.corporate_actions) == 0
    
    # Check that the summary stats were generated correctly
    assert digest.summary_stats["total_notifications"] == 2
    assert digest.summary_stats["margin_calls"]["count"] == 1
    assert digest.summary_stats["margin_calls"]["total_amount"] == 5000.00
    assert digest.summary_stats["retirement_contributions"]["count"] == 1
    assert digest.summary_stats["retirement_contributions"]["total_amount"] == 6000.00
    assert digest.summary_stats["has_high_priority"] == True

def test_build_digest_unknown_advisor():
    """Test building a digest for an unknown advisor"""
    with pytest.raises(ValueError):
        build_digest("UNKNOWN", date.today())

def test_generate_summary_stats(sample_advisor_digest):
    """Test generating summary statistics for a digest"""
    stats = _generate_summary_stats(sample_advisor_digest)
    
    assert stats["total_notifications"] == 2
    assert stats["margin_calls"]["count"] == 1
    assert stats["margin_calls"]["total_amount"] == 5000.00
    assert stats["margin_calls"]["high_priority_count"] == 1
    assert stats["retirement_contributions"]["count"] == 1
    assert stats["retirement_contributions"]["total_amount"] == 6000.00
    assert stats["corporate_actions"]["count"] == 0
    assert stats["has_high_priority"] == True
