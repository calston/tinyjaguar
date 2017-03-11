from twisted.internet import defer


class SegmentDisplay(object):
    def __init__(self, serial, clock, latch):
        self.sr = ShiftRegister(serial, clock, latch)

        self.chars = {
            ' ': 0b00000000,
            '0': 0b01110111,
            '1': 0b01000100,
            '2': 0b01101011,
            '3': 0b01101110,
            '4': 0b01011100,
            '5': 0b00111110,
            '6': 0b00011111,
            '7': 0b01100100,
            '8': 0b01111111,
            '9': 0b01111100,
            '-': 0b00001000,
            'A': 0b01111101,
            'C': 0b00110011,
            'E': 0b00111011,
            'F': 0b00111001,
            'G': 0b01111110,
            'H': 0b01011101,
            'I': 0b00010001,
            'J': 0b01000110,
            'L': 0b00010011,
            'N': 0b00001101,
            'O': 0b00001111,
            'P': 0b01111001,
            'R': 0b00001001,
            'U': 0b01010111,
            'Y': 0b01011001,
        }

    @defer.inlineCallbacks
    def setup(self):
        self.sr.setup()
        yield self.display(0)
        defer.returnValue(None)

    @defer.inlineCallbacks
    def display(self, val):
        i = str(val).upper()
        if i in self.chars:
            v = self.chars[i]

            yield self.sr.shiftOut(v ^ 0b11111111)
        defer.returnValue(None)

