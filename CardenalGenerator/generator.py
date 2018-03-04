import zmq

DEFAULT_POLLER_TIMEOUT = 2000
DEFAULT_PORT = 6666


class CardenalGenerator(object):

    def __init__(self, name, server,
                 timeout=DEFAULT_POLLER_TIMEOUT, port=DEFAULT_PORT):
        self.name = name
        self.server = server
        self.port = port
        self.poller_timeout = timeout
        self._init_socket()

    def _init_socket(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect('tcp://%s:%d' % (self.server, self.port))
        self.poller = zmq.Poller()
        self.poller.register(self.socket)

    def stop(self):
        self.socket.close()
        self.context.term()

    def _reset_socket(self):
        self.stop()
        self._init_socket()

    def txt_msg(self, msg):
        self.socket.send_json({
            'msg': msg,
            'generator': self.name,
        })
        socks = self.poller.poll(self.poller_timeout)
        if not len(socks):
            return None
        return socks[0][0].recv_json()
