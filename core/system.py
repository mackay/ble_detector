from bunch import Bunch
from core.models import SystemOption


class SystemBase(object):

    MODE_KEY = "mode"
    MODES = Bunch({
        "OFF": "off",
        "RUN": "run",
        "TRAINING": "training",
        "TESTING": "testing",
        "DEMO": "demo"
    })

    FILTER_KEY = "filter-data"
    TRAINING_KEY = "training-data"

    def __init__(self):
        pass

    def set_option(self, key, value):
        try:
            system_option = SystemOption.get(SystemOption.key == key)
        except:
            system_option = SystemOption()

        system_option.value = value
        system_option.key = key
        system_option.save()

        return system_option

    def get_options(self):
        return { option.key: option.value for option in SystemOption.select() }

    def get_option(self, key, default=None):
        try:
            return SystemOption.get(SystemOption.key == key).value
        except:
            return default

    def is_mode(self, mode):
        return self.get_option(SystemBase.MODE_KEY) == mode

    def is_mode_off(self):
        return self.is_mode(SystemBase.MODES.OFF)
