"""Add vector column and chunk_index to document_chunks

Revision ID: 002
Revises: 001
Create Date: 2025-08-19

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add chunk_index column
    op.add_column('document_chunks', sa.Column('chunk_index', sa.Integer(), nullable=False, server_default='0'))
    
    # The embedding column is already created in migration 001, so we skip it
    # Just ensure the HNSW index exists with a specific name
    op.execute('CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding ON document_chunks USING hnsw (embedding vector_l2_ops)')


def downgrade() -> None:
    # Drop the vector index
    op.execute('DROP INDEX IF EXISTS idx_document_chunks_embedding')
    
    # Don't drop the embedding column as it was created in migration 001
    # Only drop the chunk_index column that we added in this migration
    op.drop_column('document_chunks', 'chunk_index')