from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    id = Column(String, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), onupdate=func.now())

    payments = relationship("Payment", back_populates="user")