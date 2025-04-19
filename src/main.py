import os
import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from jose import JWTError, jwt

from .models import EmailData, DigestRequest, AdvisorDigest
from .email_processor import process_emails
from .digest_builder import build_digest
from .ai_insights import generate_insights
from .email_sender import send_digest_email

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/financial_digest.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("financial_digest")

# Initialize FastAPI app
app = FastAPI(
    title="Financial Digest Emailer",
    description="API for processing financial notifications and creating AI-enhanced digest emails",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "development_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Sample user database - In production, use a proper database
USERS_DB = {
    "admin": {
        "username": "admin",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        "disabled": False,
    }
}

# Auth models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

# Auth functions
def verify_password(plain_password, hashed_password):
    # In production, use proper password hashing
    return plain_password == "password"  # Simplified for example

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(USERS_DB, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Auth endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(USERS_DB, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# API endpoints
@app.get("/")
async def read_root():
    return {"message": "Financial Digest Emailer API", "version": "1.0.0"}

@app.post("/api/process-emails")
async def api_process_emails(
    email_data: EmailData,
    current_user: User = Depends(get_current_active_user)
):
    """
    Process incoming email notifications and organize them by recipient
    """
    try:
        result = process_emails(email_data)
        return {
            "status": "success",
            "message": f"Processed {len(email_data.emails)} emails for {len(result)} advisors",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error processing emails: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-digests")
async def api_generate_digests(
    request: DigestRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate daily digests for specified advisors
    """
    try:
        digests = []
        for advisor_id in request.advisor_ids:
            # Build the digest for this advisor
            digest = build_digest(advisor_id, request.date)
            
            # Add AI insights if requested
            if request.include_ai_insights:
                insights = generate_insights(digest)
                digest.ai_insights = insights
            
            digests.append(digest)
            
        return {
            "status": "success",
            "message": f"Generated {len(digests)} digests",
            "data": digests
        }
    except Exception as e:
        logger.error(f"Error generating digests: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/send-digests")
async def api_send_digests(
    digests: List[AdvisorDigest],
    current_user: User = Depends(get_current_active_user)
):
    """
    Send generated digests to advisors via email
    """
    try:
        results = []
        for digest in digests:
            # Send the digest email
            result = await send_digest_email(digest)
            results.append(result)
            
        return {
            "status": "success",
            "message": f"Sent {len(results)} digest emails",
            "data": results
        }
    except Exception as e:
        logger.error(f"Error sending digests: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/digest-history/{advisor_id}")
async def api_digest_history(
    advisor_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve digest history for a specific advisor
    """
    try:
        # In a real implementation, this would query a database
        # For this example, we'll return a placeholder
        return {
            "status": "success",
            "message": f"Retrieved digest history for advisor {advisor_id}",
            "data": {
                "advisor_id": advisor_id,
                "digests": [
                    {
                        "date": "2025-04-17",
                        "sent_at": "2025-04-17T08:00:00Z",
                        "summary": "5 margin calls, 3 retirement contributions, 2 corporate actions"
                    },
                    {
                        "date": "2025-04-16",
                        "sent_at": "2025-04-16T08:00:00Z",
                        "summary": "2 margin calls, 4 retirement contributions, 1 corporate action"
                    }
                ]
            }
        }
    except Exception as e:
        logger.error(f"Error retrieving digest history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
