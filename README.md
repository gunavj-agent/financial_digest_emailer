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

```
+-----------------------------+        +------------------------+        +------------------------+
|      Data Sources           |        |     Core System        |        |      Delivery          |
+-----------------------------+        +------------------------+        +------------------------+
| - JSON Email Data           |        | - Email Processor      |        | - Email Formatter      |
| - Margin Calls              | -----> | - Recipient Grouper    | -----> | - HTML Templates       |
| - Retirement Contributions  |        | - Digest Builder       |        | - SMTP Delivery        |
| - Corporate Actions         |        +------------------------+        +------------------------+
| - Outgoing Account Transfers|                 |                                  |
+-----------------------------+                 v                                  v
                                    +------------------------+        +------------------------+
                                    |    AI Processing*      |        |       Recipients       |
                                    +------------------------+        +------------------------+
                                    | - Executive Summary*   | -----> | - Financial Advisors   |
                                    | - AI Insights          |        |                        |
                                    +------------------------+        +------------------------+
                                                |
                                                v
                                    +------------------------+
                                    |  Environment & Storage |
                                    +------------------------+
                                    | - .env Configuration   |
                                    | - Processed Data       |
                                    | - Email Templates      |
                                    +------------------------+
```

*Note: Components marked with * are new features added to the system.



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
