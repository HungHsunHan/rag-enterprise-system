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
    
    # Add embedding column with vector type
    op.execute('ALTER TABLE document_chunks ADD COLUMN embedding vector(384)')
    
    # Create HNSW index for vector similarity search
    op.execute('CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding ON document_chunks USING hnsw (embedding vector_l2_ops)')


def downgrade() -> None:
    # Drop the vector index
    op.execute('DROP INDEX IF EXISTS idx_document_chunks_embedding')
    
    # Drop the embedding column
    op.drop_column('document_chunks', 'embedding')
    
    # Drop chunk_index column
    op.drop_column('document_chunks', 'chunk_index')