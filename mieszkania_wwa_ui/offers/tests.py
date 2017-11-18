import json
from http.server import BaseHTTPRequestHandler

from django.test import override_settings

from utils.test_utils import MockedTestCase, e2e


class ShouldReturnAllOffersFromRepositoryMock(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            'data': [
                {
                    'type': 'offers',
                    'attributes': {
                        'lat': '52.171962',
                        'lng': '20.997109',
                        'subject': 'some apartment',
                        'price': '2000zl'
                    },
                    'id': '59c77ca636f8b57904f3724f',
                    'links': {
                        'self': 'someFakeUrl'
                    }
                },
                {
                    'type': 'offers',
                    'attributes': {
                        'lat': '52.244365',
                        'lng': '20.982019',
                        'subject': 'some apartment 2',
                        'price': '1000zl'
                    },
                    'id': '59c77d4c36f8b57904f37250',
                    'links': {
                        'self': 'someFakeUrl2'
                    }
                }
            ]
        }).encode(encoding='UTF-8'))


class ShouldThrowErrorWhenCantGetOffersMock(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(500)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()


@e2e
class ShouldReturnAllOffers(MockedTestCase):
    @classmethod
    def mock_server_request_handler(cls):
        return ShouldReturnAllOffersFromRepositoryMock

    def test_should_return_all_offers_from_repository(self):
        with override_settings(OFFERS_URL='http://localhost:{port}'.format(port=self.mock_server_port)):
            # when
            response = self.client.get('/offers')

            # then
            self.assertEqual(response.status_code, 200)

            # and
            result = json.loads(response.content.decode('utf-8'))
            self.assertListEqual(
                sorted(result, key=lambda e: e['pk']),
                [
                    {
                        'lat': '52.171962',
                        'lng': '20.997109',
                        'subject': 'some apartment',
                        'price': '2000zl',
                        'pk': '59c77ca636f8b57904f3724f'
                    },
                    {
                        'lat': '52.244365',
                        'lng': '20.982019',
                        'subject': 'some apartment 2',
                        'price': '1000zl',
                        'pk': '59c77d4c36f8b57904f37250'
                    }
                ]
            )


@e2e
class ShouldReturnErrorWhenCantGetOffers(MockedTestCase):
    @classmethod
    def mock_server_request_handler(cls):
        return ShouldThrowErrorWhenCantGetOffersMock

    def test_should_throw_error_when_cant_get_offers(self):
        with override_settings(OFFERS_URL='http://localhost:{port}'.format(port=self.mock_server_port)):
            # when
            response = self.client.get('/offers')

            # then
            self.assertEqual(response.status_code, 500)

            # and
            result = json.loads(response.content.decode('utf-8'))
            self.assertIn('message', result)
            self.assertIn('error_code', result)
            self.assertIn('status_code', result)