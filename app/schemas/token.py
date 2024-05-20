from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Optional, Dict


class TokenData(BaseModel):
    first_name: Optional[str] = Field(None, title='Firstname', description='Firstname of the account holder.', examples=['Confidence'])
    last_name: Optional[str] = Field(None, title='Lastname', description='Lastname of the account holder', examples=['James'])   
    id: Optional[int] = Field(None, title='Account ID', description='ID of the account')
    username: Optional[str] = Field(None, title='Username', description="Username of the account holder.", examples=['jc'])
    email: Optional[str] = Field(None, title='Email Address', description='Email address of the account', examples=['joe@example.com'])
    role: Optional[str] = Field(None, title='Account Role', description='Role of the account', examples=['Admin', 'Guest', 'User'])
    avatar: Optional[str] = Field(None, title='Avatar Image', description='Link to the avatar image of the account holder', examples=['https://example.com/image.jpg'])


class Token(BaseModel):
    refresh_token: str = Field(..., title='Refresh token', description='Used to obtain new access token')
    access_token: str = Field(..., title='Acccess Token', description='Generated access token')
    token_type: str = Field(..., title='Access Token Type', description='Type of the access token', examples=['Bearer'])
    token_expiry_seconds: int = Field(..., title='Access Token Expiry', description='Access token expiry in seconds', examples=[3600]) 
    data: TokenData = Field(..., title='Token data', description='Contains account metadata')


