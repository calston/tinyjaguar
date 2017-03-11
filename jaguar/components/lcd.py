from twisted.internet import defer


class CharacterDisplay(object):

    DIR_MODE = 0x04
    DIR_LEFT = 0x00
    DIR_RIGHT = 0x02
    DIR_BLINK = 0x01

    CUR_MODE = 0x08
    CUR_DISPON = 0x04
    CUR_SHOW = 0x02
    CUR_BLINK=0x01

    FN_MODE = 0x20
    FN_8BIT = 0x10
    FN_4BIT = 0x00
    FN_1LINE = 0x00
    FN_2LINE = 0x08
    FN_FONT5x11 = 0x04
    FN_FONT5x8 = 0x00

    ROW = (0x00, 0x40, 0x14, 0x54)

    def __init__(self, shift_register):
        self.sr = shift_register

        self.out = self.sr.shiftOut
        self.buffer = 0x00

    @defer.inlineCallbacks
    def setup(self):
        self.sr.setup()

        yield self.lcd_init()
    
    @defer.inlineCallbacks
    def pulse_enable(self):
        yield self.out(self.buffer | 0x02)
        yield self.out(self.buffer)

    @defer.inlineCallbacks
    def lcd_send(self, b, cmd=False):
        br = (b >> 4, b)

        for b in br:
            self.buffer = (b << 4) | int(not cmd)

            yield self.out(b)

            yield self.pulse_enable()

    @defer.inlineCallbacks
    def lcd_init(self):
        yield self.lcd_send(0x33, cmd=True)
        yield self.lcd_send(0x32, cmd=True)
        yield self.lcd_send(self.FN_MODE | self.FN_4BIT | self.FN_2LINE | self.FN_FONT5x8, cmd=True)
        yield self.lcd_send(self.CUR_MODE | self.CUR_DISPON, cmd=True)
        yield self.clear()
        yield self.lcd_entry_mode()

    def lcd_entry_mode(self):
        return self.lcd_send(self.DIR_MODE | self.DIR_RIGHT, cmd=True)

    def lcd_dram_set(self, val):
        return self.lcd_send(0x80 | val, cmd=True)

    def clear(self):
        return self.lcd_send(0x01, cmd=True)

    def home(self):
        return self.lcd_send(0x02, cmd=True)

    def setCursor(self, row, col):
        return self.lcd_dram_set(self.ROW[row] + col)

    def newLine(self):
        return self.lcd_send(0xc0, cmd=True)

    @defer.inlineCallbacks
    def write(self, s):
        for c in s:
            if c == '\n':
                yield self.newLine()
            else:
                yield self.lcd_send(ord(c))

