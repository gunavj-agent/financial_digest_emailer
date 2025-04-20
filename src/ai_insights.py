import os
import logging
import json
from typing import List, Dict, Any
import anthropic

from .models import AdvisorDigest, AIInsight

logger = logging.getLogger("financial_digest")

# Get Anthropic API key from environment variable
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Log API key status
if ANTHROPIC_API_KEY:
    logger.info(f"Using Anthropic API key: {ANTHROPIC_API_KEY[:10]}...")
else:
    logger.warning("ANTHROPIC_API_KEY not set in environment variables")
    
# Initialize client with API key
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def generate_insights(digest: AdvisorDigest) -> List[AIInsight]:
    """
    Generate AI insights for a digest using Claude Sonnet
    
    Args:
        digest: The advisor digest to analyze
        
    Returns:
        List of AIInsight objects
    """
    if not ANTHROPIC_API_KEY:
        logger.warning("ANTHROPIC_API_KEY not set, skipping AI insights generation")
        return []
    
    logger.info(f"Generating AI insights for advisor {digest.advisor_id}")
    
    try:
        # Create a structured digest summary for Claude
        digest_summary = _create_digest_summary(digest)
        
        # Create the prompt for Claude
        prompt = _create_claude_prompt(digest.advisor_name, digest_summary)
        
        # Call Claude Sonnet
        try:
            # Use a valid Claude model name
            response = client.messages.create(
                model="claude-3-opus-20240229",  # Try with a valid model
                max_tokens=2000,
                temperature=0.3,
                system="You are a financial advisor assistant. Analyze the financial digest data and provide valuable insights and recommendations.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
        except Exception as e:
            logger.warning(f"Error with first model attempt: {str(e)}. Trying with claude-3-haiku.")
            try:
                response = client.messages.create(
                    model="claude-3-haiku-20240307",  # Fallback to another model
                    max_tokens=2000,
                    temperature=0.3,
                    system="You are a financial advisor assistant. Analyze the financial digest data and provide valuable insights and recommendations.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
            except Exception as e2:
                logger.error(f"Error with second model attempt: {str(e2)}. Generating generic insights.")
                # Return generic insights if API calls fail
                return [
                    AIInsight(
                        title="High Priority Margin Calls",
                        content="There are several high priority margin calls that require immediate attention.",
                        recommendation="Contact clients with margin calls due in the next 48 hours.",
                        related_clients=[call.client_name for call in digest.margin_calls if call.priority >= 4],
                        priority=5
                    ),
                    AIInsight(
                        title="Retirement Contribution Summary",
                        content="Several clients have made retirement contributions that may have tax implications.",
                        recommendation="Review retirement planning strategies with these clients.",
                        related_clients=[contrib.client_name for contrib in digest.retirement_contributions],
                        priority=3
                    )
                ]
        
        # Process Claude's response
        insights = _parse_claude_response(response.content[0].text)
        
        logger.info(f"Generated {len(insights)} AI insights for advisor {digest.advisor_id}")
        return insights
        
    except Exception as e:
        logger.error(f"Error generating AI insights: {str(e)}")
        return []

def _create_digest_summary(digest: AdvisorDigest) -> Dict[str, Any]:
    """Create a structured summary of the digest for Claude"""
    summary = {
        "advisor": {
            "id": digest.advisor_id,
            "name": digest.advisor_name
        },
        "date": str(digest.date),
        "margin_calls": [
            {
                "client_name": call.client_name,
                "account_number": call.account_number,
                "call_amount": call.call_amount,
                "due_date": str(call.due_date),
                "current_margin_percentage": call.current_margin_percentage,
                "required_margin_percentage": call.required_margin_percentage,
                "priority": call.priority
            }
            for call in digest.margin_calls
        ],
        "retirement_contributions": [
            {
                "client_name": contrib.client_name,
                "account_number": contrib.account_number,
                "contribution_amount": contrib.contribution_amount,
                "contribution_type": contrib.contribution_type,
                "tax_year": contrib.tax_year,
                "priority": contrib.priority
            }
            for contrib in digest.retirement_contributions
        ],
        "corporate_actions": [
            {
                "client_name": action.client_name,
                "account_number": action.account_number,
                "security_name": action.security_name,
                "action_type": action.action_type,
                "deadline_date": str(action.deadline_date),
                "description": action.description,
                "priority": action.priority
            }
            for action in digest.corporate_actions
        ],
        "summary_stats": digest.summary_stats
    }
    
    return summary

def _create_claude_prompt(advisor_name: str, digest_summary: Dict[str, Any]) -> str:
    """Create the prompt for Claude"""
    prompt = f"""
    Hello! I need your help analyzing a financial digest for advisor {advisor_name}.
    
    Here's the digest data in JSON format:
    
    {json.dumps(digest_summary, indent=2)}
    
    Based on this data, please provide:
    
    1. 2-3 key insights about the advisor's clients and their financial situations
    2. Specific recommendations for the advisor to take action on
    3. Any patterns or trends you notice across the different notification types
    4. Highlight any potential risks or compliance issues and suggest ways to address them.
5. Support your insights with specific numbers or trends from the data whenever possible.
6. Write each insight and recommendation clearly and concisely.
    
    Format your response as a JSON array with the following structure for each insight:
    
    [
      {{
        "title": "Brief title of the insight",
        "content": "Detailed explanation of the insight",
        "recommendation": "Specific action the advisor should take",
        "related_clients": ["List of client names this relates to"],
        "priority": priority_level (1-5, with 5 being highest)
      }},
      ...
    ]
    
    Only return the JSON array, nothing else.
    """
    
    return prompt

def _parse_claude_response(response_text: str) -> List[AIInsight]:
    """Parse Claude's response into AIInsight objects"""
    try:
        # Extract JSON from response (in case Claude adds any extra text)
        json_start = response_text.find('[')
        json_end = response_text.rfind(']') + 1
        
        if json_start == -1 or json_end == 0:
            logger.warning("Could not find JSON array in Claude response")
            return []
        
        json_str = response_text[json_start:json_end]
        insights_data = json.loads(json_str)
        
        # Convert to AIInsight objects
        insights = []
        for insight_data in insights_data:
            insight = AIInsight(
                title=insight_data.get("title", "Untitled Insight"),
                content=insight_data.get("content", ""),
                recommendation=insight_data.get("recommendation"),
                related_clients=insight_data.get("related_clients", []),
                priority=insight_data.get("priority", 3)
            )
            insights.append(insight)
        
        return insights
    
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing Claude response as JSON: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Error processing Claude response: {str(e)}")
        return []
