import requests
import datetime
from dateutil.parser import parse as parse_dt
from django.conf import settings
from django.utils import timezone

from offers.domain import Offer
from offers.dto import UnsavedOffer


class Error(Exception):
    def __init__(self, message, *args, **kwargs):
        super(*args, **kwargs)
        self.message = message


class CouldNotGetOffersError(Error):
    pass


class CouldNotSaveOfferError(Error):
    pass


class CouldNotDeleteOfferError(Error):
    pass


class InMemoryOfferRepository:
    _COUNTER = 0
    _OFFERS = {}

    @classmethod
    def all(cls):
        return [o for o in cls._OFFERS.values()]

    @classmethod
    def save(cls, new_offer):
        cls._OFFERS[cls._COUNTER] = Offer(
                str(cls._COUNTER),
                new_offer.lat,
                new_offer.lng,
                new_offer.price,
                new_offer.subject
            )
        cls._COUNTER += 1

    @classmethod
    def delete(cls, pk):
        del cls._OFFERS[pk]

    @classmethod
    def delete_all(cls):
        cls._OFFERS = {}


class OfferRepository:

    @classmethod
    def all(cls):
        offers_resp = requests.get(settings.OFFERS_URL)
        cls._raise_if_not_ok(CouldNotGetOffersError, offers_resp)
        return cls._map_response_to_offers(offers_resp)

    @classmethod
    def save(cls, new_offer):
        response = requests.post(settings.OFFERS_URL, json={
            'data': {
                'type': 'offers',
                'attributes': {
                    'lat': new_offer.lat,
                    'lng': new_offer.lng,
                    'price': new_offer.price,
                    'subject': new_offer.subject
                }
            }
        })

        cls._raise_if_not_ok(CouldNotSaveOfferError, response)

    @classmethod
    def delete(cls, pk):
        response = requests.delete(f'{settings.OFFERS_URL}/{pk}')
        cls._raise_if_not_ok(CouldNotDeleteOfferError, response)

    @classmethod
    def delete_all(cls):
        for offer in OfferRepository.all():
            OfferRepository.delete(offer.pk)

    @staticmethod
    def _map_response_to_offers(offers_resp):
        return [Offer(
            pk=offer_data['id'],
            **offer_data['attributes']) for offer_data in offers_resp.json()['data']
        ]

    @staticmethod
    def _raise_if_not_ok(exception, response):
        if response.status_code != 200:
            reason = f'{response.status_code}, {response.text}'
            raise exception(reason)


# TODO refactor
class OfferFacebookRepository:
    @classmethod
    def from_last_n_days(cls, N):
        response = requests.get(settings.FACEBOOK_GROUP_URL)
        response_body = response.json()
        result = []
        while response_body['data']:
            for offer_data in response_body['data']:
                dt = parse_dt(offer_data['updated_time'])
                if 'message' not in offer_data or (timezone.now() - datetime.timedelta(days=N)) > dt:
                    continue

                elements = offer_data['message'].split('\n')

                POSITION = 0
                position = elements[POSITION]
                lat_lng = position.split(':')[1]
                lat, lng = lat_lng.split(',')

                PRICE = 1
                price = elements[PRICE]
                price = price.split(':')[1]

                MESSAGE = 2
                message = elements[MESSAGE]
                message = message.split(':')[1]

                result.append(UnsavedOffer(lat.strip(), lng.strip(), price.strip(), message.strip()))

            response = requests.get(response_body['paging']['next'])
            response_body = response.json()

        return result
