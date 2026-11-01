from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from sqlalchemy.engine import Connection

from dependencies import get_db_connection
from queries import auth_queries as q  

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBasic()
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_user(
    credentials: HTTPBasicCredentials = Depends(security), 
    conn: Connection = Depends(get_db_connection)
) -> dict:
    """Dependency to protect routes. Returns the user dict if valid."""
    user = q.get_user_by_username(conn, credentials.username)
    
    # Check if user exists AND password matches the hash
    if not user or not pwd.verify(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    if not user["is_active"]:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user