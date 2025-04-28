import os
import logging
import json
from typing import List, Dict, Any
from datetime import datetime

from anthropic import Anthropic

from src.models import AdvisorDigest, AIInsight
from src.data_masking import mask_sensitive_data

logger = logging.getLogger("financial_digest")

# Initialize client variable
client = None

def _initialize_client():
    """Initialize the Anthropic client with API key from environment variables"""
    global client
    
    # Get Anthropic API key from environment variable
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    
    # Log API key status
    if api_key:
        logger.info(f"Using Anthropic API key: {api_key[:10]}...")
        client = Anthropic(api_key=api_key)
        return True
    else:
        logger.warning("ANTHROPIC_API_KEY not set in environment variables")
        return False

def generate_executive_summary(digest: AdvisorDigest) -> str:
    """Generate an executive summary for the digest"""
    logger.info(f"Generating executive summary for advisor {digest.advisor_id}")
    
    # Initialize client if needed
    if not client and not _initialize_client():
        logger.warning("ANTHROPIC_API_KEY not set, skipping executive summary generation")
        return f"Daily digest for {digest.date} with {digest.summary_stats['total_notifications']} notifications requiring your attention."
    
    # Create a summary of the digest for AI processing
    digest_summary = _create_digest_summary(digest)
    # Note: digest_summary is already masked by _create_digest_summary
    
    # Create the prompt
    prompt = _create_executive_summary_prompt(digest.advisor_name, digest_summary)
        
    try:
        # Send the prompt to Claude
        message = client.messages.create(
            model="claude-3-opus-20240229",  # Try with this model first
            max_tokens=500,
            temperature=0.3,
            system="You are a professional financial advisor assistant that specializes in creating concise executive summaries.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
    except Exception as e:
        logger.warning(f"Error with first model attempt: {str(e)}. Trying with claude-3-haiku.")
        try:
            # Try with a different model
            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                temperature=0.3,
                system="You are a professional financial advisor assistant that specializes in creating concise executive summaries.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
        except Exception as e2:
            logger.error(f"Error generating executive summary: {str(e2)}")
            return f"Daily digest for {digest.date} with {digest.summary_stats['total_notifications']} notifications requiring your attention."
        
    # Extract the summary from the response
    summary = message.content[0].text
    logger.info(f"Generated executive summary for advisor {digest.advisor_id}")
    return summary
        
def generate_insights(digest: AdvisorDigest) -> List[AIInsight]:
    """Generate AI insights for the digest"""
    logger.info(f"Generating AI insights for advisor {digest.advisor_id}")
    
    # Initialize client if needed
    if not client and not _initialize_client():
        logger.warning("ANTHROPIC_API_KEY not set, skipping AI insights generation")
        return [
            AIInsight(
                title="High Priority Margin Calls",
                content="There are several high priority margin calls that require immediate attention.",
                recommendation="Contact clients with margin calls due in the next 48 hours.",
                related_clients=[call.client_name for call in digest.margin_calls if call.priority >= 2],
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
    
    # Create a summary of the digest for AI processing
    digest_summary = _create_digest_summary(digest)
    # Note: digest_summary is already masked by _create_digest_summary
    
    # Create the prompt
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
        
def _create_digest_summary(digest: AdvisorDigest) -> Dict[str, Any]:
    """Create a summary of the digest for AI processing"""
    summary = {
        "advisor_id": digest.advisor_id,
        "advisor_name": digest.advisor_name,
        "date": str(digest.date),
        "margin_calls": [
            {
                "client_id": call.client_id,
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
                "client_id": contrib.client_id,
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
                "client_id": action.client_id,
                "client_name": action.client_name,
                "account_number": action.account_number,
                "security_id": action.security_id,
                "security_name": action.security_name,
                "action_type": action.action_type,
                "deadline_date": str(action.deadline_date),
                "description": action.description,
                "priority": action.priority
            }
            for action in digest.corporate_actions
        ],
        "outgoing_account_transfers": [
            {
                "client_id": transfer.client_id,
                "client_name": transfer.client_name,
                "account_number": transfer.account_number,
                "account_type": transfer.account_type,
                "net_amount": transfer.net_amount,
                "gross_amount": transfer.gross_amount,
                "transfer_type": transfer.transfer_type,
                "entry_date": str(transfer.entry_date),
                "payment_date": str(transfer.payment_date),
                "status": transfer.status,
                "description": transfer.description,
                "priority": transfer.priority
            }
            for transfer in digest.outgoing_account_transfers
        ],
        "summary_stats": digest.summary_stats
    }
    
    # Mask sensitive data before returning
    masked_summary = mask_sensitive_data(summary)
    return masked_summary

def _create_executive_summary_prompt(advisor_name: str, digest_summary: Dict[str, Any]) -> str:
    """Create an enhanced prompt for generating a financial advisor's executive summary"""
    # Extract key metrics
    stats = digest_summary["summary_stats"]
    total_notifications = stats["total_notifications"]
    
    # Get total unique clients (calculated from all notification types)
    client_ids = set()
    for category in ["margin_calls", "retirement_contributions", "corporate_actions", "outgoing_account_transfers"]:
        for item in digest_summary[category]:
            if "client_id" in item:
                client_ids.add(item["client_id"])
    total_clients = len(client_ids)
    
    # Get highest priority item
    highest_priority = 0
    for category in ["margin_calls", "retirement_contributions", "corporate_actions", "outgoing_account_transfers"]:
        for item in digest_summary[category]:
            if "priority" in item and item["priority"] > highest_priority:
                highest_priority = item["priority"]
    
    # Prepare lists of upcoming deadlines
    upcoming_deadlines = []
    
    # Check for upcoming corporate action deadlines
    for action in digest_summary["corporate_actions"]:
        if "deadline_date" in action:
            upcoming_deadlines.append(f"{action['client_name']}'s {action['action_type']} for {action['security_name']} (due {action['deadline_date']})")
    
    # Check for upcoming margin call due dates
    for call in digest_summary["margin_calls"]:
        if "due_date" in call:
            upcoming_deadlines.append(f"{call['client_name']}'s margin call for ${call['call_amount']:,.2f} (due {call['due_date']})")
    
    # Limit to top 3 deadlines
    upcoming_deadlines = upcoming_deadlines[:3]
    
    prompt = f"""
    As a professional financial advisor assistant, create a concise yet comprehensive executive summary for {advisor_name}'s daily digest.

    CONTEXT:
    - You have {total_notifications} notifications across {total_clients} clients
    - The highest priority item is rated {highest_priority}/10
    - Key upcoming deadlines: {'; '.join(upcoming_deadlines) if upcoming_deadlines else 'None'}

    DIGEST DATA:
    {json.dumps(digest_summary, indent=2)}

    INSTRUCTIONS:
    1. Begin with a professional greeting addressing {advisor_name} directly
    2. Provide a concise 2-3 sentence overview of today's key priorities
    3. Highlight the most urgent items requiring immediate attention (next 48 hours)
    4. Mention any significant financial trends or patterns across clients
    5. End with a clear, actionable next step recommendation

    REQUIREMENTS:
    - Keep the summary under 200 words
    - Use professional, clear financial language
    - Focus on actionable insights rather than just listing data
    - Prioritize information based on urgency and financial impact
    - Maintain a confident, authoritative tone
    - Do not mention that this summary was AI-generated

    NOTE: All sensitive client information has been masked for privacy and security. Do not attempt to reconstruct or infer actual identities or account details.
    """
    return prompt

def _create_claude_prompt(advisor_name: str, digest_summary: Dict[str, Any]) -> str:
    """Create the prompt for Claude"""
    prompt = f"""
    You are a professional financial analyst assistant for {advisor_name}. Analyze this financial digest and generate actionable insights.
    
    DIGEST DATA (JSON):
    {json.dumps(digest_summary, indent=2)}
    
    ANALYSIS REQUIREMENTS:
    1. Identify 3-5 high-value insights from this data that would be most valuable to a financial advisor
    2. Prioritize time-sensitive issues requiring immediate action (next 48-72 hours)
    3. Focus on high-risk areas: margin calls, outgoing transfers, and approaching deadlines
    4. Detect patterns across client portfolios that may indicate market trends or systemic issues
    5. Identify compliance risks or regulatory concerns that require attention
    
    INSIGHT CATEGORIES TO INCLUDE:
    - URGENT: At least one insight about immediate action items (next 24-48 hours)
    - TRANSFERS: If outgoing account transfers exist (especially with status "Next 5 business days - Review Required" or high-priority), provide specific analysis
    - MARGIN CALLS: Analyze margin call patterns, risk levels, and recommended interventions
    - CLIENT PATTERNS: Identify behavioral or financial patterns across multiple clients
    - OPPORTUNITY: Highlight potential revenue or relationship-building opportunities
    
    PATTERN OBSERVATIONS TO CONSIDER:
    - CONCENTRATION RISK: Identify clients with multiple high-priority notifications across different categories
    - TIMING PATTERNS: Note if multiple deadlines/actions cluster around specific dates
    - RECURRING ISSUES: Flag clients with repeated margin calls or similar issues over time
    - PORTFOLIO VULNERABILITY: Identify clients with both margin calls and outgoing transfers
    - LIQUIDITY CONCERNS: Note patterns of outgoing transfers that may impact account liquidity
    - RETIREMENT PLANNING GAPS: Identify clients with retirement contributions below optimal levels
    - CORPORATE ACTION IMPACT: Assess how corporate actions might affect overall client portfolios
    - SEASONAL TRENDS: Note if current activity aligns with typical seasonal financial patterns
    - COMPLIANCE RED FLAGS: Identify patterns that may indicate regulatory or compliance risks
    
    FORMAT INSTRUCTIONS:
    Return ONLY a JSON array with 3-5 insights using this exact structure:
    [
      {{
        "title": "Clear, specific insight title (5-8 words)",
        "content": "Detailed explanation with specific data points and analysis (2-4 sentences)",
        "recommendation": "Precise, actionable next step the advisor should take (1-2 sentences)",
        "related_clients": ["List of affected client names"],
        "priority": priority_level (1-10, with 10 being highest)
      }},
      ...
    ]
    
    SECURITY NOTICE:
    All sensitive client information has been masked for privacy and security. Do not attempt to reconstruct or infer actual identities, account numbers or other sensitive data. Your analysis must maintain client confidentiality.
    
    Return only the properly formatted JSON array with no additional text.
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
