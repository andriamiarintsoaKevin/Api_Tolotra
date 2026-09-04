"""align product and stock movement schema

Revision ID: f1a2b3c4d5e6
Revises: e69c1ce79a8f
Create Date: 2026-09-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "e69c1ce79a8f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    product_columns = {column["name"] for column in inspector.get_columns("products")}

    columns = [
        ("price", sa.Column("price", sa.Float(), nullable=False, server_default=sa.text("0"))),
        ("quantity", sa.Column("quantity", sa.Integer(), nullable=False, server_default=sa.text("0"))),
        ("sku", sa.Column("sku", sa.String(length=100), nullable=True)),
        ("sector", sa.Column("sector", sa.String(length=50), nullable=False, server_default="general")),
        ("reorder_threshold", sa.Column("reorder_threshold", sa.Integer(), nullable=False, server_default=sa.text("10"))),
        ("warehouse_location", sa.Column("warehouse_location", sa.String(length=255), nullable=True)),
        ("batch_number", sa.Column("batch_number", sa.String(length=100), nullable=True)),
        ("expiry_date", sa.Column("expiry_date", sa.DateTime(timezone=True), nullable=True)),
        ("storage_temperature", sa.Column("storage_temperature", sa.Float(), nullable=True)),
        ("serial_number", sa.Column("serial_number", sa.String(length=100), nullable=True)),
        ("hardware_condition", sa.Column("hardware_condition", sa.String(length=100), nullable=True)),
        ("assigned_to", sa.Column("assigned_to", sa.String(length=255), nullable=True)),
    ]
    for name, column in columns:
        if name not in product_columns:
            op.add_column("products", column)

    if "unit_price" in product_columns and "price" not in product_columns:
        op.execute("UPDATE products SET price = unit_price")
    if "stock_quantity" in product_columns and "quantity" not in product_columns:
        op.execute("UPDATE products SET quantity = stock_quantity")

    existing_indexes = {index["name"] for index in inspector.get_indexes("products")}
    for name, column in (("ix_products_sku", "sku"), ("ix_products_batch_number", "batch_number"), ("ix_products_serial_number", "serial_number")):
        if name not in existing_indexes:
            op.create_index(name, "products", [column], unique=False)

    if not inspector.has_table("stock_movements"):
        op.create_table(
            "stock_movements",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("product_id", sa.Integer(), nullable=False),
            sa.Column("quantity", sa.Integer(), nullable=False),
            sa.Column("movement_type", sa.String(length=3), nullable=False),
            sa.Column("reason", sa.String(length=255), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_stock_movements_id", "stock_movements", ["id"], unique=False)
        op.create_index("ix_stock_movements_product_id", "stock_movements", ["product_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_stock_movements_product_id"), table_name="stock_movements")
    op.drop_index(op.f("ix_stock_movements_id"), table_name="stock_movements")
    op.drop_table("stock_movements")

    op.drop_column("products", "assigned_to")
    op.drop_column("products", "hardware_condition")
    op.drop_index(op.f("ix_products_serial_number"), table_name="products")
    op.drop_column("products", "serial_number")
    op.drop_column("products", "storage_temperature")
    op.drop_column("products", "expiry_date")
    op.drop_index(op.f("ix_products_batch_number"), table_name="products")
    op.drop_column("products", "batch_number")
    op.drop_column("products", "warehouse_location")
    op.drop_column("products", "reorder_threshold")
    op.drop_column("products", "sector")
    op.drop_index(op.f("ix_products_sku"), table_name="products")
    op.drop_column("products", "sku")
    op.drop_column("products", "quantity")
    op.drop_column("products", "price")