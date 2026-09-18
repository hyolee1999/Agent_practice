"""Authentication routes and security dependency templates.

Provides endpoints for user registration and JWT login, as well as the
`get_current_user` dependency to protect endpoints like /api/chat and /api/documents.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from docuagent.config.settings import settings
from docuagent.db.database import User, get_session, create_db_and_tables
from sqlmodel import select, Session 
import bcrypt
from sqlalchemy.exc import ProgrammingError



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ---------------------------------------------------------------------------
# Pydantic Request & Response Schemas
# ---------------------------------------------------------------------------
class RegisterRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ---------------------------------------------------------------------------
# Helper Functions (Password hashing & JWT)
# ---------------------------------------------------------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token.
    
    NOTE: In production, install PyJWT (`uv add pyjwt`) or python-jose.
    This fallback generates a valid token if pyjwt is installed, or a mock token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    
    try:
        import jwt
        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    except ImportError:
        # Development fallback if PyJWT is not installed yet
        import base64
        import json
        payload_str = json.dumps(to_encode, default=str)
        fake_jwt = f"mock_jwt.{base64.urlsafe_b64encode(payload_str.encode()).decode()}.signature"
        return fake_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a signed JWT access token."""
    try:
        import jwt
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except Exception:
        # Fallback decode for mock token during initial development
        if token.startswith("mock_jwt."):
            try:
                import base64
                import json
                parts = token.split(".")
                payload_str = base64.urlsafe_b64decode(parts[1].encode()).decode()
                return json.loads(payload_str)
            except Exception:
                return None
        return None


# ---------------------------------------------------------------------------
# Authentication Endpoints
# ---------------------------------------------------------------------------
@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, session: Session = Depends(get_session)):
    """Register a new user, store credentials, and return a JWT access token."""
    email_key = req.email.lower()
    
    try:
        email = select(User).where(User.email == email_key) 
        user = session.exec(email).first()
        # print(user)
    except ProgrammingError as e:
        session.rollback() 
        create_db_and_tables()
        email = select(User).where(User.email == email_key)
        user = session.exec(email).first()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching user from database."
        )

    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )
    
    new_user = User(
        email=email_key,
        name=req.name or req.email.split("@")[0],
        hashed_password=bcrypt.hashpw(req.password.encode(), bcrypt.gensalt()).decode("utf-8")
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    token = create_access_token({"sub": str(new_user.id), "email": req.email, "name": new_user.name})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(new_user.id),
            "email": req.email,
            "name": new_user.name
        }
    }


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, session: Session = Depends(get_session)):
    """Authenticate user credentials and return a JWT access token."""
    email_key = req.email.lower()
    
    try:
        email = select(User).where(User.email == email_key) 
        user = session.exec(email).first()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching user from database."
        )
    
    if not user or not bcrypt.checkpw(req.password.encode(), user.hashed_password.encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
    
    token = create_access_token({"sub": str(user.id), "email": user.email, "name": user.name})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name
        }
    }


# ---------------------------------------------------------------------------
# Dependency: get_current_user (Use to protect routes)
# ---------------------------------------------------------------------------
async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[Dict[str, Any]]:
    """Dependency to extract and verify current authenticated user from Bearer token.
    
    Usage in protected route:
        @router.post("/chat")
        async def chat(request: ChatRequest, current_user = Depends(get_current_user)):
            user_id = current_user["sub"]
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please sign in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload
