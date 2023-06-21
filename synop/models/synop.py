from geoalchemy2 import Geometry
from sqlalchemy import func

from synop import db


class Station(db.Model):
    __tablename__ = "synop_station"

    wigos_id = db.Column(db.String(256), primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    territory = db.Column(db.String(256), nullable=True)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    elevation = db.Column(db.Float, nullable=True)
    geom = db.Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)

    def __init__(self, wigos_id, name, longitude, latitude, territory=None, elevation=None):
        self.wigos_id = wigos_id
        self.name = name
        self.longitude = longitude
        self.latitude = latitude
        self.geom = func.ST_Point(self.longitude, self.latitude)

        self.territory = territory
        self.elevation = elevation

    def __repr__(self):
        return '<Station %r>' % self.name

    def serialize(self):
        """Return object data in easily serializable format"""
        station = {
            "wigos_id": self.id,
            "name": self.name,
        }

        return station


rename_columns = {
    "24hour_pressure_change": "pressure_change_24hour",
    "3hour_pressure_change": "pressure_change_3hour",
}

obs_columns = ['time', 'non_coordinate_pressure', 'characteristic_of_pressure_tendency',
               'non_coordinate_geopotential_height', 'air_temperature', 'dewpoint_temperature', 'horizontal_visibility',
               'state_of_ground', 'ground_minimum_temperature_past12hours', 'present_weather', 'past_weather1',
               'past_weather2', 'total_sunshine', 'minimum_temperature_at_height_and_over_period_specified',
               'maximum_wind_gust_speed', 'wind_direction', 'wind_speed', 'pressure_reduced_to_mean_sea_level',
               'relative_humidity', 'cloud_cover_total', 'cloud_amount', 'height_of_base_of_cloud', 'cloud_type',
               'long_wave_radiation_integrated_over_period_specified', '24hour_pressure_change',
               '3hour_pressure_change',
               'evaporation', 'other_weather_phenomena', 'obscuration', 'precipitation_type',
               'maximum_temperature_at_height_and_over_period_specified', 'maximum_wind_gust_direction',
               'total_precipitation_or_total_water_equivalent',
               'extreme_counterclockwise_wind_direction_of_avariable_wind',
               'extreme_clockwise_wind_direction_of_avariable_wind',
               'global_solar_radiation_integrated_over_period_specified', 'soil_temperature'
               ]


class Observation(db.Model):
    __tablename__ = "synop_observation"
    __table_args__ = (
        db.UniqueConstraint('wigos_id', 'time', name='unique_station_time'),
    )

    id = db.Column(db.Integer, primary_key=True)
    wigos_id = db.Column(db.String(256), db.ForeignKey('synop_station.wigos_id', ondelete="CASCADE"), nullable=False)
    time = db.Column(db.DateTime(), nullable=False)
    non_coordinate_pressure = db.Column(db.Float, nullable=True)
    characteristic_of_pressure_tendency = db.Column(db.Float, nullable=True)
    non_coordinate_geopotential_height = db.Column(db.Float, nullable=True)
    air_temperature = db.Column(db.Float, nullable=True)
    dewpoint_temperature = db.Column(db.Float, nullable=True)
    horizontal_visibility = db.Column(db.Float, nullable=True)
    state_of_ground = db.Column(db.Float, nullable=True)
    ground_minimum_temperature_past12hours = db.Column(db.Float, nullable=True)
    present_weather = db.Column(db.Float, nullable=True)
    past_weather1 = db.Column(db.Float, nullable=True)
    past_weather2 = db.Column(db.Float, nullable=True)
    total_sunshine = db.Column(db.Float, nullable=True)
    minimum_temperature_at_height_and_over_period_specified = db.Column(db.Float, nullable=True)
    maximum_wind_gust_speed = db.Column(db.Float, nullable=True)
    wind_direction = db.Column(db.Float, nullable=True)
    wind_speed = db.Column(db.Float, nullable=True)
    pressure_reduced_to_mean_sea_level = db.Column(db.Float, nullable=True)
    relative_humidity = db.Column(db.Float, nullable=True)
    cloud_cover_total = db.Column(db.Float, nullable=True)
    cloud_amount = db.Column(db.Float, nullable=True)
    height_of_base_of_cloud = db.Column(db.Float, nullable=True)
    cloud_type = db.Column(db.Float, nullable=True)
    long_wave_radiation_integrated_over_period_specified = db.Column(db.Float, nullable=True)
    pressure_change_24hour = db.Column(db.Float, nullable=True)
    pressure_change_3hour = db.Column(db.Float, nullable=True)
    evaporation = db.Column(db.Float, nullable=True)
    other_weather_phenomena = db.Column(db.Float, nullable=True)
    obscuration = db.Column(db.Float, nullable=True)
    precipitation_type = db.Column(db.Float, nullable=True)
    maximum_temperature_at_height_and_over_period_specified = db.Column(db.Float, nullable=True)
    maximum_wind_gust_direction = db.Column(db.Float, nullable=True)
    total_precipitation_or_total_water_equivalent = db.Column(db.Float, nullable=True)
    extreme_counterclockwise_wind_direction_of_avariable_wind = db.Column(db.Float, nullable=True)
    extreme_clockwise_wind_direction_of_avariable_wind = db.Column(db.Float, nullable=True)
    global_solar_radiation_integrated_over_period_specified = db.Column(db.Float, nullable=True)
    soil_temperature = db.Column(db.Float, nullable=True)

    def __init__(self, **kwargs):
        for column in list(kwargs):
            if rename_columns.get(column):
                new_col_name = rename_columns.get(column)
                kwargs.update({new_col_name: kwargs[column]})
                column = new_col_name

            if hasattr(self, column):
                setattr(self, column, kwargs[column])

    def serialize(self):
        """Return object data in easily serializable format"""

        obs = {
            "wigos_id": self.wigos_id
        }

        return obs


class StationIdentifier(db.Model):
    __tablename__ = "synop_station_identifier"

    id = db.Column(db.Integer, primary_key=True)
    wigos_id = db.Column(db.String(256), db.ForeignKey('synop_station.wigos_id', ondelete="CASCADE"), nullable=False)
    identifier = db.Column(db.String(256), nullable=False)
