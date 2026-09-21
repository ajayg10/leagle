from sqlalchemy import String, DateTime, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from uuid import UUID, uuid4
from core.database import Base


class ApiKey(Base):
    """Institutional API keys for protocol access"""
    
    __tablename__ = "api_keys"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<ApiKey(id={self.id}, name='{self.name}', key='{self.key[:10]}...')>"
