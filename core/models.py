from peewee import *

import json
from datetime import datetime

#set sane default log levels
import logging
logging.getLogger('peewee').setLevel(logging.INFO)
logging.getLogger("peewee.pool").setLevel(logging.DEBUG)

database = SqliteDatabase('detector.db')


class JSONField(TextField):
    def db_value(self, value):
        if value is not None:
            return json.dumps(value)

        return None

    def python_value(self, value):
        if value is not None:
            return json.loads(value)


class BaseModel(Model):
    def __init__(self, *args, **kwargs):
        super(BaseModel, self).__init__( *args, **kwargs )
        self._meta.base_uri = self._meta.db_table

    class Meta:
        database = database
        base_uri = "unknown"


class SystemOption(BaseModel):
    key = CharField(max_length=64, unique=True, index=True)
    value = CharField(max_length=255)


class ActiveEntity(BaseModel):
    uuid = CharField(max_length=64, unique=True, index=True)
    last_active = DateTimeField(null=True)
    total_packets = IntegerField(default=0)
    metadata = JSONField(null=True)

    class Meta:
        order_by = ('uuid', )


class Detector(ActiveEntity):
    pass


class Beacon(ActiveEntity):
    is_accepted = IntegerField(default=0)


class Agent(ActiveEntity):
    pass


class Signal(BaseModel):
    date = DateTimeField(default=datetime.utcnow)
    detector = ForeignKeyField(rel_model=Detector)
    beacon = ForeignKeyField(rel_model=Beacon)
    rssi = FloatField()
    source_data = CharField(max_length=255, null=True)


class Training(BaseModel):
    date = DateTimeField(default=datetime.utcnow)
    beacon = ForeignKeyField(rel_model=Beacon)
    expectation = JSONField()
    is_used = IntegerField(default=1)

    class Meta:
        order_by = ('date', 'expectation', 'beacon')


class TrainingSignal(BaseModel):
    training = ForeignKeyField(rel_model=Training, related_name='signals')
    signal = ForeignKeyField(rel_model=Signal)


def initialize():
    database.connect()

    database.create_tables([ SystemOption ], safe=True)
    database.create_tables([ Detector, Beacon, Agent ], safe=True)
    database.create_tables([ Signal ], safe=True)
    database.create_tables([ Training, TrainingSignal ], safe=True)

    database.close()
