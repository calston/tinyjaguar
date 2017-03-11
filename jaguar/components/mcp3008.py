import RPi.GPIO as GPIO

 
class MCP3008(object):
    def __init__(self, clock_pin, mosi_pin, miso_pin, cs_pin):
        self.clock_pin = clock_pin
        self.mosi_pin = mosi_pin
        self.miso_pin = miso_pin
        self.cs_pin = cs_pin

    def setup(self):
        GPIO.setup(self.mosi_pin, GPIO.OUT)
        GPIO.setup(self.miso_pin, GPIO.IN)
        GPIO.setup(self.clock_pin, GPIO.OUT)
        GPIO.setup(self.cs_pin, GPIO.OUT)
 
    def read(self, channel):
        if ((channel > 7) or (channel < 0)):
            return -1

        GPIO.output(self.cs_pin, True)

        GPIO.output(self.clock_pin, False)  # start clock low
        GPIO.output(self.cs_pin, False)     # bring CS low

        commandout = channel
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here

        for i in range(5):
            if (commandout & 0x80):
                GPIO.output(self.mosi_pin, True)
            else:
                GPIO.output(self.mosi_pin, False)
            commandout <<= 1
            GPIO.output(self.clock_pin, True)
            GPIO.output(self.clock_pin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
            GPIO.output(self.clock_pin, True)
            GPIO.output(self.clock_pin, False)
            adcout <<= 1
            if (GPIO.input(self.miso_pin)):
                adcout |= 0x1

        GPIO.output(self.cs_pin, True)
        
        adcout >>= 1       # first bit is 'null' so drop it

        return adcout
