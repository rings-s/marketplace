import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.models.base import UUIDMixin, TimestampMixin
from app.core.enums import UserRole
from app.database import Base


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    google_sub: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(2048))
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.buyer, nullable=False)
    city: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_active: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # relationships
    store: Mapped["Store | None"] = relationship("Store", back_populates="owner", uselist=False)
    favorites: Mapped[list["Favorite"]] = relationship("Favorite", back_populates="user")
    sent_messages: Mapped[list["ChatMessage"]] = relationship("ChatMessage", back_populates="sender")
    reports: Mapped[list["Report"]] = relationship(
        "Report", back_populates="reporter", foreign_keys="Report.reporter_id"
    )
