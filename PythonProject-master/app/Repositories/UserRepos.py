from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.Models.User import User
from app.Schemas.UserSchema import UserSchema
from passlib.context import CryptContext
from sqlalchemy.future import select

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def GetUserById(db: AsyncSession, UserId: int):
    result = await db.execute(select(User).filter(User.Id == UserId))
    return result.scalars().first()

async def GetUserByEmail(db: AsyncSession, UserEmail: str):
    result = await db.execute(select(User).filter(User.Email == UserEmail))
    return result.scalars().first()

async def GetAllUsers(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()

async def SaveUser(db: AsyncSession, user: UserSchema):
    db_user: User
    if user.Id == 0 or user.Id is None:
        hashedPassword = pwd_context.hash(user.Password)
        db_user = User(
            FirstName=user.FirstName, 
            MiddleName=user.MiddleName, 
            LastName=user.LastName,
            Email=user.Email,
            Password=hashedPassword
        )
        db.add(db_user)
    else:
        result = await db.execute(select(User).filter(User.Id == user.Id))
        db_user = result.scalars().first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        db_user.FirstName = user.FirstName
        db_user.MiddleName = user.MiddleName
        db_user.LastName = user.LastName
        db_user.Email = user.Email

        
    await db.commit()
    await db.refresh(db_user)
    return UserSchema.from_orm(db_user)
