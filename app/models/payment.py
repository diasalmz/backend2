from sqlalchemy import Column, String, DateTime, func, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Payment(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)
    external_id = Column(String, nullable=True)  # ID платежа в шлюзе
    fio = Column(String, nullable=True)
    iin = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    user = relationship("User", back_populates="payments")