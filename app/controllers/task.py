from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, Task as schema_task
from app.utils.logging_helper import logger

from fastapi import HTTPException, status
from fastapi.responses import ORJSONResponse

from typing import List


async def create_task_ctrl(db: Session, account_id: int, task: TaskCreate) -> Task:
    logger.info("Creating new task for account id: {account_id}")
    return await schema_task.create_task(db=db, account_id=account_id, task=task)


async def get_task_ctrl(db: Session, account_id: int, task_id: int) -> Task:
    # Check if task exist
    logger.info("Fetching task: {task_id} for account: {account_id}")
    task_exist = await schema_task.get_task_by_id(db=db, task_id=task_id, account_id=account_id)
    if not task_exist:
        logger.warn(f"Task: {task_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid task id"
        )

    logger.info(f"Task: {task_id} found.")
    return task_exist


async def get_tasks_ctrl(db: Session, account_id: int, skip: int, limit: int) -> List[Task]:
    # Fetch tasks
    logger.info(f"Fetching tasks for account: {account_id}")
    tasks = await schema_task.get_account_tasks(db=db, account_id=account_id, skip=skip, limit=limit)
    if not tasks or len(tasks) < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tasks not found for account: {account_id}"
        )

    logger.info(f"Tasks for account: {account_id} found")
    return tasks


async def update_task_ctrl(db: Session, account_id: int, task_id: int, update: TaskUpdate) -> Task:
    updated_task = await schema_task.update_task(db=db, task_id=task_id, account_id=account_id, update=update)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tasks not found for account: {account_id}"
        )
    return updated_task 
 
async def delete_task_ctrl(db: Session, task_id: int, account_id: int) -> None:
    await schema_task.delete_task(db=db, task_id=task_id, account_id = account_id)
    return ORJSONResponse(
        content=f"Task: {task_id} deleted successfully"
    )