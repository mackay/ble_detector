from peewee import *

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
    pass


class Signal(BaseModel):
    detector = ForeignKeyField(rel_model=Detector)
    beacon = ForeignKeyField(rel_model=Beacon)
    rssi = FloatField()
    source_data = CharField(max_length=255, null=True)


def initialize():
    database.connect()
    database.create_tables([ Detector, Beacon, Signal ], safe=True)
    database.create_tables([ SystemOption ], safe=True)
    database.close()
