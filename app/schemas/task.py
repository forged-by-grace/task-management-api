from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.schemas import task, account
from app.models.task import Task as model_task
from app.utils.logging_helper import logger

from typing import List




class TaskBase(BaseModel):
    title: str = Field(..., title='Task title', description='Title of the task', examples=['Hiking'])
    description: str = Field(..., title='Task Description', description='Description of the task', examples=['I want to hike today'])
    start_time: datetime = Field(datetime.now(), title='Task Start time', description='Date and time the task will be started', examples=['2024-05-17T17:25:20'])
    stop_time: Optional[datetime] = Field(None, title='Task Stop Time', description='Date and time the task will end', examples=[None])
    

class TaskCreate(TaskBase):    
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, title='Updated Task title', description='Updated title of the task', examples=['Climbing'])
    description: Optional[str] = Field(None, title='Updated Task Description', description='Updated description of the task', examples=['I want to climbing today'])
    completed: Optional[bool] = Field(None, title='Updated Completed', description='Updated completion status of the task', examples=[True])



class TaskInDB(TaskBase):
    id: int = Field(..., title='Task ID', description='Unique identifier for the task')
    completed: bool = Field(..., title='Task Completed', description='Completion status of the task', examples=[True])
  
    class Config:
        from_attributes = True


class Task:
    def __init__(self):
        pass


    @staticmethod
    async def get_task_by_id(db: Session, task_id: int, account_id: int) -> model_task:
        return db.query(model_task).filter(model_task.id == task_id and model_task.owner_id == account_id).first()


    @staticmethod
    async def create_task(db: Session, account_id: int, task: task.TaskCreate) -> model_task:
        # Create task db object
        db_task = model_task(**task.model_dump(exclude_none=True), owner_id=account_id)

        # Add new task to db
        db.add(db_task)
        db.commit()
        db.refresh(db_task)

        return db_task


    @staticmethod
    async def get_account_tasks(db: Session, account_id: int, skip: int, limit: int) -> List[model_task]:
        return db.query(model_task).filter(model_task.owner_id == account_id).offset(skip).limit(limit).all()


    @staticmethod
    async def update_task(db: Session, task_id: int, account_id: int, update: task.TaskUpdate) -> model_task:
        logger.info("Creating task update query")
        db.query(model_task).filter(model_task.id == task_id and model_task.owner_id == account_id).update(values=update.model_dump(exclude_none=True))
        
        logger.info("Commiting changes to database")
        db.commit()
        return await Task.get_task_by_id(db=db, task_id=task_id, account_id=account_id)


    @staticmethod
    async def delete_task(db: Session, task_id: int, account_id: int) -> None:
        db.query(model_task).filter(model_task.id == task_id and model_task.owner_id == account_id).delete()
        db.commit()
