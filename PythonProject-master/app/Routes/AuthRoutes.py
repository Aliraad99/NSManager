from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.Repositories import UserRepos as user_repo
from app.Schemas.ResponseMessage import ResponseMessage
from app.Auth.LoginModel import LoginModel
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from app.Auth.Authentication import oauth2_scheme, get_current_user, create_access_token
from passlib.context import CryptContext
from fastapi.responses import JSONResponse


router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/Login/")
async def Login(form_data: LoginModel, db: AsyncSession = Depends(get_db)):
    # Fetch the user by email
    user = await user_repo.GetUserByEmail(db, form_data.UserEmail)
    # Verify the user exists and the password is correct
    if user is None or not pwd_context.verify(form_data.UserPassword, user.Password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Create the access token
    access_token = create_access_token(data={
        "Email": user.Email,
        "Id": user.Id,
        "FirstName": user.FirstName,
        "LastName": user.LastName
    })
    
    # Set the token as an HTTP-only cookie
    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
    key="access_token",
    value=access_token,
    httponly=True,
    secure=True,    # Use HTTPS in production
    samesite="Lax", # Prevent CSRF in most cases
    path="/"  # Prevent CSRF in most cases
    )
    return response




@router.post("/logout")
async def logout():
    print("Logout endpoint called")  # Debug log
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie(
    key="access_token",
    path="/",          # Matches the path set in set_cookie
    httponly=True,     # Matches the httponly attribute
    secure=True,       # Matches the secure attribute
    samesite="Lax" 
    )
    print("Cookie deletion attempted")  # Debug log
    return response