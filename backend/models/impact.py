from sqlalchemy import String, Float, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import UUID, uuid4
from core.database import Base
from typing import Optional


class ImpactMapping(Base):
    """
    Links regulations to affected policies.
    Created by Qdrant semantic search + LLM analysis.
    """
    
    __tablename__ = "impact_mappings"
    
    # Columns
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    regulation_id: Mapped[UUID] = mapped_column(ForeignKey("regulations.id", ondelete="CASCADE"), nullable=False, index=True)
    policy_id: Mapped[UUID] = mapped_column(ForeignKey("policies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Similarity and impact scores
    similarity: Mapped[float] = mapped_column(Float, nullable=True)  # Cosine similarity from Qdrant (0-1)
    impact_level: Mapped[str] = mapped_column(String(20), default="MEDIUM")  # "HIGH", "MEDIUM", "LOW"
    
    # LLM analysis results
    llm_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # AI-generated explanation
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Why high/medium/low impact
    recommended_actions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON or plain text
    
    # Status tracking
    status: Mapped[str] = mapped_column(String(20), default="OPEN")  # "OPEN", "RESOLVED", "IGNORED"
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    regulation: Mapped["Regulation"] = relationship(back_populates="impact_mappings")
    policy: Mapped["Policy"] = relationship(back_populates="impact_mappings")
    
    def __repr__(self):
        return f"<ImpactMapping(regulation_id={self.regulation_id}, policy_id={self.policy_id}, impact_level='{self.impact_level}')>"
