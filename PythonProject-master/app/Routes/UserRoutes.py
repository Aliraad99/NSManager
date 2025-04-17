from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.Auth.Authentication import get_current_user
from app.Repositories import UserRepos as user_repo
from app.Schemas.UserSchema import UserSchema
from app.database import get_db
from typing import List

router = APIRouter()

@router.post("/SaveUser/", response_model=UserSchema)
async def SaveUser(user: UserSchema, db: AsyncSession = Depends(get_db)):

    saved_user = await user_repo.SaveUser(db, user)
    if not saved_user:
        raise HTTPException(status_code=400, detail="Failed to save user.")
    return saved_user

@router.get("/GetAllUsers", response_model=List[UserSchema])
async def GetAllUsers(db: AsyncSession = Depends(get_db)):

    db_users = await user_repo.GetAllUsers(db) 
    return db_users

@router.get("/GetUserById/{UserId}", response_model=UserSchema)
async def GetUserById(UserId: int, db: AsyncSession = Depends(get_db)):

    db_user = await user_repo.GetUserById(db, UserId)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/GetUserByEmail/{UserEmail}", response_model=UserSchema)
async def GetUserByEmail(UserEmail: str, db: AsyncSession = Depends(get_db)):

    try:
        db_user = await user_repo.GetUserByEmail(db, UserEmail)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
