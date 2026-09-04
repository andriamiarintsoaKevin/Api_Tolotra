from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Product(Base):
    """Modèle SQLAlchemy représentant un produit en stock."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
    )
    # --- Champs Généraux & Sectoriels ---
    sku: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    sector: Mapped[str] = mapped_column(String(50), default="general", nullable=False, index=True)
    reorder_threshold: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    warehouse_location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # --- Spécificités Médicales ---
    batch_number: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    expiry_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    storage_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)

    # --- Spécificités IT ---
    serial_number: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    hardware_condition: Mapped[str | None] = mapped_column(String(100), nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    category: Mapped["Category"] = relationship("Category", back_populates="products")
    stock_movements: Mapped[list["StockMovement"]] = relationship(
        "StockMovement",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    @property
    def is_expired(self) -> bool:
        """Indique si le produit médical a dépassé sa date de péremption."""
        if not self.expiry_date:
            return False
        from datetime import timezone
        now = datetime.now(timezone.utc)
        exp = self.expiry_date if self.expiry_date.tzinfo else self.expiry_date.replace(tzinfo=timezone.utc)
        return exp < now
