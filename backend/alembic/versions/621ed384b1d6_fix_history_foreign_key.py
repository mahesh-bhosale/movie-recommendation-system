"""fix history foreign key

Revision ID: 621ed384b1d6
Revises: c41913980a6a
Create Date: 2025-03-28 05:51:28.569825

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '621ed384b1d6'
down_revision: Union[str, None] = 'c41913980a6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('history', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('history', 'movie_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_constraint('history_movie_id_fkey', 'history', type_='foreignkey')
    op.drop_constraint('history_user_id_fkey', 'history', type_='foreignkey')
    op.create_foreign_key(None, 'history', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'history', 'movies', ['movie_id'], ['id'], ondelete='CASCADE')
    op.alter_column('movies', 'title',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('movies', 'title',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.drop_constraint(None, 'history', type_='foreignkey')
    op.drop_constraint(None, 'history', type_='foreignkey')
    op.create_foreign_key('history_user_id_fkey', 'history', 'users', ['user_id'], ['id'])
    op.create_foreign_key('history_movie_id_fkey', 'history', 'movies', ['movie_id'], ['id'])
    op.alter_column('history', 'movie_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('history', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
