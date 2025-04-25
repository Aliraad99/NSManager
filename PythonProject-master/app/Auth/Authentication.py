from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from jose import jwt, JWTError
from fastapi import HTTPException, Depends
from app.Auth.Authentication import SECRET_KEY, ALGORITHM  # Ensure these are defined in your Authentication module

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
Http_Bearer = HTTPBearer()

credentials_exception = HTTPException(
        detail="Could not validate credentials",
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"}
    )

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def DecodeToken(token: str):
    if not token.startswith("Bearer "):
        raise credentials_exception 
    token = token[len("Bearer "):]
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    Email: str = payload.get("Email")
    
    if Email is None or Email == "":
        raise credentials_exception  
    return Email

def get_current_user(token: str):
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract user information from the token payload
        email: str = payload.get("Email")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Optionally, you can return the entire payload or specific user details
        return payload  # Return the decoded payload (e.g., user details)
    
    except JWTError:
        # Raise an exception if the token is invalid or expired
        raise HTTPException(status_code=401, detail="Invalid or expired token")