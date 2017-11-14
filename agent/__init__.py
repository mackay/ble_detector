import json
import threading
import time
from datetime import datetime

from core.time import IDLE_MIN_MS
from remote.api import API


class AgentRunException(Exception):
    pass


class Agent(object):

    def __init__(self, uuid):
        self.uuid = uuid
        self.run_enable = False
        self.run_thread = None

    def load_state_from_file(self, json_file_path):
        json_data = open(json_file_path)
        data = json.load(json_data)
        json_data.close()

        self.state = data

    def _setup(self):
        pass

    def _teardown(self):
        pass

    def run(self, callback=None):
        if self.run_enable or self.run_thread:
            raise AgentRunException("Agent already running.")

        self.run_enable = True

        t = threading.Thread( name='agent_run_loop',
                              target=self._run_loop,
                              args=(callback,),
                              kwargs=None )
        self.run_thread = t
        t.start()

    def _run_loop(self, callback=None):
        self._setup()

        timing_previous = datetime.utcnow()
        while self.run_enable:

            #per step timing
            timing_current = datetime.utcnow()
            elapsed_time_ms = float( (timing_current - timing_previous).microseconds / 1000. )
            timing_previous = timing_current

            #agent process of observe-reason-act
            self.observe(elapsed_time_ms)
            self.reason(elapsed_time_ms)
            self.act(elapsed_time_ms)

            if elapsed_time_ms < IDLE_MIN_MS:
                time.sleep(0.001)

        self._teardown()

    def observe(self, elapsed_time_ms):
        pass

    def reason(self, elapsed_time_ms):
        pass

    def act(self, elapsed_time_ms):
        pass

    def stop(self):
        self.run_enable = False
        if self.run_thread:
            self.run_thread.join()


class StatefulAgent(Agent):

    STATE_RUN_TIME_HRS = "runtime_hrs"
    STATE_UUID = "uuid"

    def __init__(self, uuid, initial_state={}):
        super(StatefulAgent, self).__init__(uuid)
        self.state = initial_state
        self._set_state(StatefulAgent.STATE_UUID, self.uuid)

    def load_state_from_file(self, json_file_path):
        json_data = open(json_file_path)
        data = json.load(json_data)
        json_data.close()

        self.state = data

    def _get_state(self, key, default=None):
        if key in self.state:
            return self.state[key]

        return default

    def _set_state(self, key, value):
        self.state[key] = value

    def _setup(self):
        self._set_state(StatefulAgent.STATE_RUN_TIME_HRS, 0)

    def reason(self, elapsed_time_ms):
        super(StatefulAgent, self).reason(elapsed_time_ms)

        self._increment_runtime(elapsed_time_ms)

    def _increment_runtime(self, elapsed_time_ms):
        elapsed_hrs = self._get_state(StatefulAgent.STATE_RUN_TIME_HRS, 0)
        elapsed_hrs += float(elapsed_time_ms) / 1000 / 60 / 60
        self._set_state(StatefulAgent.STATE_RUN_TIME_HRS, elapsed_hrs)


class BeaconAgent(StatefulAgent):

    STATE_TRIGGER_TIME = "trigger_time_ms"
    STATE_STALE_TIME = "stale_time_ms"

    @classmethod
    def _beacon_key(cls, beacon):
        return str(beacon["uuid"])

    @classmethod
    def _beacon_record(cls, beacon):
        return { "beacon": beacon,
                 "last_heard_ms": 0.,
                 "trigger_ms": 0. }

    def __init__(self, uuid, stale_time_ms=5*1000, trigger_time_ms=500, state={}):
        super(BeaconAgent, self).__init__(uuid, state)

        self.beacons = { }
        self.trigger_time_ms = trigger_time_ms
        self.stale_time_ms = stale_time_ms

        if self.stale_time_ms:
            self.stale_time_ms = float(self.stale_time_ms)

        if self.trigger_time_ms:
            self.trigger_time_ms = float(self.trigger_time_ms)

    def _setup(self):
        self.trigger_time_ms = self._get_state( BeaconAgent.STATE_TRIGGER_TIME, self.trigger_time_ms)
        self.stale_time_ms = self._get_state( BeaconAgent.STATE_STALE_TIME, self.stale_time_ms)

        self._set_state(BeaconAgent.STATE_SPRITE_COUNT, 0)
        self._set_state(BeaconAgent.STATE_RUN_TIME_HRS, 0)

    def reason(self, elapsed_time_ms):
        super(BeaconAgent, self).reason(elapsed_time_ms)

        self.clean_stale_beacons()
        self.update_beacon_life(elapsed_time_ms)

    def act(self, elapsed_time_ms):
        super(BeaconAgent, self).act(elapsed_time_ms)

        for beacon in self.get_actable_beacons():
            self.act_on_beacon(beacon)

    def refresh_beacon(self, beacon):
        key = BeaconAgent._beacon_key(beacon)
        if key not in self.beacons:
            self.beacons[key] = BeaconAgent._beacon_record(beacon)

        self.beacons[key]["beacon"] = beacon
        self.beacons[key]["last_heard_ms"] = 0.

    def update_beacon_life(self, elapsed_time_ms):
        for key in self.beacons.keys():
            self.beacons[key]["last_heard_ms"] += elapsed_time_ms
            self.beacons[key]["trigger_ms"] -= elapsed_time_ms

    def clean_stale_beacons(self):
        if self.stale_time_ms is None:
            return

        for key in self.beacons.keys():
            if self.beacons[key]["last_heard_ms"] >= self.stale_time_ms:
                self.beacons.pop(key)

    def get_actable_beacons(self):
        actable = [ ]

        for key in self.beacons.keys():
            if self.beacons[key]["trigger_ms"] <= 0:
                actable.append(self.beacons[key]["beacon"])

        return actable

    def act_on_beacon(self, beacon):
        key = BeaconAgent._beacon_key(beacon)
        self.beacons[key]["trigger_ms"] = self.trigger_time_ms


class HTTPBeaconAgent(BeaconAgent):

    def __init__(self, uuid, api_url, refresh_max_rate_ms=250, stale_time_ms=5*1000, trigger_time_ms=500, state={}):
        super(HTTPBeaconAgent, self).__init__( uuid,
                                               stale_time_ms=stale_time_ms,
                                               trigger_time_ms=trigger_time_ms,
                                               state=state )
        self.api_url = api_url
        self.api = API(self.api_url, ignore_errors=True)

        self.refresh_max_rate_ms = refresh_max_rate_ms
        self.refresh_trigger_ms = 0
        self.checkin_trigger_ms = 0

    def observe(self, elapsed_time_ms):
        super(HTTPBeaconAgent, self).observe(elapsed_time_ms)

        if self.refresh_trigger_ms <= 0:
            beacons = self.get_active_beacons()
            for beacon in beacons:
                self.refresh_beacon(beacon)

            self.refresh_trigger_ms = self.refresh_max_rate_ms

        else:
            self.refresh_trigger_ms -= elapsed_time_ms

    def act(self, elapsed_time_ms):
        super(HTTPBeaconAgent, self).act(elapsed_time_ms)

        if self.checkin_trigger_ms <= 0:
            self.checkin()
            self.checkin_trigger_ms = self.refresh_max_rate_ms * 10

    def checkin(self):
        self.api.checkin_agent(self.uuid, metadata=self.state)

    def get_active_beacons(self):
        beacons = self.api.get_active_beacons(self.stale_time_ms)
        return beacons
