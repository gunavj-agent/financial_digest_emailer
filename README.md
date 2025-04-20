# Financial Digest Emailer

A system that processes multiple financial email notifications, organizes them by recipient (Financial Advisor), creates daily digest emails, and adds AI insights using Claude Sonnet.

## 🚀 Features

- **Multi-source Email Processing**: Handles various financial notification types:
  - Margin calls
  - Retirement contributions
  - Voluntary corporate actions
  - Outgoing account transfers
- **Recipient Organization**: Groups notifications by Financial Advisor
- **Daily Digest Creation**: Generates consolidated daily email digests
- **AI-powered Insights**: Uses Claude to provide intelligent summaries and recommendations
- **Executive Summaries**: AI-generated concise overviews of the most important information
- **Email Delivery**: Sends formatted HTML emails to recipients
- **Secure Authentication**: API endpoints protected with authentication

## 📋 Architecture

### System Overview

```mermaid
flowchart TD
    A[Email Data Sources<br/>(JSON, Margin Calls, Retirement,<br/>Corp. Actions, Outgoing Transfers)] -->|Batch Upload/API| B[Email Processor<br/>(email_processor.py)]
    B --> C[Recipient Grouper<br/>(by Advisor)]
    C --> D[Digest Builder<br/>(digest_builder.py)]
    
    subgraph "AI Processing"
        E1[AI Executive Summary<br/>(generate_executive_summary)]
        E2[AI Insights<br/>(generate_insights)]
    end
    
    D --> E1
    D --> E2
    
    E1 --> F[Email Formatter<br/>(Jinja2 HTML Template)]
    E2 --> F
    
    F --> G[Email Sender<br/>(email_sender.py)]
    G -->|SMTP| H[Email Server<br/>(Gmail: smtp.gmail.com)]
    H --> I[Advisor Inbox<br/>(Financial Advisor)]

    subgraph "Environment & Storage"
        J1[.env File<br/>(API Keys, SMTP Credentials)]
        J2[Storage<br/>(Processed Data,<br/>Digest History)]
        J3[Templates<br/>(base_digest.html)]
    end
    
    J1 -.->|Config| B
    J1 -.->|Config| E1
    J1 -.->|Config| E2
    J1 -.->|Config| G
    
    D -- Save/Load --> J2
    F -- Use Template --> J3
    
    classDef newFeature fill:#f9f,stroke:#333,stroke-width:2px;
    class E1,A newFeature;
```

*Note: Highlighted in pink are the new features added to the system.*

## 🔧 Setup & Installation

### Prerequisites
- Python 3.9+
- Anthropic API Key (for Claude)
- SMTP server access for sending emails (configured for Gmail by default)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd financial_digest_emailer
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your configuration:
```
ANTHROPIC_API_KEY=your_api_key_here
SMTP_SERVER=your_smtp_server
SMTP_PORT=587
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
EMAIL_FROM=digest@yourdomain.com
```

## 🚀 Running the Application

Start the API server:
```bash
python -m uvicorn src.main:app --reload
```

The API will be available at: http://127.0.0.1:8000

## 📊 Key Endpoints

- **API Documentation**: http://127.0.0.1:8000/docs
- **Process Emails**: POST /api/process-emails
- **Generate Digests**: POST /api/generate-digests
- **Send Digests**: POST /api/send-digests
- **View Digest History**: GET /api/digest-history/{advisor_id}

## 🔍 How It Works

### Email Processing Flow

1. **Data Ingestion**:
   - System receives JSON data containing email notifications
   - Data is validated and normalized

2. **Recipient Grouping**:
   - Notifications are organized by recipient (Financial Advisor)
   - Each advisor's notifications are categorized by type

3. **Digest Creation**:
   - For each advisor, a daily digest is compiled
   - Notifications are formatted according to type-specific templates
   - Priority notifications are highlighted

4. **AI Enhancement**:
   - Claude Sonnet analyzes the digest content
   - Generates personalized insights and recommendations
   - Identifies patterns and potential action items

5. **Email Delivery**:
   - HTML email is generated using templates
   - Sent to the advisor's email address
   - Delivery status is tracked

## 📁 Project Structure

```
financial_digest_emailer/
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
├── src/
│   ├── main.py           # FastAPI application and endpoints
│   ├── email_processor.py # Email processing logic
│   ├── digest_builder.py  # Digest creation functionality
│   ├── ai_insights.py     # Claude integration for insights
│   ├── email_sender.py    # Email delivery functionality
│   └── models.py          # Pydantic data models
├── templates/
│   ├── base_digest.html   # Base HTML template
│   ├── margin_call.html   # Margin call section template
│   ├── retirement.html    # Retirement section template
│   └── corporate.html     # Corporate action section template
├── data/                  # Sample data and storage
└── logs/                  # Application logs
```

## 🔒 Security Considerations

- API endpoints are secured with authentication
- Sensitive data is not stored persistently
- Email credentials are stored securely in environment variables
- HTTPS is recommended for production deployments

## 📄 License

[MIT License](LICENSE)
