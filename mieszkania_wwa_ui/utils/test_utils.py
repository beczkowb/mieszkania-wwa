import socket
from django.test import TestCase, Client
from http.server import HTTPServer
from threading import Thread


class MockedTestCase(TestCase):
    @classmethod
    def get_free_port(cls):
        s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
        s.bind(('localhost', 0))
        address, port = s.getsockname()
        s.close()
        return port

    @classmethod
    def setUpClass(cls):
        cls.client = Client()
        cls.mock_server_port = cls.get_free_port()
        cls.mock_server = HTTPServer(('localhost', cls.mock_server_port),
                                     cls.mock_server_request_handler())

        cls.mock_server_thread = Thread(target=cls.mock_server.serve_forever)
        cls.mock_server_thread.setDaemon(True)
        cls.mock_server_thread.start()

    @classmethod
    def mock_server_request_handler(cls):
        raise RuntimeError("Not implemented")

    @classmethod
    def tearDownClass(cls):
        pass


def e2e(o):
    return o