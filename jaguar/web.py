import json
import inspect

from twisted.internet import defer
from twisted.web.template import renderer, XMLFile
from twisted.python.filepath import FilePath
from twisted.web.static import File

from twisted.web.template import tags

from .web_base import BaseResource, ContentElement, JSONResource


class API(JSONResource):
    isLeaf = True
    
    def get(self, request):
        members = dict([
            ('/api/' + n[5:].replace('_', '/'), m) for n,m in
            inspect.getmembers(self, predicate=inspect.ismethod)
            if n.startswith('call_')
        ])

        keys = members.keys()
        keys.sort(key=lambda n: len(n))

        for key in reversed(keys):
            if request.path.startswith(key):
                return members[key](request)

        return {'Err': 'No command'}

    def call_node_state(self, request):
        try:
            node = request.path.split('/')[-1]
            node = int(node)
        except:
            node = None

        if node:
            return {
                'node': node, 'state': self.service.states[node - 1], 
                'temps': self.service.temps[node - 1]
            }

        else:
            d = []
            for node in range(4):
                d.append({
                    'node': node + 1,
                    'state': self.service.states[node],
                    'temps': self.service.temps[node]
                })

            return d

    @defer.inlineCallbacks
    def call_node_on(self, request):
        node = request.path.split('/')[-1]
        node = int(node)

        yield self.service.nodeOn(node - 1)

        defer.returnValue({})

    @defer.inlineCallbacks
    def call_node_off(self, request):
        node = request.path.split('/')[-1]
        node = int(node)

        yield self.service.nodeOff(node - 1)

        defer.returnValue({})

    def call_system_state(self, request):
        return {
            'powergood': self.service.atxGood
        }

    def call_atx_on(self, request):
        self.service.atxOn.on()
        return {}

    def call_atx_off(self, request):
        self.service.atxOn.off()
        return {}

class Index(BaseResource):
    isLeaf = True

    class Content(ContentElement):
        loader = XMLFile(FilePath('jaguar/resources/index.html'))

