from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.utils.init_db import Base
from datetime import datetime


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, index=True, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False, index=True)
    updated_at = Column(DateTime(), nullable=True)
    start_time = Column(DateTime(), default=datetime.now(), nullable=False, index=True)
    stop_time = Column(DateTime(), nullable=True)
    owner_id = Column(Integer, ForeignKey("accounts.id"))

    owner = relationship("Account", back_populates="tasks")
