# gtfsrdb.py: load gtfs-realtime data to a database
# recommended to have the (static) GTFS data for the agency you are connecting
# to already loaded.

# Copyright 2011 Matt Conway

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Authors:
# Matt Conway: main code

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, Float
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

def add_schema(schema, data_classes=None):
    ''' will add the schema meta data to the __table__ element in the data access classes
        default list of classes are the subclasses of Base...
    '''
    # step 0: this is a schema name?
    if schema and len(schema) > 0:
        # step 1: make sure we have a list of classes ... default to Base subclasses
        if data_classes is None:
            data_classes = Base.__subclasses__()

        # step 2: set the schema meta data  
        for c in data_classes:
            if c and hasattr(c, '__table__'):
                c.__table__.schema = schema

# Collapsed types:
# TripUpdate.trip
# TripUpdate.vehicle
# StopTimeUpdate.arrival
# StopTimeUpdate.departure
# Alert.active_period
# Position.latitude
# Position.longitude
# Position.bearing
# Position.speed
# VehicleDescriptor.id
# VehicleDescriptor.label
# VehicleDescriptor.license_plate

# The oid is called oid because several of the GTFSr types have string ids
# TODO: add sequences

class TripUpdate(Base):
    __tablename__ = 'trip_updates'
    oid = Column(Integer, primary_key=True, index=True)

    # This replaces the TripDescriptor message
    # TODO: figure out the relations
    trip_id = Column(String(10), index=True)
    route_id = Column(String(10), index=True)
    trip_start_time = Column(String(8))
    trip_start_date = Column(String(10), index=True)
    # Put in the string value not the enum
    # TODO: add a domain
    schedule_relationship = Column(String(9))

    # Collapsed VehicleDescriptor
    vehicle_id = Column(String(10))
    vehicle_label = Column(String(15))
    vehicle_license_plate = Column(String(10))

    # moved from the header, and reformatted as datetime
    timestamp = Column(DateTime)

    StopTimeUpdates = relationship('StopTimeUpdate', backref='TripUpdate')

class StopTimeUpdate(Base):
    __tablename__ = 'stop_time_updates'
    oid = Column(Integer, primary_key=True, index=True)

    # TODO: Fill one from the other
    stop_sequence = Column(Integer)
    stop_id = Column(String(10), index=True)

    # Collapsed StopTimeEvent
    arrival_delay = Column(Integer)
    arrival_time = Column(Integer)
    arrival_uncertainty = Column(Integer)

    # Collapsed StopTimeEvent
    departure_delay = Column(Integer)
    departure_time = Column(Integer)
    departure_uncertainty = Column(Integer)

    # TODO: Add domain
    schedule_relationship = Column(String(9))

    # Link it to the TripUpdate
    trip_update_id = Column(Integer, ForeignKey('trip_updates.oid'))
    
    # The .TripUpdate is done by the backref in TripUpdate

class Alert(Base):
    __tablename__ = 'alerts'

    oid = Column(Integer, primary_key=True, index=True)

    # Collapsed TimeRange
    start = Column(Integer, index=True)
    end = Column(Integer)

    # Add domain
    cause = Column(String(20))
    effect = Column(String(20))

    url = Column(String(300))
    header_text = Column(String(80))
    description_text = Column(String(4000))

    # FXP added
    route_ids = Column(String(500))
    route_short_names = Column(String(1000))

    '''
    InformedEntities = relationship('EntitySelector', 
            backref='Alert', lazy='joined'
    )

    InformedEntities = relationship('EntitySelector',
        primaryjoin='EntitySelector.oid==Alert.oid',
        foreign_keys='(Alert.oid)',
        uselist=True, viewonly=True, backref='Alert')#, lazy='joined')
    '''

class EntitySelector(Base):
    __tablename__ = 'entity_selectors'
    oid = Column(Integer, primary_key=True, index=True)

    agency_id = Column(String(15), index=True)
    route_id = Column(String(10), index=True)

    route_type = Column(Integer)
    stop_id = Column(String(10))

    # Collapsed TripDescriptor
    trip_id = Column(String(10))
    trip_route_id = Column(String(10))
    trip_start_time = Column(String(8))
    trip_start_date = Column(String(10), index=True)

    alert_id = Column(Integer, ForeignKey('alerts.oid'))

    Alert = relationship('Alert', 
            lazy='joined',
            backref='InformedEntities'
    )



class VehiclePosition(Base):
    __tablename__ = 'vehicle_positions'
    oid = Column(Integer, primary_key=True, index=True)

    # This replaces the TripDescriptor message
    # TODO: figure out the relations
    trip_id = Column(String(10))
    route_id = Column(String(10))
    trip_start_time = Column(String(8))
    trip_start_date = Column(String(10))

    # Collapsed VehicleDescriptor
    vehicle_id = Column(String(10))
    vehicle_label = Column(String(15))
    vehicle_license_plate = Column(String(10))

    # Collapsed Position
    position_latitude = Column(Float)
    position_longitude = Column(Float)
    position_bearing = Column(Float)
    position_speed = Column(Float)

    # moved from the header, and reformatted as datetime
    timestamp = Column(DateTime)
   

# So one can loop over all classes to clear them for a new load (-o option)
AllClasses = (TripUpdate, StopTimeUpdate, Alert, EntitySelector, VehiclePosition)
