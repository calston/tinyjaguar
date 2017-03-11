import RPi.GPIO as gpio

from twisted.internet import task, reactor, defer

from jaguar import utils


class MCP410x0(object):
    def __init__(self, cs, si, sck):
        self.cs = cs
        self.si = si
        self.sck = sck

    def setup(self):
        gpio.setup(self.cs, gpio.OUT)
        gpio.setup(self.si, gpio.OUT)
        gpio.setup(self.sck, gpio.OUT)
        gpio.output(self.cs, 1)
        gpio.output(self.sck, 0)
        gpio.output(self.cs, 0)

    @defer.inlineCallbacks
    def write_byte(self, val):
        for i in reversed(xrange(8)):
            gpio.output(self.sck, 0)
            gpio.output(self.si, (val >> i) & 1)
            yield utils.wait(0.01)
            gpio.output(self.sck, 1)

    @defer.inlineCallbacks
    def set(self, wiper):
        gpio.output(self.cs, 0)

        yield self.write_byte(0b00010001)
        yield self.write_byte(wiper)

        gpio.output(self.cs, 1)
