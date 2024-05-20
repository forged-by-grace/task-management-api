from fastapi import APIRouter, Depends, HTTPException

from app.utils import init_db
from app.utils.db_helper import get_db
from app.models import task as model_task
from app.schemas import task as schema_task
from app.models.account import Account
from app.utils.init_db import SessionLocal, engine
from app.core.security import get_current_active_account
from app.controllers import task as task_controller
from app.models import task

from typing import List

from sqlalchemy.orm import Session



# Create task table if it does not exist
task.Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/api/v1/tasks",
    tags=['Task'],
)


@router.post("/create/", response_model=schema_task.TaskInDB, response_model_exclude_none=True, description="Create new task for current account user")
async def create_new_task(task: schema_task.TaskCreate, db: Session = Depends(get_db), current_account: Account = Depends(get_current_active_account)):
    return await task_controller.create_task_ctrl(db=db, account_id=current_account.id, task=task)


@router.get("/", response_model=List[schema_task.TaskInDB], response_model_exclude_none=True)
async def get_tasks(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_account: Account = Depends(get_current_active_account) 
    ):
    return await task_controller.get_tasks_ctrl(db=db, account_id=current_account.id, skip=skip, limit=limit)


@router.get("/{task_id}", response_model=schema_task.TaskInDB, response_model_exclude_none=True)
async def get_task(
    task_id: int, 
    db: Session = Depends(get_db),
    current_account: Account = Depends(get_current_active_account) 
   ):
    return await task_controller.get_task_ctrl(db=db, account_id=current_account.id, task_id=task_id)


@router.put("/update/{task_id}", response_model=schema_task.TaskInDB, response_model_exclude_none=True)
async def update_existing_task(
    task_id: int,
    update: schema_task.TaskUpdate,
    db: Session = Depends(get_db),
    current_account: Account = Depends(get_current_active_account)
    ):
    return await task_controller.update_task_ctrl(db=db, account_id=current_account.id, task_id=task_id, update=update)


@router.delete("/remove/{task_id}", response_model=schema_task.TaskInDB, response_model_exclude_none=True)
async def delete_existing_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_account: Account = Depends(get_current_active_account),   
   ):
    return await task_controller.delete_task_ctrl(db=db, task_id=task_id, account_id=current_account.id)
