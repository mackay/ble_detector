
IDLE_MIN_MS = 1


class BaseActionDelegate(object):
    def __init__(self):
        pass

    def act(self):
        pass


class TimedAction(object):

    def __init__(self, action_delegate, action_rate_ms):
        self.action = action_delegate

        self.action_rate_ms = abs(action_rate_ms)
        self.reset()

    def reset(self):
        self.trigger_ms = 0

    def tick(self, elapsed_time_ms):
        self.trigger_ms += elapsed_time_ms

        if self.trigger_ms > self.action_rate_ms:
            self.action_delegate.act()
            self.trigger_ms = 0


class ContinualTimedAction(TimedAction):

    def tick(self, elapsed_time_ms):
        self.trigger_ms += elapsed_time_ms

        while self.trigger_ms > self.action_rate_ms:
            self.action_delegate.act()
            self.trigger_ms -= self.action_rate_ms
