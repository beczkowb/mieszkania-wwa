import json
from http.server import BaseHTTPRequestHandler
from unittest import mock

from django.test import override_settings

from offers.dto import UnsavedOffer
from offers.repositories import InMemoryOfferRepository
from offers.tasks import OfferRefresher
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


class FacebookGroupApiMock(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        if self.path == '/next':
            self.wfile.write(json.dumps({
                "data": [],
                "paging": {
                    "previous": "prev_link",
                    "next": f"http://localhost:{self.port}/next"
                }
            }).encode(encoding='UTF-8'))
        else:
            self.wfile.write(json.dumps({
                "data": [
                    {
                        "message": "pozycja: 52.242714, 20.989553\ncena: 2000z\u0142\nopis: bla1",
                        "updated_time": "2017-11-18T21:58:51+0000",
                        "id": "497345270640091_497346870639931"
                    },
                    {
                        "message": "pozycja: 52.242714, 20.989553\ncena: 2000z\u0142\nopis: bla2",
                        "updated_time": "2017-10-10T21:58:51+0000",
                        "id": "497345270640091_497346870639931"
                    },
                    {
                        "story": "Bart\u0142omiej B\u0119czkowski created the group mw-dev.",
                        "updated_time": "2017-11-18T21:57:54+0000",
                        "id": "497345270640091_497345273973424"
                    }
                ],
                "paging": {
                    "previous": "prev_link",
                    "next": f"http://localhost:{self.port}/next"
                }
            }).encode(encoding='UTF-8'))


class ShouldRefreshOffers(MockedTestCase):
    @classmethod
    def mock_server_request_handler(cls):
        return FacebookGroupApiMock

    def test_should_refresh_offers(self):
        repository = InMemoryOfferRepository()
        refresher = OfferRefresher(repository)

        with override_settings(
            FACEBOOK_GROUP_URL='http://localhost:{port}'.format(port=self.mock_server_port),
            OFFERS_URL='http://localhost:{port}'.format(port=self.mock_server_port)
        ):
            # given
            repository.save(UnsavedOffer('52.242714', '20.989553', '2000zł', 'bla bla'))

            # when
            refresher.refresh()

            # then
            self.assertEqual(len(repository.all()), 1)

            # and
            offer = repository.all()[0]
            self.assertEqual(offer.lat, '52.242714')
            self.assertEqual(offer.lng, '20.989553')
            self.assertEqual(offer.price, '2000zł')
            self.assertEqual(offer.subject, 'bla1')