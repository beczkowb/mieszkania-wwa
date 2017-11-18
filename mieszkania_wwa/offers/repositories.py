import requests
from django.conf import settings

from offers.domain import Offer


class CouldNotGetOffersError(Exception):
    def __init__(self, message, *args, **kwargs):
        super(*args, **kwargs)
        self.message = message


class OfferRepository:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = OfferRepository()

        return cls._instance

    def all(self):
        offers_resp = requests.get(settings.OFFERS_URL)

        if offers_resp.status_code != 200:
            reason = f'{offers_resp.status_code}, {offers_resp.text}'
            raise CouldNotGetOffersError(f'Could not get offers. Reason: {reason}')

        return self._map_response_to_offers(offers_resp)

    def save(self):
        pass

    def deleteAll(self):
        pass

    def _map_response_to_offers(self, offers_resp):
        return [Offer(
            pk=offer_data['id'],
            **offer_data['attributes']) for offer_data in offers_resp.json()['data']
        ]


class OfferFetcher:
    def fetch(self):
        response = requests.get(settings.FACEBOOK_GROUP_URL)
