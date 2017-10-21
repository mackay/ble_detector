from peewee import *

database = SqliteDatabase('detector.db')


def before_request_handler():
    database.connect()


def after_request_handler():
    database.close()


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


class Detector(BaseModel):
    uuid = CharField(max_length=64, unique=True)
    last_active = DateTimeField(null=True)
    total_packets = IntegerField(default=0)
    metadata = JSONField(null=True)

    class Meta:
        order_by = ('uuid', )


def initialize():
    database.connect()
    databse.create_tables([ Detector ], safe=True)
    database.disconnect()
