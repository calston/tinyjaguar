import copy
import exceptions
import json
import math
import time

try:
    import RPi.GPIO as gpio
except:
    gpio = None

from twisted.application import service
from twisted.internet import task, reactor, defer
from twisted.python import log
from twisted.python.filepath import FilePath
from twisted.web import server, resource
from twisted.web.static import File

from twisted.internet.utils import getProcessOutput

from .components import *
from . import web, utils


class JaguarService(service.Service):
    def __init__(self):
        self.t = None
        self.srval = 1

        self.sr = ShiftRegister(2, 8, 25, bits=16)

        self.red = (8, 4, 2, 1)
        self.green = (2048, 1024, 512, 256)
        self.yellow = (128, 64, 32, 16)

        self.nodes = [
            Output(23),
            Output(7),
            Output(22),
            Output(27)
        ]

        self.states = [0, 0, 0, 0]

        self.temps = [
            {'ambient': -1, 'cpu': -1},
            {'ambient': -1, 'cpu': -1},
            {'ambient': -1, 'cpu': -1},
            {'ambient': -1, 'cpu': -1}
        ]

        self.nlocks = [False, False, False, False]

        self.atxOn = Output(18)

        self.autoOn = False

        self.atxGood = False

        self.btnGreen = Button(17, self.greenButton)
        self.btnRed = Button(4, self.redButton)

        self.pwrGood = Button(11, self.powerGood)

    @defer.inlineCallbacks
    def setLEDStates(self):
        led = 0
        for i, s in enumerate(self.states):
            if s == 0:
                led = led | self.red[i]

            if s == 1:
                led = led | self.yellow[i]

            if s == 2:
                led = led | self.green[i]

        yield self.sr.shiftOut(led)

    @defer.inlineCallbacks
    def powerGood(self, state):
        if state == gpio.LOW:
            self.atxGood = True
            print "ATX Good"
            yield self.sr.shiftOut(reduce(lambda x, y: x | y, self.green))
            yield utils.wait(200)
            yield self.sr.shiftOut(0)
            yield utils.wait(100)
            yield self.sr.shiftOut(reduce(lambda x, y: x | y, self.green))
            yield utils.wait(200)
            yield self.setLEDStates()

            # Start node 1
            if self.autoOn:
                self.autoOn = False
                yield self.nodeOn(0)
        else:
            print "ATX bad"
            self.atxGood = False

    @defer.inlineCallbacks
    def nodeOff(self, node):
        n = self.nodes[node]
        n.off()
        self.states[node] = 0
        yield self.setLEDStates()

    @defer.inlineCallbacks
    def nodeOn(self, node):
        n = self.nodes[node]
        n.on()
        self.states[node] = 1
        yield self.setLEDStates()

    @defer.inlineCallbacks
    def powerOff(self):
        print "Off"
        if self.atxGood:
            if sum(self.states[1:]) > 0:
                for i in range(1, 4):
                    yield self.nodeOff(i)
                    yield utils.wait(100)
            
            else:
                yield self.nodeOff(0)
                self.atxOn.off()

    @defer.inlineCallbacks
    def greenButton(self, state):
        if state == gpio.LOW:
            o = reduce(lambda x, y: x | y, self.green)
            yield self.sr.shiftOut(o)
            self.autoOn = True

        else:
            # Button released
            yield self.setLEDStates()

            if self.states[0] == 2:
                self.autoOn = False
                # Node 1 is active, so start all the others
                for i in range(4):
                    yield self.nodeOn(i)
                    if i < 3:
                        yield utils.wait(1000)
            else:
                self.atxOn.on()

    @defer.inlineCallbacks
    def redButton(self, state):
        if state == gpio.LOW:
            o = reduce(lambda x, y: x | y, self.red)
            yield self.sr.shiftOut(o)

        else:
            yield self.setLEDStates()
            yield self.powerOff()

    
    @defer.inlineCallbacks
    def checkNode(self, node):
        out = yield getProcessOutput('/usr/bin/ssh-keyscan', args=('-T', '1', '10.0.1.%s' % node,), errortoo=1)

        if "OpenSSH" in out:
            defer.returnValue(True)
        defer.returnValue(False)

    @defer.inlineCallbacks
    def checkMonitor(self, node):
        # Check lock to prevent async call overlaps
        if not self.nlocks[node-1]:
            self.nlocks[node-1] = True
            try:
                out = yield getProcessOutput('/usr/bin/ssh', args=('10.0.1.%s' % node, 'monitor'), errortoo=1)
                out = json.loads(out)
                temp = []
                cpu = 0
                for d in out:
                    if 'temp1' in d:
                        temp.append(d['temp1'])
                    if 'temp2' in d:
                        cpu = d['temp2']
                    
                self.temps[node-1] = {'ambient': max(temp), 'cpu': cpu}
            except:
                pass
            self.nlocks[node-1] = False

    @defer.inlineCallbacks
    def loop(self):
        node_states = []
        for i in range(4):
            state = yield self.checkNode(i+1)
            node_states.append(state)

        cng = False
        for i, state in enumerate(node_states):
            if state:
                yield self.checkMonitor(i+1)

                if self.states[i] != 2:
                    self.states[i] = 2
                    cng = True
            if not state:
                self.states[i] = self.nodes[i].state
                self.temps[i] = {'ambient': -1, 'cpu': -1}

        #print "Node state:", self.states, "Power:", self.atxGood, "Auto:", self.autoOn, self.temps

        if cng:
            yield self.setLEDStates()

    @defer.inlineCallbacks
    def startService(self):
        root = resource.Resource()

        root.putChild('', web.Index(self))
        root.putChild('api', web.API(self))
        root.putChild("static", File(FilePath('jaguar/resources/static').path))

        site = server.Site(root, logPath='jaguar-access.log')

        reactor.listenTCP(80, site)

        gpio.setmode(gpio.BCM)

        self.sr.setup()
        yield self.sr.clear()
        yield utils.wait(1)
        yield self.sr.shiftOut(reduce(lambda x, y: x | y, self.red))

        self.btnGreen.setup()
        self.btnRed.setup()
        self.pwrGood.setup()
        self.atxOn.setup()

        for n in self.nodes:
            n.setup()
        yield utils.wait(1)

        if self.atxOn.state == gpio.LOW:
            yield self.powerGood(gpio.LOW)

        self.t = task.LoopingCall(self.loop)
        self.t.start(5.0)

    def stopService(self):
        print "Shutdown" 
