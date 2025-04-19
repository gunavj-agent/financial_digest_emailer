import pytest
from unittest.mock import patch, MagicMock
from src.ai_insights import generate_insights, _create_digest_summary, _parse_claude_response
from src.models import AIInsight

@pytest.fixture
def mock_anthropic_response():
    """Mock response from Anthropic API"""
    mock_response = MagicMock()
    mock_response.content = [
        MagicMock(
            text='''
            [
              {
                "title": "High Priority Margin Calls",
                "content": "There are several high priority margin calls that require immediate attention.",
                "recommendation": "Contact clients with margin calls due in the next 48 hours.",
                "related_clients": ["Alice Johnson"],
                "priority": 5
              },
              {
                "title": "Retirement Contribution Trends",
                "content": "Several clients are making maximum IRA contributions for the tax year.",
                "recommendation": "Review retirement planning strategies with these clients.",
                "related_clients": ["Bob Williams"],
                "priority": 3
              }
            ]
            '''
        )
    ]
    return mock_response

def test_create_digest_summary(sample_advisor_digest):
    """Test creating a structured summary of a digest for Claude"""
    summary = _create_digest_summary(sample_advisor_digest)
    
    # Check that the summary contains the expected sections
    assert "advisor" in summary
    assert "margin_calls" in summary
    assert "retirement_contributions" in summary
    assert "corporate_actions" in summary
    assert "summary_stats" in summary
    
    # Check advisor info
    assert summary["advisor"]["id"] == "A001"
    assert summary["advisor"]["name"] == "John Smith"
    
    # Check margin calls
    assert len(summary["margin_calls"]) == 1
    assert summary["margin_calls"][0]["client_name"] == "Alice Johnson"
    assert summary["margin_calls"][0]["call_amount"] == 5000.00
    
    # Check retirement contributions
    assert len(summary["retirement_contributions"]) == 1
    assert summary["retirement_contributions"][0]["client_name"] == "Bob Williams"
    assert summary["retirement_contributions"][0]["contribution_amount"] == 6000.00

def test_parse_claude_response(mock_anthropic_response):
    """Test parsing Claude's response into AIInsight objects"""
    insights = _parse_claude_response(mock_anthropic_response.content[0].text)
    
    # Check that we got the expected number of insights
    assert len(insights) == 2
    
    # Check the first insight
    assert insights[0].title == "High Priority Margin Calls"
    assert "immediate attention" in insights[0].content
    assert "Contact clients" in insights[0].recommendation
    assert "Alice Johnson" in insights[0].related_clients
    assert insights[0].priority == 5
    
    # Check the second insight
    assert insights[1].title == "Retirement Contribution Trends"
    assert "maximum IRA contributions" in insights[1].content
    assert "Review retirement planning" in insights[1].recommendation
    assert "Bob Williams" in insights[1].related_clients
    assert insights[1].priority == 3

@patch('src.ai_insights.client.messages.create')
def test_generate_insights_with_api_key(mock_create, sample_advisor_digest, mock_anthropic_response):
    """Test generating insights with a valid API key"""
    # Mock the Anthropic API response
    mock_create.return_value = mock_anthropic_response
    
    # Mock the environment variable
    with patch('src.ai_insights.ANTHROPIC_API_KEY', 'test_api_key'):
        insights = generate_insights(sample_advisor_digest)
        
        # Check that the API was called
        mock_create.assert_called_once()
        
        # Check that we got insights back
        assert len(insights) == 2
        assert insights[0].title == "High Priority Margin Calls"
        assert insights[1].title == "Retirement Contribution Trends"

@patch('src.ai_insights.ANTHROPIC_API_KEY', None)
def test_generate_insights_without_api_key(sample_advisor_digest):
    """Test generating insights without an API key"""
    insights = generate_insights(sample_advisor_digest)
    
    # Should return an empty list when no API key is available
    assert insights == []

def test_parse_claude_response_invalid_json():
    """Test parsing an invalid JSON response from Claude"""
    invalid_response = "This is not valid JSON"
    insights = _parse_claude_response(invalid_response)
    
    # Should return an empty list for invalid JSON
    assert insights == []
