from sqlalchemy import Column,BigInteger,String,Text,DateTime,func,ForeignKey,Enum
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at = Column( DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False)

class Task(Base):
    __tablename__ = "tasks"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        Enum(
            "pending",
            "in_progress",
            "completed",
            "cancelled",
            name="task_status"
        ),
        nullable=False,
        default="pending"
    )
    priority = Column(
        Enum(
            "low",
            "medium",
            "high",
            name="task_priority"
        ),
        nullable=False,
        default="medium"
    )
    due_date = Column(DateTime(timezone=True),nullable=True)
    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at = Column( DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False)