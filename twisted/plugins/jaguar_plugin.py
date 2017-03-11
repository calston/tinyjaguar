from zope.interface import implements
 
from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
 
import jaguar
 
class Options(usage.Options):
    optParameters = [
    ]
 
class JaguarServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "jaguar"
    description = "jaguar"
    options = Options
 
    def makeService(self, options):
        return jaguar.makeService()
 
serviceMaker = JaguarServiceMaker()
