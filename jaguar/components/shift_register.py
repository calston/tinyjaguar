import RPi.GPIO as gpio

from twisted.internet import reactor, defer
from twisted.python import log

from jaguar import utils


class ShiftRegister(object):
    def __init__(self, serial, clock, latch, bits=8, frequency=0.1):
        self.serial = serial
        self.clock = clock
        self.latch = latch
        self.freq = frequency
        self.bits = bits

    def setup(self):
        gpio.setup(self.serial, gpio.OUT)
        gpio.setup(self.clock, gpio.OUT)
        gpio.setup(self.latch, gpio.OUT)

    def clear(self):
        return self.shiftOut(0)

    @defer.inlineCallbacks
    def shiftOut(self, val, msbf=True):
        gpio.output(self.latch, 0)

        if msbf:
            cnt = reversed(xrange(self.bits))
        else:
            cnt = xrange(self.bits)

        yield utils.wait(self.freq)

        for i in cnt:
            b = (val >> i) & 1

            gpio.output(self.clock, 0)
            gpio.output(self.serial, b)
            yield utils.wait(self.freq)
            gpio.output(self.clock, 1)

        gpio.output(self.clock, 0)
        yield utils.wait(self.freq)
        gpio.output(self.latch, 1)
        
