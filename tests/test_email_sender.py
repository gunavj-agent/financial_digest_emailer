import pytest
from unittest.mock import patch, MagicMock
import aiosmtplib
from src.email_sender import send_digest_email, _generate_html_content, _generate_fallback_html

@pytest.mark.asyncio
@patch('src.email_sender.aiosmtplib.send')
@patch('src.email_sender.SMTP_SERVER', 'smtp.example.com')
@patch('src.email_sender.SMTP_USERNAME', 'test_user')
@patch('src.email_sender.SMTP_PASSWORD', 'test_password')
async def test_send_digest_email_success(mock_send, sample_advisor_digest):
    """Test sending a digest email successfully"""
    # Mock the SMTP send function to return successfully
    mock_send.return_value = True
    
    # Send the digest email
    result = await send_digest_email(sample_advisor_digest)
    
    # Check that the SMTP send function was called
    mock_send.assert_called_once()
    
    # Check the result
    assert result.advisor_id == "A001"
    assert result.advisor_email == "john.smith@example.com"
    assert result.success == True
    assert "successfully" in result.message.lower()

@pytest.mark.asyncio
@patch('src.email_sender.aiosmtplib.send')
@patch('src.email_sender.SMTP_SERVER', 'smtp.example.com')
@patch('src.email_sender.SMTP_USERNAME', 'test_user')
@patch('src.email_sender.SMTP_PASSWORD', 'test_password')
async def test_send_digest_email_failure(mock_send, sample_advisor_digest):
    """Test handling a failure when sending a digest email"""
    # Mock the SMTP send function to raise an exception
    mock_send.side_effect = aiosmtplib.SMTPException("Connection failed")
    
    # Send the digest email
    result = await send_digest_email(sample_advisor_digest)
    
    # Check that the SMTP send function was called
    mock_send.assert_called_once()
    
    # Check the result
    assert result.advisor_id == "A001"
    assert result.advisor_email == "john.smith@example.com"
    assert result.success == False
    assert "error" in result.message.lower()
    assert "connection failed" in result.message.lower()

@pytest.mark.asyncio
@patch('src.email_sender.SMTP_SERVER', None)
async def test_send_digest_email_missing_config(sample_advisor_digest):
    """Test sending a digest email with missing SMTP configuration"""
    # Send the digest email
    result = await send_digest_email(sample_advisor_digest)
    
    # Check the result
    assert result.advisor_id == "A001"
    assert result.advisor_email == "john.smith@example.com"
    assert result.success == False
    assert "configuration" in result.message.lower()

@patch('src.email_sender.template_env.get_template')
def test_generate_html_content(mock_get_template, sample_advisor_digest):
    """Test generating HTML content for a digest email"""
    # Mock the template rendering
    mock_template = MagicMock()
    mock_template.render.return_value = "<html>Test HTML</html>"
    mock_get_template.return_value = mock_template
    
    # Generate the HTML content
    html = _generate_html_content(sample_advisor_digest)
    
    # Check that the template was rendered
    mock_template.render.assert_called_once()
    
    # Check the result
    assert html == "<html>Test HTML</html>"

@patch('src.email_sender.template_env.get_template')
def test_generate_html_content_template_error(mock_get_template, sample_advisor_digest):
    """Test generating HTML content with a template error"""
    # Mock the template rendering to raise an exception
    mock_get_template.side_effect = Exception("Template error")
    
    # Generate the HTML content
    html = _generate_html_content(sample_advisor_digest)
    
    # Check that the fallback HTML was generated
    assert "<html>" in html
    assert "Financial Digest for" in html
    assert "John Smith" in html
    assert "Alice Johnson" in html
    assert "Bob Williams" in html
