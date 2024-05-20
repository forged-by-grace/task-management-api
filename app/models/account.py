from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from datetime import datetime

from app.utils.init_db import Base

from app.enums.account_enum import AccountRoleEnum

class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True, nullable=False)
    last_name = Column(String, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    avatar = Column(String, unique=False, index=False, nullable=True)
    role = Column(String, index=True, default=AccountRoleEnum.guest.value, nullable=False)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False, index=True)
    updated_at = Column(DateTime(), nullable=True)

    tasks = relationship("Task", back_populates="owner")
