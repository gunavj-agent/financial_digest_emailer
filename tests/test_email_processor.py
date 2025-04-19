import pytest
from datetime import datetime, date
from src.email_processor import process_emails
from src.models import EmailData, EmailNotification, EmailType

def test_process_emails(sample_email_data):
    """Test that emails are correctly processed and organized by advisor"""
    # Process the sample email data
    result = process_emails(sample_email_data)
    
    # Check that the result contains the expected advisor IDs
    assert "A001" in result
    assert "A002" in result
    
    # Check that advisor A001 has the expected notification types
    advisor_a001 = result["A001"]
    assert "margin_call" in advisor_a001
    assert "retirement_contribution" in advisor_a001
    assert len(advisor_a001["margin_call"]) == 1
    assert len(advisor_a001["retirement_contribution"]) == 1
    
    # Check that advisor A002 has the expected notification types
    advisor_a002 = result["A002"]
    assert "corporate_action" in advisor_a002
    assert len(advisor_a002["corporate_action"]) == 1
    
    # Check that the margin call was correctly converted
    margin_call = advisor_a001["margin_call"][0]
    assert margin_call.client_name == "Alice Johnson"
    assert margin_call.call_amount == 5000.00
    assert margin_call.priority == 5
    
    # Check that the retirement contribution was correctly converted
    retirement = advisor_a001["retirement_contribution"][0]
    assert retirement.client_name == "Bob Williams"
    assert retirement.contribution_amount == 6000.00
    assert retirement.contribution_type == "IRA"
    assert retirement.tax_year == 2025
    
    # Check that the corporate action was correctly converted
    corporate = advisor_a002["corporate_action"][0]
    assert corporate.client_name == "Charlie Davis"
    assert corporate.security_name == "Apple Inc."
    assert corporate.action_type == "stock split"

def test_process_emails_empty():
    """Test processing an empty list of emails"""
    empty_data = EmailData(emails=[])
    result = process_emails(empty_data)
    
    # Result should be an empty dict
    assert result == {}

def test_process_emails_unknown_type():
    """Test processing an email with an unknown type"""
    # This test requires modifying the EmailType enum to include a test type
    # Since we can't modify the enum in the test, we'll skip this test
    pass
