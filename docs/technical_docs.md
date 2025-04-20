# Financial Digest Emailer - Technical Documentation

## System Architecture

The Financial Digest Emailer is designed with a modular architecture that processes financial notifications, groups them by advisor, generates AI insights, and delivers personalized digest emails.

### Core Components

1. **Email Processor** (`src/email_processor.py`)
   - Parses email notifications from various sources
   - Converts generic notifications to typed models
   - Groups notifications by recipient (Financial Advisor)

2. **Digest Builder** (`src/digest_builder.py`)
   - Builds comprehensive digests for each advisor
   - Generates summary statistics
   - Organizes notifications by type and priority

3. **AI Insights** (`src/ai_insights.py`)
   - Integrates with Anthropic's Claude API
   - Generates executive summaries
   - Provides actionable insights based on notification data
   - Implements privacy protection through data masking

4. **Data Masking** (`src/data_masking.py`)
   - Protects sensitive client information
   - Masks account numbers, client IDs, and personal information
   - Ensures privacy when interacting with external AI services

5. **Email Sender** (`src/email_sender.py`)
   - Formats digest content into HTML emails
   - Delivers emails via SMTP
   - Handles delivery errors and retries

## Data Privacy & Security

### Data Masking Implementation

The system implements comprehensive data masking to protect sensitive client information before sending it to external AI services:

#### Types of Masked Data

- **Account Numbers**: Masked to show only last 4 digits (e.g., "XXXXXX3456")
- **Client IDs**: Hashed to provide consistent but anonymized references
- **Client Names**: Partially masked to show only first initial and last name (e.g., "A. Johnson")
- **Email Addresses**: Username portion masked while preserving domain (e.g., "j***e@example.com")

#### Masking Process

1. The `mask_sensitive_data()` function recursively processes all data structures
2. Sensitive fields are identified based on field names and patterns
3. Different masking strategies are applied based on data type
4. Masked data preserves structure and meaning while protecting PII

#### Code Example

```python
# Example of how account numbers are masked
def mask_account_number(account_number: str) -> str:
    """Mask an account number, showing only last 4 digits."""
    if not account_number:
        return account_number
    
    if len(account_number) <= 4:
        return "****"
    
    masked = "X" * (len(account_number) - 4) + account_number[-4:]
    return masked
```

### Security Considerations

- API keys and credentials are stored in environment variables
- Sensitive data is masked before being sent to external services
- SMTP communication uses TLS encryption
- Error handling prevents exposure of sensitive information in logs

## Configuration

The system is configured through environment variables, typically stored in a `.env` file:

```
# Anthropic API key for Claude
ANTHROPIC_API_KEY=your_api_key_here

# SMTP Configuration
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password
EMAIL_FROM=sender@example.com

# Application settings
DEBUG=True
LOG_LEVEL=INFO
```

## AI Integration

### Executive Summary Generation

The system generates concise executive summaries for financial advisors by:

1. Masking sensitive data in the digest
2. Creating a structured prompt with key statistics and priorities
3. Sending the prompt to Claude API
4. Processing and formatting the response

### AI Insights

AI insights are generated to provide actionable recommendations:

1. Analyzing patterns across different notification types
2. Identifying high-priority items requiring attention
3. Suggesting specific actions for financial advisors
4. Highlighting potential risks or compliance issues

## Testing

The system includes comprehensive tests for all components:

- Unit tests for individual functions
- Integration tests for component interactions
- End-to-end tests for the complete workflow

## Deployment

The system can be deployed as:

1. A scheduled job that runs daily
2. A microservice that processes notifications in real-time
3. An API that generates digests on demand

## Future Enhancements

Planned enhancements include:

1. Additional notification types
2. More sophisticated AI insights
3. Interactive digest elements
4. Enhanced data visualization
5. Multi-channel delivery options
