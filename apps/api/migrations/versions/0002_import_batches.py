"""add import batches

Revision ID: 0002_import_batches
Revises: 0001_initial
Create Date: 2026-06-29
"""

from alembic import op

revision = "0002_import_batches"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS import_batches (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            source VARCHAR(80) NOT NULL,
            original_filename VARCHAR(255) NOT NULL,
            stored_path TEXT,
            status VARCHAR(40) NOT NULL DEFAULT 'received',
            total_rows INTEGER NOT NULL DEFAULT 0,
            processed_rows INTEGER NOT NULL DEFAULT 0,
            skipped_rows INTEGER NOT NULL DEFAULT 0,
            errors JSON NOT NULL DEFAULT '[]'::json,
            created_at TIMESTAMPTZ DEFAULT now(),
            completed_at TIMESTAMPTZ
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_import_batches_user_id ON import_batches(user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_import_batches_source ON import_batches(source)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_import_batches_status ON import_batches(status)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_import_batches_created_at ON import_batches(created_at)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS import_batches")
