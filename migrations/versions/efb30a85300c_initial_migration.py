"""Initial migration

Revision ID: efb30a85300c
Revises: 
Create Date: 2023-06-20 12:15:56.744141

"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision = 'efb30a85300c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_geospatial_table('synop_station',
    sa.Column('wigos_id', sa.String(length=256), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('territory', sa.String(length=256), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('elevation', sa.Float(), nullable=True),
    sa.Column('geom', Geometry(geometry_type='POINT', srid=4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry'), nullable=False),
    sa.PrimaryKeyConstraint('wigos_id')
    )
    with op.batch_alter_table('synop_station', schema=None) as batch_op:
        batch_op.create_geospatial_index('idx_synop_station_geom', ['geom'], unique=False, postgresql_using='gist', postgresql_ops={})

    op.create_table('synop_observation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('wigos_id', sa.String(length=256), nullable=False),
    sa.Column('time', sa.DateTime(), nullable=False),
    sa.Column('non_coordinate_pressure', sa.Float(), nullable=True),
    sa.Column('characteristic_of_pressure_tendency', sa.Float(), nullable=True),
    sa.Column('non_coordinate_geopotential_height', sa.Float(), nullable=True),
    sa.Column('air_temperature', sa.Float(), nullable=True),
    sa.Column('dewpoint_temperature', sa.Float(), nullable=True),
    sa.Column('horizontal_visibility', sa.Float(), nullable=True),
    sa.Column('state_of_ground', sa.Float(), nullable=True),
    sa.Column('ground_minimum_temperature_past12hours', sa.Float(), nullable=True),
    sa.Column('present_weather', sa.Float(), nullable=True),
    sa.Column('past_weather1', sa.Float(), nullable=True),
    sa.Column('past_weather2', sa.Float(), nullable=True),
    sa.Column('total_sunshine', sa.Float(), nullable=True),
    sa.Column('minimum_temperature_at_height_and_over_period_specified', sa.Float(), nullable=True),
    sa.Column('maximum_wind_gust_speed', sa.Float(), nullable=True),
    sa.Column('wind_direction', sa.Float(), nullable=True),
    sa.Column('wind_speed', sa.Float(), nullable=True),
    sa.Column('pressure_reduced_to_mean_sea_level', sa.Float(), nullable=True),
    sa.Column('relative_humidity', sa.Float(), nullable=True),
    sa.Column('cloud_cover_total', sa.Float(), nullable=True),
    sa.Column('cloud_amount', sa.Float(), nullable=True),
    sa.Column('height_of_base_of_cloud', sa.Float(), nullable=True),
    sa.Column('cloud_type', sa.Float(), nullable=True),
    sa.Column('long_wave_radiation_integrated_over_period_specified', sa.Float(), nullable=True),
    sa.Column('pressure_change_24hour', sa.Float(), nullable=True),
    sa.Column('pressure_change_3hour', sa.Float(), nullable=True),
    sa.Column('evaporation', sa.Float(), nullable=True),
    sa.Column('other_weather_phenomena', sa.Float(), nullable=True),
    sa.Column('obscuration', sa.Float(), nullable=True),
    sa.Column('precipitation_type', sa.Float(), nullable=True),
    sa.Column('maximum_temperature_at_height_and_over_period_specified', sa.Float(), nullable=True),
    sa.Column('maximum_wind_gust_direction', sa.Float(), nullable=True),
    sa.Column('total_precipitation_or_total_water_equivalent', sa.Float(), nullable=True),
    sa.Column('extreme_counterclockwise_wind_direction_of_avariable_wind', sa.Float(), nullable=True),
    sa.Column('extreme_clockwise_wind_direction_of_avariable_wind', sa.Float(), nullable=True),
    sa.Column('global_solar_radiation_integrated_over_period_specified', sa.Float(), nullable=True),
    sa.Column('soil_temperature', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['wigos_id'], ['synop_station.wigos_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('wigos_id', 'time', name='unique_station_time')
    )
    op.create_table('synop_station_identifier',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('wigos_id', sa.String(length=256), nullable=False),
    sa.Column('identifier', sa.String(length=256), nullable=False),
    sa.ForeignKeyConstraint(['wigos_id'], ['synop_station.wigos_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('synop_station_identifier')
    op.drop_table('synop_observation')
    with op.batch_alter_table('synop_station', schema=None) as batch_op:
        batch_op.drop_geospatial_index('idx_synop_station_geom', postgresql_using='gist', column_name='geom')

    op.drop_geospatial_table('synop_station')
    # ### end Alembic commands ###