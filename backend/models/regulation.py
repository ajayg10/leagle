from sqlalchemy import String, Text, SmallInteger, Date, DateTime, ARRAY, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, date
from uuid import UUID, uuid4
from core.database import Base
from typing import List


class Regulation(Base):
    """External regulatory documents (GDPR, labor laws, finance regs, etc.)"""
    
    __tablename__ = "regulations"
    
    # Columns
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(255), nullable=True)  # e.g., "eu.gdpr", "india.sebi"
    category: Mapped[str] = mapped_column(String(100), nullable=True, index=True)  # "data_privacy", "finance", "labor"
    jurisdiction: Mapped[str] = mapped_column(String(100), nullable=True)  # e.g., "EU", "US", "India"
    effective_date: Mapped[date] = mapped_column(Date, nullable=True, index=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=True)
    qdrant_ids: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)  # Vector chunk IDs in Qdrant
    risk_level: Mapped[int] = mapped_column(SmallInteger, default=0)  # 0-100 scale
    penalty_description: Mapped[str] = mapped_column(Text, nullable=True)  # e.g., "Fine: 4% global turnover"
    legal_weight: Mapped[int] = mapped_column(SmallInteger, default=5)  # 1-10 scale (Constitutional=10, Law=7, Reg=3)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    impact_mappings: Mapped[List["ImpactMapping"]] = relationship(back_populates="regulation", cascade="all, delete-orphan")
    alerts: Mapped[List["Alert"]] = relationship(back_populates="regulation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Regulation(id={self.id}, title='{self.title}', category='{self.category}')>"
