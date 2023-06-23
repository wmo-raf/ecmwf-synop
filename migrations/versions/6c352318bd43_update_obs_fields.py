"""Update obs fields

Revision ID: 6c352318bd43
Revises: 33e171f6a4b9
Create Date: 2023-06-23 14:22:46.215990

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6c352318bd43'
down_revision = '33e171f6a4b9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('synop_observation', schema=None) as batch_op:
        batch_op.add_column(sa.Column('wind_direction_at10m', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('wind_speed_at10m', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('air_temperature_at2m', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('dewpoint_temperature_at2m', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('total_precipitation_past3hours', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('non_coordinate_geopotential', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('total_precipitation_past1hour', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('total_precipitation_past12hours', sa.Float(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('synop_observation', schema=None) as batch_op:
        batch_op.drop_column('total_precipitation_past12hours')
        batch_op.drop_column('total_precipitation_past1hour')
        batch_op.drop_column('non_coordinate_geopotential')
        batch_op.drop_column('total_precipitation_past3hours')
        batch_op.drop_column('dewpoint_temperature_at2m')
        batch_op.drop_column('air_temperature_at2m')
        batch_op.drop_column('wind_speed_at10m')
        batch_op.drop_column('wind_direction_at10m')

    # ### end Alembic commands ###