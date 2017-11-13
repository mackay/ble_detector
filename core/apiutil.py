from bottle import request, abort

import json
import datetime
import glob

from bottle import response

from core.models import BaseModel

import logging
log = logging.getLogger()


def get_configuration( config_filename=None ):
    return { "networks": glob.glob('*.network') }


def require_fields( field_list ):
    def require_fields_wrapper( func ):
        def require_fields_chain_fn(*args, **kwargs):
            if any(field not in request.json for field in field_list):
                message = "Missing required field in body.\n\nFields expected: {expected}\n\nFields supplied: {supplied}".format(
                    expected=str(field_list),
                    supplied=str(request.json.keys()) )

                print message
                abort(400, message)
            return func( *args, **kwargs )

        return require_fields_chain_fn
    return require_fields_wrapper


def timedelta_to_time( timedelta_obj ):

    #the ORM used to return non-time objects for time fields, and instead returned timedeltas
    #... so now that we are upgraded, until this function is completely unecessary, we're
    #   going to have to include this check to bypass accordingly
    if isinstance(timedelta_obj, datetime.time):
        return timedelta_obj

    seconds = int(timedelta_obj.seconds + (timedelta_obj.days * 24 * 3600))
    hours = seconds / 3600
    minutes = (seconds % 3600) / 60
    seconds = seconds % 60

    time = datetime.time(hours, minutes, seconds)
    return time


class SimpleSerializable(object):

    def to_JSON(self):
        return { }


class APIEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()  # + "Z"

        if isinstance(obj, datetime.time):
            return obj.isoformat()

        if isinstance(obj, datetime.timedelta):
            time = timedelta_to_time(obj)
            return time.isoformat()

        if isinstance(obj, datetime.datetime):
            return obj.isoformat() + "Z"
            #return int(mktime(obj.timetuple()))

        if isinstance(obj, BaseModel):
            return obj._data

        if isinstance(obj, SimpleSerializable):
            return obj.to_JSON()

        return json.JSONEncoder.default(self, obj)


class APISerializer():

    def __init__(self, object):
        self.object = object
        self.log = logging.getLogger()

    def json(self):
        return json.dumps( self.object, cls=APIEncoder, sort_keys=True )


#decorator for returning json data
def serialize_json( ):
    def serialize_json_wrapper( func ):
        def serialize_chain_fn(*args, **kwargs):
            model_object = func( *args, **kwargs )
            serializer = APISerializer(model_object)

            response.content_type = 'application/json'
            return serializer.json()

        return serialize_chain_fn
    return serialize_json_wrapper
