from fastapi import APIRouter, Depends, HTTPException, Header

from sqlalchemy.orm import Session

from omegaconf import DictConfig

from typing import Annotated, List

from app.utils import init_db
from app.schemas.account import AccountInDBBase
from app.schemas.token import Token
from app.schemas import account as schema_account
from app.utils.init_db import SessionLocal, engine
from app.controllers import account as account_controller
from app.utils.db_helper import get_db
from app.utils.config_helper import get_config
from app.core import security
from app.models import account


# Create account table if it does not exist
account.Base.metadata.create_all(bind=engine)


router = APIRouter(
    prefix="/api/v1/accounts",
    tags=['Account'],
)


@router.post("/register", response_model_exclude_none=True, response_model=AccountInDBBase, response_model_exclude='hashed_password', description="Registers new account")
async def create_new_account(account: schema_account.AccountCreate, db: Session = Depends(get_db)):
    return await account_controller.create_account_ctr(db=db, account=account)


@router.post("/login", response_model=Token, description="Login account for access and refresh token after successful account credential authentication")
async def login_for_access_token(credentials: schema_account.AccountLogin, db: Session = Depends(get_db), config: DictConfig = Depends(get_config)):
    return await account_controller.login_for_access_token_ctr(db=db, credentials=credentials, config=config)


@router.get("/renew-access-token", response_model=Token, description="Get new access token from refresh token", response_model_exclude_none=True)
async def renew_access_token(x_refresh_token: Annotated[str, Header()],  db: Session = Depends(get_db), config: DictConfig = Depends(get_config)):
    return await account_controller.renew_access_token_ctrl(db=db, x_refresh_token=x_refresh_token, config=config)


@router.put("/me", response_model=AccountInDBBase, response_model_exclude=['hashed_password'], description="Updates current user account")
async def update_me(update: schema_account.AccountUpdate, db: Session = Depends(get_db), current_account: account.Account = Depends(security.get_current_active_account)):
    return await account_controller.update_me_ctrl(update=update, db=db, current_account=current_account)


@router.get("/logout", description="Logout current active account")
async def log_me_out(
    db: Session = Depends(get_db),
    current_account: account.Account = Depends(security.get_current_active_account)
):
    return await account_controller.logout_account_ctrl(db=db, current_account=current_account)


@router.delete("/me", description="Deletes current user account")
async def delete_me(
    db: Session = Depends(get_db),
    current_account: account.Account = Depends(security.get_current_active_account)
    ):
    return await account_controller.delete_me_ctrl(db=db, current_account=current_account)

