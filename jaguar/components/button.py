import RPi.GPIO as gpio

from twisted.internet import reactor, defer, task
from twisted.python import log


class Button(object):
    def __init__(self, pin, action):
        self.pin = pin
        self.action = action
        self.state = None

    def setup(self):
        gpio.setup(self.pin, gpio.IN, gpio.PUD_UP)
        self.state = gpio.input(self.pin)

        self.t = task.LoopingCall(self.loop)
        self.t.start(0.1)

    @defer.inlineCallbacks
    def loop(self):
        state = gpio.input(self.pin)
        if state != self.state:
            self.state = state
            yield defer.maybeDeferred(self.action, state)
