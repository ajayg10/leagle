from sqlalchemy import String, Text, Date, DateTime, ARRAY, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, date
from uuid import UUID, uuid4
from core.database import Base
from typing import List


class Policy(Base):
    """Internal company policies that may be impacted by regulations"""
    
    __tablename__ = "policies"
    
    # Columns
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    department: Mapped[str] = mapped_column(String(100), nullable=True, index=True)  # HR, IT, Finance, Legal, etc.
    owner: Mapped[str] = mapped_column(String(200), nullable=True)
    last_review: Mapped[date] = mapped_column(Date, nullable=True)
    qdrant_ids: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)  # Vector chunk IDs in Qdrant
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    impact_mappings: Mapped[List["ImpactMapping"]] = relationship(back_populates="policy", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Policy(id={self.id}, title='{self.title}', department='{self.department}')>"
