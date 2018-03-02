import zmq
import json

DEFAULT_POLLER_TIMEOUT = 2000
DEFAULT_PORT = 6666


class CardenalClient(object):

    def __init__(self, ip, timeout=DEFAULT_POLLER_TIMEOUT, port=DEFAULT_PORT):
        self.ip = ip
        self.port = port
        self.poller_timeout = timeout
        self._init_socket()

    def _init_socket(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect('tcp://%s:%d' % (self.ip, self.port))
        self.poller = zmq.Poller()
        self.poller.register(self.socket)

    def stop(self):
        self.socket.close()
        self.context.term()

    def _reset_socket(self):
        self.stop()
        self._init_socket()

    def txt_msg(self, msg, user_id=None, username=None):
        if user_id is None and username is None:
            raise ValueError(
                "Se debe especificar username o user_id como parámetros")

        self.socket.send_json({
            'msg': msg,
            'user_id': user_id,
            'username': username})
        socks = self.poller.poll(self.poller_timeout)
        if not len(socks):
            return None
        return socks[0][0].recv_json()
