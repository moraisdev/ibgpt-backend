"""initial migration

Revision ID: 33216ba898b0
Revises: 
Create Date: 2024-12-17 23:51:30.863168

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '33216ba898b0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column("name", sa.String(50), unique=True, nullable=False),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), unique=True, index=True, nullable=False),
        sa.Column("phone", sa.String(20), unique=True, index=True, nullable=False),
        sa.Column("password", sa.String(255), nullable=False),
        sa.Column("cnpj", sa.String(14), unique=True, index=True, nullable=False),
        sa.Column("company_name", sa.String(255), index=True, nullable=False),
        sa.Column("job_title", sa.String(255), index=True, nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id"), nullable=False, server_default=sa.text("3")),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("TRUE"), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("timezone('America/Sao_Paulo', now())"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("timezone('America/Sao_Paulo', now())"),
            nullable=False,
        ),
    )

    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("company_representative_name", sa.String(100), nullable=False),
        sa.Column("company_representative_last_name", sa.String(100), nullable=False),
        sa.Column("company_representative_email", sa.String(255), nullable=False),
        sa.Column("company_representative_phone_number", sa.String(20), nullable=False),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("company_email", sa.String(255), nullable=False),
        sa.Column("company_phone_number", sa.String(20), nullable=False),
        sa.Column("company_website", sa.String(255), nullable=False),
        sa.Column("company_activity_sector", sa.String(100), nullable=False),
        sa.Column("company_cnpj", sa.String(14), nullable=False),
        sa.Column("company_address_street", sa.String(255), nullable=False),
        sa.Column("company_address_number", sa.String(255), nullable=False),
        sa.Column("company_address_complement", sa.String(255), nullable=True),
        sa.Column("company_address_neighbourhood", sa.String(255), nullable=False),
        sa.Column("company_address_city", sa.String(255), nullable=False),
        sa.Column("company_address_state", sa.String(255), nullable=False),
        sa.Column("company_address_country", sa.String(255), nullable=False),
        sa.Column("company_address_zip_code", sa.String(20), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("TRUE"), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("timezone('America/Sao_Paulo', now())"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("timezone('America/Sao_Paulo', now())"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.UniqueConstraint("user_id", "company_cnpj", name="uq_user_customer"),
    )

    # Tabela offers
    op.create_table(
        "offers",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id"), nullable=True),
        sa.Column("status", sa.String(255), nullable=True),
        sa.Column("offer_type", sa.String(50), nullable=True),
        sa.Column("company_service_type", sa.String(50), nullable=True),
        sa.Column("company_profit_type", sa.String(50), nullable=True),
        sa.Column("company_time_profit_type", sa.String(50), nullable=True),
        sa.Column("company_work_regime", sa.String(50), nullable=True),
        sa.Column("company_clt_employees", sa.Integer(), nullable=True),
        sa.Column("company_pj_employees", sa.Integer(), nullable=True),
        sa.Column("company_freelance_employees", sa.Integer(), nullable=True),
        sa.Column("company_internship_employees", sa.Integer(), nullable=True),
        sa.Column("company_cooperative_employees", sa.Integer(), nullable=True),
        sa.Column("company_total_employees", sa.Integer(), nullable=True),
        sa.Column("accuracy_ia", sa.Float(), nullable=True),
        sa.Column("periodicity", sa.String(50), nullable=True),
        sa.Column("calculated_value", sa.Float(), nullable=True),
        sa.Column("commission", sa.Float(), nullable=True),
        sa.Column("liquidation_value", sa.Float(), nullable=True),
        sa.Column("observations", sa.Text(), nullable=True),
        sa.Column("result_openai", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("timezone('America/Sao_Paulo', now())"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("timezone('America/Sao_Paulo', now())"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )

    # Tabela offer_documents
    op.create_table(
        "offer_documents",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("offer_id", sa.Integer(), sa.ForeignKey("offers.id"), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("content", sa.LargeBinary(), nullable=False),
        sa.Column("processed_text", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("timezone('America/Sao_Paulo', now())"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("timezone('America/Sao_Paulo', now())"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )

    # Tabela inss_synthesized_calculations
    op.create_table(
        "inss_synthesized_calculations",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("offer_id", sa.Integer(), sa.ForeignKey("offers.id"), nullable=False),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("values", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("timezone('America/Sao_Paulo', now())"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("timezone('America/Sao_Paulo', now())"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )

def downgrade():
    op.drop_table("inss_synthesized_calculations")
    op.drop_table("offer_documents")
    op.drop_table("offers")
    op.drop_table("customers")
    op.drop_table("users")
    op.drop_table("roles")
