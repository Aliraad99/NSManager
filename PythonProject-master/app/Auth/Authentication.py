from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

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

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(Http_Bearer)):
    try:
        token = credentials.credentials
        return DecodeToken(token)
    except JWTError as e:
        raise credentials_exception from e
