import pytest
from fastapi import status
from unittest.mock import patch, MagicMock
from datetime import date

@pytest.mark.parametrize("endpoint,method", [
    ("/api/process-emails", "POST"),
    ("/api/generate-digests", "POST"),
    ("/api/send-digests", "POST"),
    ("/api/digest-history/A001", "GET")
])
def test_endpoint_authentication(client, endpoint, method):
    """Test that endpoints require authentication"""
    # Try to access the endpoint without authentication
    if method == "GET":
        response = client.get(endpoint)
    else:
        response = client.post(endpoint, json={})
    
    # Should return 401 Unauthorized
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "not validate credentials" in response.json()["detail"]

def test_login_endpoint(client):
    """Test the login endpoint"""
    response = client.post(
        "/token",
        data={"username": "admin", "password": "password"}
    )
    
    # Should return 200 OK with an access token
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_endpoint_invalid_credentials(client):
    """Test the login endpoint with invalid credentials"""
    response = client.post(
        "/token",
        data={"username": "admin", "password": "wrong_password"}
    )
    
    # Should return 401 Unauthorized
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect username or password" in response.json()["detail"]

@patch('src.main.process_emails')
def test_api_process_emails(mock_process_emails, client, auth_headers, sample_email_data):
    """Test the process-emails endpoint"""
    # Mock the process_emails function
    mock_process_emails.return_value = {"A001": {"margin_call": []}}
    
    # Call the endpoint
    response = client.post(
        "/api/process-emails",
        json=sample_email_data.dict(),
        headers=auth_headers
    )
    
    # Should return 200 OK with the expected result
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"
    assert "Processed" in response.json()["message"]
    assert response.json()["data"] == {"A001": {"margin_call": []}}

@patch('src.main.process_emails')
def test_api_process_emails_error(mock_process_emails, client, auth_headers, sample_email_data):
    """Test error handling in the process-emails endpoint"""
    # Mock the process_emails function to raise an exception
    mock_process_emails.side_effect = Exception("Test error")
    
    # Call the endpoint
    response = client.post(
        "/api/process-emails",
        json=sample_email_data.dict(),
        headers=auth_headers
    )
    
    # Should return 500 Internal Server Error
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Test error" in response.json()["detail"]

@patch('src.main.build_digest')
@patch('src.main.generate_insights')
def test_api_generate_digests(mock_generate_insights, mock_build_digest, client, auth_headers, sample_advisor_digest):
    """Test the generate-digests endpoint"""
    # Mock the build_digest function
    mock_build_digest.return_value = sample_advisor_digest
    
    # Mock the generate_insights function
    mock_generate_insights.return_value = []
    
    # Create a simplified request payload to avoid recursion issues
    today_str = date.today().isoformat()
    payload = {
        "advisor_ids": ["A001"],
        "date": today_str,
        "include_ai_insights": True
    }
    
    # Call the endpoint
    response = client.post(
        "/api/generate-digests",
        json=payload,
        headers=auth_headers
    )
    
    # Should return 200 OK with the expected result
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"
    assert "Generated" in response.json()["message"]
    assert "digests" in response.json()["message"]

@patch('src.main.send_digest_email')
def test_api_send_digests(mock_send_digest_email, client, auth_headers, sample_advisor_digest):
    """Test the send-digests endpoint"""
    # Mock the send_digest_email function
    mock_send_digest_email.return_value = MagicMock(
        advisor_id="A001",
        advisor_email="john.smith@example.com",
        success=True,
        message="Email sent successfully"
    )
    
    # Call the endpoint
    response = client.post(
        "/api/send-digests",
        json=[sample_advisor_digest.dict()],
        headers=auth_headers
    )
    
    # Should return 200 OK with the expected result
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"
    assert "Sent 1 digest emails" in response.json()["message"]
    assert len(response.json()["data"]) == 1

def test_api_digest_history(client, auth_headers):
    """Test the digest-history endpoint"""
    # Call the endpoint
    response = client.get(
        "/api/digest-history/A001",
        headers=auth_headers
    )
    
    # Should return 200 OK with the expected result
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"
    assert "Retrieved digest history" in response.json()["message"]
    assert response.json()["data"]["advisor_id"] == "A001"
    assert len(response.json()["data"]["digests"]) == 2
