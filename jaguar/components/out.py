import RPi.GPIO as gpio

from twisted.internet import reactor, defer, task
from twisted.python import log


class Output(object):
    def __init__(self, pin, state=0):
        self.pin = pin
        self.state = state

    def setup(self):
        gpio.setup(self.pin, gpio.OUT)
        #gpio.output(self.pin, self.state)

    def on(self):
        self.state = 1
        gpio.output(self.pin, self.state)

    def off(self):
        self.state = 0
        gpio.output(self.pin, self.state)
