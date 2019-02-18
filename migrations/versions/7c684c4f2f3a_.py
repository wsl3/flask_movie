"""empty message

Revision ID: 7c684c4f2f3a
Revises: a8a694aa5797
Create Date: 2019-02-17 15:26:59.567965

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7c684c4f2f3a'
down_revision = 'a8a694aa5797'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('category', 'type',
               existing_type=mysql.VARCHAR(length=30),
               nullable=False)
    op.alter_column('comment', 'body',
               existing_type=mysql.TEXT(),
               nullable=False)
    op.alter_column('movie', 'title',
               existing_type=mysql.VARCHAR(length=120),
               nullable=False)
    op.drop_column('movie', 'kind')
    op.drop_column('movie', 'episodes')
    op.alter_column('user', 'email',
               existing_type=mysql.VARCHAR(length=30),
               nullable=False)
    op.alter_column('user', 'password',
               existing_type=mysql.VARCHAR(length=120),
               nullable=False)
    op.alter_column('user', 'username',
               existing_type=mysql.VARCHAR(length=100),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'username',
               existing_type=mysql.VARCHAR(length=100),
               nullable=True)
    op.alter_column('user', 'password',
               existing_type=mysql.VARCHAR(length=120),
               nullable=True)
    op.alter_column('user', 'email',
               existing_type=mysql.VARCHAR(length=30),
               nullable=True)
    op.add_column('movie', sa.Column('episodes', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.add_column('movie', sa.Column('kind', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.alter_column('movie', 'title',
               existing_type=mysql.VARCHAR(length=120),
               nullable=True)
    op.alter_column('comment', 'body',
               existing_type=mysql.TEXT(),
               nullable=True)
    op.alter_column('category', 'type',
               existing_type=mysql.VARCHAR(length=30),
               nullable=True)
    # ### end Alembic commands ###