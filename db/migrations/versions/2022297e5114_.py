"""empty message

Revision ID: 2022297e5114
Revises: 3dc1213b9539
Create Date: 2015-03-26 21:56:55.262955

"""

# revision identifiers, used by Alembic.
revision = '2022297e5114'
down_revision = '3dc1213b9539'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('category', sa.Column('local_id', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('category', 'local_id')
    ### end Alembic commands ###