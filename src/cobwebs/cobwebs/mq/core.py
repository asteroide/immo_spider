from cobwebs import exceptions


class Driver(object):
    rpc = None
    topics = None


class RPCLink:

    def run_server(self, key, callback, endpoint):
        raise exceptions.NotImplementedException  # noqa

    def send(self, key, data, endpoint):
        raise exceptions.NotImplementedException  # noqa


class TopicsLink:

    def run_server(self, key, callback, endpoint):
        raise exceptions.NotImplementedException  # noqa

    def emit(self, topic, message, endpoint):
        raise exceptions.NotImplementedException  # noqa
