import json

from twisted.internet import defer
from twisted.web import server
from twisted.web.resource import Resource
from twisted.web.template import Element, renderer, XMLFile, tags, flattenString, TagLoader
from twisted.python.filepath import FilePath


class BaseElement(Element):
    loader = XMLFile(FilePath('jaguar/resources/base.html'))

    def __init__(self, service, content):
        Element.__init__(self)
        self.content_element = content
        self.service = service

    @renderer
    def header(self, request, tag):
        return tag('1')

    @renderer
    def footer(self, request, tag):
        return tag('2')

    @renderer
    def content(self, request, tag):
        yield self.content_element(self.service)
        #return tag("content")


class ContentElement(Element):
    def __init__(self, service):
        Element.__init__(self)
        self.service = service
        

class BaseResource(Resource):
    addSlash = True

    def __init__(self, service):
        Resource.__init__(self)
        self.service = service

    def completeCall(self, response, request):
        request.write(response)
        request.finish()

    def render_GET(self, request):
        flattenString(None, BaseElement(self.service, self.Content)
            ).addCallback(self.completeCall, request)

        return server.NOT_DONE_YET


class JSONResource(Resource):
    def __init__(self, service):
        Resource.__init__(self)
        self.service = service

    def completeCall(self, response, request):
        request.write(json.dumps(response))
        request.finish()

    def get(self, request):
        return ""

    def render_GET(self, request):
        request.setHeader("content-type", "application/json")

        d = defer.maybeDeferred(self.get, request)
        d.addCallback(self.completeCall, request)

        return server.NOT_DONE_YET

