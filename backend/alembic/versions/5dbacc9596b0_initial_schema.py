"""initial_schema

Revision ID: 5dbacc9596b0
Revises: 
Create Date: 2026-04-17 17:15:21.891235

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5dbacc9596b0'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Create all tables"""
    # Create regulations table
    op.create_table(
        'regulations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('source', sa.String(255), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('jurisdiction', sa.String(100), nullable=True),
        sa.Column('effective_date', sa.Date(), nullable=True),
        sa.Column('raw_text', sa.Text(), nullable=True),
        sa.Column('qdrant_ids', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('risk_level', sa.SmallInteger(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_regulations_category', 'regulations', ['category'])
    op.create_index('ix_regulations_effective_date', 'regulations', ['effective_date'])
    op.create_index('ix_regulations_title', 'regulations', ['title'])

    # Create policies table
    op.create_table(
        'policies',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('department', sa.String(100), nullable=True),
        sa.Column('owner', sa.String(200), nullable=True),
        sa.Column('last_review', sa.Date(), nullable=True),
        sa.Column('qdrant_ids', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_policies_department', 'policies', ['department'])
    op.create_index('ix_policies_title', 'policies', ['title'])

    # Create impact_mappings table
    op.create_table(
        'impact_mappings',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('regulation_id', sa.UUID(), nullable=False),
        sa.Column('policy_id', sa.UUID(), nullable=False),
        sa.Column('similarity', sa.Float(), nullable=True),
        sa.Column('impact_level', sa.String(20), nullable=False, server_default='MEDIUM'),
        sa.Column('llm_summary', sa.Text(), nullable=True),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('recommended_actions', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='OPEN'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['regulation_id'], ['regulations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['policy_id'], ['policies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_impact_mappings_policy_id', 'impact_mappings', ['policy_id'])
    op.create_index('ix_impact_mappings_regulation_id', 'impact_mappings', ['regulation_id'])

    # Create alerts table
    op.create_table(
        'alerts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('regulation_id', sa.UUID(), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False, server_default='MEDIUM'),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('acknowledged', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['regulation_id'], ['regulations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_alerts_acknowledged', 'alerts', ['acknowledged'])
    op.create_index('ix_alerts_regulation_id', 'alerts', ['regulation_id'])


def downgrade() -> None:
    """Downgrade schema - Drop all tables"""
    op.drop_index('ix_alerts_regulation_id', table_name='alerts')
    op.drop_index('ix_alerts_acknowledged', table_name='alerts')
    op.drop_table('alerts')
    op.drop_index('ix_impact_mappings_regulation_id', table_name='impact_mappings')
    op.drop_index('ix_impact_mappings_policy_id', table_name='impact_mappings')
    op.drop_table('impact_mappings')
    op.drop_index('ix_policies_title', table_name='policies')
    op.drop_index('ix_policies_department', table_name='policies')
    op.drop_table('policies')
    op.drop_index('ix_regulations_title', table_name='regulations')
    op.drop_index('ix_regulations_effective_date', table_name='regulations')
    op.drop_index('ix_regulations_category', table_name='regulations')
    op.drop_table('regulations')
