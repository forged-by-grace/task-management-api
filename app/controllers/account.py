from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Header
from fastapi.responses import ORJSONResponse

from app import models, schemas
from app.utils.logging_helper import logger
from app.core import security
from app.core.security import get_password_hash
from app.enums.account_enum import AccountRoleEnum

from omegaconf import DictConfig


async def create_account_ctr(db: Session, account: schemas.account.AccountCreate) -> models.account.Account:
    # Check if account exits
    logger.info(f"Checking if account with email: {account.email} exists.")
    account_exist = await schemas.account.Account.get_account_by_email(db=db, email=account.email)
    if account_exist:
        logger.warning(f"Account registration failed due to email: {account.email} already registered.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Account with email: {account.email} already registered'
        )

    # Check if username is taken
    logger.info(f"Checking if username: {account.username} is taken")
    username_exists = await schemas.account.Account.get_account_by_username(db=db, username=account.username)
    if username_exists:
        logger.warning(f"Account with username: {account.username} already registered")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Account with username: {account.username} already registered"
        )

    # Hash plain password
    hashed_password = get_password_hash(account.password.get_secret_value())
        
    # Register new account
    new_account = await schemas.account.Account.create_account(db=db, account=account, hashed_password=hashed_password)
    logger.info(f"Account with email: {new_account.email} created successfully")
    return new_account


async def login_for_access_token_ctr(db: Session, credentials: schemas.account.AccountLogin, config: DictConfig) -> schemas.token.Token:
    # Validate credentials
    logger.info(f"Validating credentials for account with email: {credentials.email}")
    account_exist = await security.authenticate_account(db=db, credentials=credentials)
    
    # Check if account is logged in
    logger.info(f"Checking if account: {credentials.email} is logged in")
    if account_exist.is_active:
        logger.warn(f"Account: {credentials.email} already logged in")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Account: {credentials.email} already active"
        )

    # Extract account data
    account_data = {
            'first_name': account_exist.first_name,
            'last_name': account_exist.last_name,
            'id': account_exist.id,
            'username': account_exist.username,
            'email': account_exist.email,
            'role': account_exist.role,
            'avatar': str(account_exist.avatar)
        }

    # Generate access and refresh tokens
    logger.info(f"Generating access and refresh tokens for account with id: {account_exist.id}")
    access_token, refresh_token = security.get_access_and_refresh_tokens(
        config=config,
        account_data=account_data
    )
    
    # Update account active status
    await schemas.account.Account.activate_account(db=db, account_id=account_exist.id)

    # Update account role
    logger.info(AccountRoleEnum.user.value)
    await schemas.account.Account.update_account(db=db, account_id=account_exist.id, update={'role': AccountRoleEnum.user.value})
    
    logger.info(await schemas.account.Account.get_acccount_by_id(db=db, account_id=account_exist.id))
    return schemas.token.Token(
        refresh_token=refresh_token,
        access_token=access_token,
        token_type=config.app.token_type,
        token_expiry_seconds=config.app.access_token_expiry_seconds,
        data= schemas.token.TokenData(
            **account_data
        )
    ).model_dump()


async def logout_account_ctrl(db: Session, current_account: models.account.Account) -> None:
    await schemas.account.Account.deactivate_account(db=db, account_id=current_account.id)
    return ORJSONResponse(
        content="Logout successful"
    )


async def renew_access_token_ctrl(db: Session, x_refresh_token: str, config: DictConfig):
    # Verify refresh token
    logger.info("Verifying refresh token")
    payload = security.verify_token(token=x_refresh_token, secret=config.app.refresh_token_secret, config=config)
    if not payload:
        # Invalid token
        logger.warning(f"Failed to decode token")
        
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Get account data
    logger.info("Extracting account id from payload")
    account_id = payload.get('id')
    account_exist = await schemas.account.Account.get_acccount_by_id(db=db, account_id=account_id)
    
    # Extract account data
    account_data = {
            'first_name': account_exist.first_name,
            'last_name': account_exist.last_name,
            'id': account_exist.id,
            'username': account_exist.username,
            'email': account_exist.email,
            'role': account_exist.role,
            'avatar': account_exist.avatar
        }

    # Generate access and refresh tokens
    logger.info(f"Generating access and refresh tokens for account with id: {account_exist.id}")
    access_token, refresh_token = security.get_access_and_refresh_tokens(
        config=config,
        account_data=account_data
    )

    return schemas.token.Token(
        refresh_token=refresh_token,
        access_token=access_token,
        token_type=config.app.token_type,
        token_expiry_seconds=config.app.access_token_expiry_seconds,
        data= schemas.token.TokenData(
            **account_data
        )
    )


async def update_me_ctrl(
    update: schemas.account.AccountUpdate,
    db: Session,
    current_account: models.account.Account
) -> models.account.Account:
    # Check if password is to be updated
    logger.info("Checking if password would be updated")
    hashed_password = None
    update_dict = {}
    if update.password:
        # Deserialize update object to dict
        update_dict = update.model_dump(exclude_none=True)   

        logger.info("Hashing plain passwor")
        hashed_password = hash_password(update.password.get_secret_value())
        update_dict.update({"hashed_password": hashed_password})

        return await schemas.account.Account.update_account(db=db, account_id=current_account.id, update=update_dict, hashed_password=hashed_password)

    return await schemas.account.Account.update_account(db=db, account_id=current_account.id, update=update.model_dump(exclude_none=True))


async def delete_me_ctrl(
    db: Session,
    current_account: models.account.Account
):
    # Delete account
    logger.info(f"Deleting account with id: {current_account.id}")
    await schemas.account.Account.delete_account(db=db, account_id=current_account.id)
    
    return ORJSONResponse(
        status_code=status.HTTP_200_OK,
        content=f"Account with id: {current_account.id} deleted successfully"
    )