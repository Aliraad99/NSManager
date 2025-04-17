from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.Repositories import UserRepos as user_repo
from app.Schemas.ResponseMessage import ResponseMessage
from app.Auth.LoginModel import LoginModel
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.Auth.Authentication import oauth2_scheme, get_current_user, create_access_token
from passlib.context import CryptContext

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/Login/")
async def Login(form_data: LoginModel = Depends(), db: AsyncSession = Depends(get_db)):
    user = await user_repo.GetUserByEmail(db,form_data.UserEmail)
    if user is None or not pwd_context.verify(form_data.UserPassword, user.Password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"Email": user.Email, "Id": user.Id, "FirstName": user.FirstName, "LastName": user.LastName, "Password":user.Password})
    return {"access_token": access_token, "token_type": "bearer"}