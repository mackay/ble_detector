
IDLE_MIN_MS = 1


class BaseActionDelegate(object):
    def __init__(self):
        pass

    def act(self):
        pass


class TimedAction(object):

    def __init__(self, action_delegate, trigger_ms):
        self.action = action_delegate

        self.trigger_ms = abs(trigger_ms)
        self.counter_ms = 0

    def reset(self):
        self.counter_ms = 0

    def tick(self, elapsed_time_ms):
        self.counter_ms += elapsed_time_ms

        if self.counter_ms > self.trigger_ms:
            self.action_delegate.act()
            self.counter_ms = 0


class ContinualTimedAction(TimedAction):

    def tick(self, elapsed_time_ms):
        self.counter_ms += elapsed_time_ms

        while self.counter_ms > self.trigger_ms:
            self.action_delegate.act()
            self.counter_ms -= self.trigger_ms
