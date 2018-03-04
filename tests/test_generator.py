import unittest
import zmq
import threading
import json
from CardenalGenerator.generator import CardenalGenerator


class MockServer(object):

    def __init__(self,
                 command_port=6666,
                 command_poller_timeout=5):

        self._context = zmq.Context()
        self._command_socket = self._context.socket(zmq.REP)
        self._command_socket.bind("tcp://*:{0}".format(command_port))
        self._command_poller = zmq.Poller()
        self._command_poller_timeout = command_poller_timeout
        self._command_poller.register(self._command_socket)
        self._stop = False
        self._thread = threading.Thread(target=self.check_msgs)
        self._thread.start()

    def stop(self):
        self._stop = True
        self._thread.join()
        self._command_socket.close()
        self._context.term()

    def check_msgs(self):
        while not self._stop:
            socks = self._command_poller.poll(self._command_poller_timeout)
            for socket, _ in socks:
                try:
                    msg = socket.recv_json()
                    if type(msg) is not dict:
                        raise TypeError
                except (json.decoder.JSONDecodeError, TypeError) as e:
                    socket.send_json({
                        'status': 500,
                        'msg': "Error en formato del comando."})
                    continue
                if 'msg' not in msg.keys():
                    socket.send_json({
                        'status': 501,
                        'msg': "No se especificó un mensaje para la "
                               "notificación."
                    })
                    continue

                if 'generator' not in msg.keys():
                    socket.send_json({
                        'status': 502,
                        'msg': 'No se especificó el nombre del generador'})
                    continue
                socket.send_json({
                    'status': 200,
                    'msg': "Notificación creada correctamente"})


class ClientTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server = MockServer()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def setUp(self):
        self.client = CardenalGenerator("generator", 'localhost')

    def tearDown(self):
        self.client.stop()

    def test_one_txt_msg(self):
        rta = self.client.send_message("prueba")
        self.assertEqual(rta['status'], 200)

    def test_1000_txt_msg(self):
        count = 0
        for i in range(0, 1000):
            rta = self.client.send_message("Mensaje {}".format(i))
            self.assertEqual(rta['status'], 200, "Message {0} failed".format(i))
            count += 1
        self.assertEqual(count, 1000)
