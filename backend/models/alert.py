from sqlalchemy import String, Boolean, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import UUID, uuid4
from core.database import Base
from typing import Optional


class Alert(Base):
    """
    Alert records for newly detected regulation impacts.
    Sent to users via email/WebSocket and tracked for acknowledgment.
    """
    
    __tablename__ = "alerts"
    
    # Columns
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    regulation_id: Mapped[UUID] = mapped_column(ForeignKey("regulations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Alert content
    severity: Mapped[str] = mapped_column(String(20), default="MEDIUM")  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Tracking
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    regulation: Mapped["Regulation"] = relationship(back_populates="alerts")
    
    def __repr__(self):
        return f"<Alert(id={self.id}, regulation_id={self.regulation_id}, severity='{self.severity}')>"
