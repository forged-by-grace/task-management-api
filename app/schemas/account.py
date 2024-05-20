from pydantic import BaseModel, EmailStr, Field, HttpUrl, SecretStr
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

from sqlalchemy.orm import Session

from app.schemas import account, task
from app.models.account import Account as model_account
from app.models.task import Task as model_task


class AccountBase(BaseModel):
    last_name: str = Field(..., title='Lastname', description='Lastname of the account user', examples=['James'])
    first_name: str = Field(..., title='Firstname', description='Firstname of the account user.', examples=['Confidence'])
    username: str = Field(..., title='Username', description="Username of the account user.", examples=['jc'])
    email: EmailStr = Field(..., title='Email Address', description='Email address of the account user', examples=['joe@example.com'])
    avatar: Optional[HttpUrl] = Field(None, title='Avatar Image', description='Link to the avatar image of the account user', examples=['https://example.com/image.jpg'])


class AccountCreate(AccountBase):
    password: SecretStr = Field(..., title='Password', description='Account password', examples=['12345678'], min_length=8)


class AccountUpdate(BaseModel):
    last_name: Optional[str] = Field(None, title='Lastname', description='Updated lastname of the account user', examples=['James'])
    first_name: Optional[str] = Field(None, title='Firstname', description='Updated firstname of the account user.', examples=['Confidence'])
    username: Optional[str] = Field(None, title='Username', description="Updated username of the account user.", examples=['jc'])
    avatar: Optional[HttpUrl] = Field(None, title='Avatar Image', description='Updated link to the avatar image of the account user', examples=['https://example.com/image.jpg'])
    password: Optional[SecretStr] = Field(None, title='Password', description='Updated account password', examples=['12345678'], min_length=8)


class AccountLogin(BaseModel):
    email: EmailStr = Field(..., title='Email Address', description='Email address of the account user', examples=['joe@example.com'])
    password: SecretStr = Field(..., title='Password', description='Account password', examples=['12345678'], min_length=8)


class AccountInDBBase(AccountBase):
    id: int = Field(..., title='Account ID', description='Unique identifier for the account.', examples=[1])
    is_active: bool = Field(..., title='IsActive', description='Active status of the account', examples=[False])
    created_at: datetime = Field(..., title='CreatedAt', description='Datetime the account was created.', examples=["2024-05-17T12:13:15"])
    updated_at: Optional[datetime] = Field(None, title='UpdatedAt', description='Datetime the account was updated.', examples=["2024-05-17T12:13:15"])
    role: str = Field(..., title='Account Role', description='Role of the account', examples=['Admin', 'Guest', 'User'])
    
    class Config:
        from_attributes = True


class Account:
    def __init__(self):
        pass
    
    @staticmethod
    async def get_acccount_by_id(db: Session, account_id: int) -> model_account:
        return db.query(model_account).filter(model_account.id == account_id).first()

    @staticmethod
    async def get_account_by_email(db: Session, email: str) -> model_account:
        return db.query(model_account).filter(model_account.email == email).first()


    @staticmethod
    async def get_account_by_username(db: Session, username: str) -> model_account:
        return db.query(model_account).filter(model_account.username == username).first()


    @staticmethod
    async def get_accounts(db: Session, skip: int = 0, limit: int = 50) -> List[model_account]:
        return db.query(model_account).offset(skip).limit(limit).all()


    @staticmethod
    async def create_account(db: Session, account: account.AccountCreate, hashed_password: str) -> model_account:
        # Create account db object
        db_account = model_account(**account.model_dump(exclude_none=True, exclude={'password', 'avatar'}), hashed_password=hashed_password, avatar=str(account.avatar))

        # Add new account to db
        db.add(db_account)
        db.commit()
        db.refresh(db_account)

        return db_account
    

    @staticmethod
    async def update_account(db: Session, account_id: int, update: dict, hashed_password: Optional[str] = None) -> model_account:
        if hashed_password:
            
            db.query(model_account).filter(model_account.id == account_id).update(values=update, hashed_password=hashed_password)
        else:
            db.query(model_account).filter(model_account.id == account_id).update(values=update)
        
        # Commit changes to db
        db.commit()

        return await Account.get_acccount_by_id(db=db, account_id=account_id)


    @staticmethod
    async def deactivate_account(db: Session, account_id: int) -> None:
        db.query(model_account).filter(model_account.id == account_id).update(values={'is_active': False})
        db.commit()


    @staticmethod
    async def activate_account(db: Session, account_id: int) -> None:
        db.query(model_account).filter(model_account.id == account_id).update(values={'is_active': True})
        db.commit()


    @staticmethod
    async def delete_account(db: Session, account_id: int) -> None:
        db.query(model_account).filter(model_account.id == account_id).delete()
        db.commit()