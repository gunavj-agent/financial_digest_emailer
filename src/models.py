from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime, date
from enum import Enum

class EmailType(str, Enum):
    MARGIN_CALL = "margin_call"
    RETIREMENT_CONTRIBUTION = "retirement_contribution"
    CORPORATE_ACTION = "corporate_action"
    OUTGOING_ACCOUNT_TRANSFER = "outgoing account transfer"

class EmailNotification(BaseModel):
    """Model for a single email notification"""
    id: str
    type: EmailType
    subject: str
    body: str
    recipient_id: str  # Financial Advisor ID
    recipient_email: EmailStr
    client_id: str
    client_name: str
    timestamp: datetime
    metadata: Dict[str, Any] = {}
    priority: int = Field(1, ge=1, le=10)  # 1-10 priority level (10 is highest)

class EmailData(BaseModel):
    """Model for the incoming batch of email notifications"""
    emails: List[EmailNotification]

class MarginCall(BaseModel):
    """Model for margin call notifications"""
    id: str
    client_id: str
    client_name: str
    account_number: str
    call_amount: float
    due_date: date
    current_margin_percentage: float
    required_margin_percentage: float
    timestamp: datetime
    priority: int = 10  # Critical priority (Outgoing Account Transfer)

class RetirementContribution(BaseModel):
    """Model for retirement contribution notifications"""
    id: str
    client_id: str
    client_name: str
    account_number: str
    contribution_amount: float
    contribution_type: str  # e.g., "401k", "IRA", etc.
    tax_year: int
    timestamp: datetime
    priority: int = 4  # Medium priority (Retirement Contribution)

class CorporateAction(BaseModel):
    """Model for voluntary corporate action notifications"""
    id: str
    client_id: str
    client_name: str
    account_number: str
    security_id: str
    security_name: str
    action_type: str  # e.g., "stock split", "merger", "tender offer"
    deadline_date: date
    description: str
    timestamp: datetime
    priority: int = 6  # Medium-high priority (Corporate Action)

class OutgoingAccountTransfer(BaseModel):
    """Model for outgoing account transfer notifications"""
    id: str
    client_id: str
    client_name: str
    account_number: str
    account_type: str
    net_amount: float
    gross_amount: float
    transfer_type: str  # e.g., "ACH", "Wire", etc.
    entry_date: date
    payment_date: date
    status: str
    description: str
    timestamp: datetime
    priority: int = 10  # Critical priority (Outgoing Account Transfer)

class AIInsight(BaseModel):
    """Model for AI-generated insights"""
    title: str
    content: str
    recommendation: Optional[str] = None
    related_clients: List[str] = []
    priority: int = Field(1, ge=1, le=10)

class AdvisorDigest(BaseModel):
    """Model for a complete advisor digest"""
    advisor_id: str
    advisor_name: str
    advisor_email: EmailStr
    date: date
    margin_calls: List[MarginCall] = []
    retirement_contributions: List[RetirementContribution] = []
    corporate_actions: List[CorporateAction] = []
    outgoing_account_transfers: List[OutgoingAccountTransfer] = []
    ai_insights: List[AIInsight] = []
    summary_stats: Dict[str, Any] = {}
    
    @property
    def has_high_priority(self) -> bool:
        """Check if digest contains any high priority items"""
        for call in self.margin_calls:
            if call.priority >= 4:
                return True
        for action in self.corporate_actions:
            if action.priority >= 4:
                return True
        for transfer in self.outgoing_account_transfers:
            if transfer.priority >= 4:
                return True
        return False

class DigestRequest(BaseModel):
    """Model for requesting digest generation"""
    advisor_ids: List[str]
    date: Optional[date] = None
    include_ai_insights: bool = True
    
    @validator('date', pre=True, always=True)
    def set_date_now(cls, v):
        return v or datetime.now().date()

class EmailDeliveryResult(BaseModel):
    """Model for email delivery result"""
    advisor_id: str
    advisor_email: EmailStr
    success: bool
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
