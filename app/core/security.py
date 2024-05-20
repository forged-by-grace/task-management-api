from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Annotated
from app.schemas.token import TokenData
from app.utils.db_helper import get_db
from app.utils.logging_helper import logger
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from app.schemas import account
from app.models import account as account_model
from app.utils.config_helper import get_config

from omegaconf import DictConfig


# Init password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Set credential exception
credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def verify_password(plain_password, hashed_password) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Failed to verify password due to error: {str(e)}")


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


async def authenticate_account(db: Session, credentials: account.AccountLogin) -> account_model.Account:
    # Check if account exists
    logger.info(f"Checking if account with email: {credentials.email} exists")
    account_exist = await account.Account.get_account_by_email(db=db, email=credentials.email)
    if not account_exist:
        logger.warning(f"Account with email: {credentials.email} not found")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email"
        )
    
    logger.info(f"Account with email: {credentials.email} found")

    # Verify password
    logger.info(f"Verifying password for account with id: {account_exist.id}")
    valid_password = verify_password(hashed_password=account_exist.hashed_password, plain_password=credentials.password.get_secret_value())
    if not valid_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password"
        )

    return account_exist


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_authorization_token(authorization: Annotated[str, Header()], config: DictConfig = Depends(get_config)) -> str:
    # Split authorization token into token type and access token
    logger.info(f"Spliting authorization token into token type and access token")
    token_type, token = authorization.split(' ')

    # Check if token type is valid
    logger.info("Checking if token type is valid")
    if token_type != config.app.token_type:
        raise credentials_exception
    
    return token


async def get_current_account(db: Session = Depends(get_db), token: str = Depends(get_authorization_token), config: DictConfig = Depends(get_config)) -> account_model.Account:
    # Verify token
    logger.info(f"Verifying token")
    payload = verify_token(token=token, secret=config.app.access_token_secret, config=config)
    if not payload:
        # Invalid token
        logger.warning(f"Failed to decode token")
        raise credentials_exception
    
    # Get account id
    logger.info('Fetchin account id from token payload')
    account_id = payload.get('id')

    # Get account with id
    logger.info(f"Fetching account with id: {account_id}")
    account_db = await account.Account.get_acccount_by_id(account_id=account_id, db=db)
    if account_db is None:
        logger.warn(f"Account: {account_id} not found in database")
        raise credentials_exception
    return account_db


async def get_current_active_account(current_account: account_model.Account = Depends(get_current_account)) -> account_model.Account:
    if not current_account.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive account",
        )

    return current_account


def generate_jwt_token(payload: dict, secret: str, config: DictConfig):
    # Encode token
    try:
        logger.info(f"Encoding token")
        return jwt.encode(claims=payload, key=secret, algorithm=config.app.token_algorithm)
    except JWTError as err:
        logger.error(f'Failed to create token due to error: {str(err)}')
    except Exception as e:
        logger.error(f'Failed to create token due to error: {str(e)}')


def get_access_and_refresh_tokens(config: DictConfig, account_data: dict):
    # Create token expiry
    logger.info(f"Creating access and refresh token expiration for account: {account_data.get('id')}")
    access_token_exp = datetime.utcnow() + timedelta(seconds=config.app.access_token_expiry_seconds)
    refresh_token_exp = datetime.utcnow() + timedelta(seconds=config.app.refresh_token_expiry_seconds)
    
    # Create access token payload
    logger.info(f"Creating access token payload for account {account_data.get('id')}")
    payload_access_token = {
        'iss': config.app.token_iss,
        'aud': config.app.token_aud,
        'sub': config.app.token_sub,        
        'email': account_data.get('email'),
        'id': account_data.get('id'),
        'role': account_data.get('role'),
        'iat': datetime.utcnow(),
        'exp': access_token_exp
    }

    # Create refresh token payload
    logger.info(f"Creating refresh token payload for account {account_data.get('id')}")
    payload_refresh_token = {
        'iss': config.app.token_iss,
        'aud': config.app.token_aud,
        'sub': config.app.token_sub,        
        'email': account_data.get('email'),
        'id': account_data.get('id'),
        'role': account_data.get('role'),
        'iat': datetime.utcnow(),
        'exp': refresh_token_exp
    }
    
    # Generate access token
    logger.info(f"Generating access token for account {account_data.get('id')}")
    access_token = generate_jwt_token(payload=payload_access_token, secret=config.app.access_token_secret, config=config)
    
    # Generate refresh token
    logger.info(f"Generating refresh token for account {account_data.get('id')}")    
    refresh_token = generate_jwt_token(payload=payload_refresh_token, secret=config.app.refresh_token_secret, config=config)

    return access_token, refresh_token


def verify_token(token: str, secret: str, config: DictConfig) -> dict:
    try:
        logger.info(f"Decoding token")
        payload = jwt.decode(
            token=token, 
            key=secret, 
            algorithms=config.app.token_algorithm, 
            audience=config.app.token_aud,
            subject=config.app.token_sub,
            issuer=config.app.token_iss
            ) 

        logger.info(f"Token: decoded successfully")
        return payload
    except JWTError as err:
        logger.error(f'Failed to verify token due to error: {str(err)}')
        raise credentials_exception
    
