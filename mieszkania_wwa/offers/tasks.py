from offers.repositories import OfferFacebookRepository, OfferRepository
from django.conf import settings


class OfferRefresher:
    _INSTANCE = None

    @classmethod
    def instance(cls):
        if cls._INSTANCE is None:
            cls._INSTANCE = OfferRefresher(OfferRepository)
        return cls._INSTANCE

    def __init__(self, offer_repository):
        self.offer_repository = offer_repository

    def refresh(self):
        self.offer_repository.delete_all()
        self._add_all()

    def _add_all(self):
        for unsaved_offer in OfferFacebookRepository.from_last_n_days(settings.OFFERS_TTL_DAYS):
            self.offer_repository.save(unsaved_offer)