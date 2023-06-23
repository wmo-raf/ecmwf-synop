"""make station territory nullable

Revision ID: 33e171f6a4b9
Revises: efb30a85300c
Create Date: 2023-06-21 21:52:19.588188

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '33e171f6a4b9'
down_revision = 'efb30a85300c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('synop_station', schema=None) as batch_op:
        batch_op.alter_column('territory',
               existing_type=sa.VARCHAR(length=256),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('synop_station', schema=None) as batch_op:
        batch_op.alter_column('territory',
               existing_type=sa.VARCHAR(length=256),
               nullable=False)

    # ### end Alembic commands ###