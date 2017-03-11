from twisted.internet import reactor, defer


def wait(msecs):
    d = defer.Deferred()
    reactor.callLater(msecs/1000.0, d.callback, None)
    return d

