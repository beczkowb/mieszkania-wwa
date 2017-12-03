import logging
from datetime import datetime
from offers.repositories import OfferFacebookRepository, OfferRepository
from django.conf import settings

logger = logging.getLogger("offer_refresher")


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
        start = datetime.now()
        self._delete_obsolete_offers_and_save_missing()
        duration = (datetime.now() - start).seconds
        logger.error(duration)

    def _delete_obsolete_offers_and_save_missing(self):
        offers = self.offer_repository.all()
        offer_post_ids = {o.post_id: o for o in offers}
        offers_from_facebook = OfferFacebookRepository.from_last_n_days(settings.OFFERS_TTL_DAYS)
        offer_post_ids_from_facebook = {o.post_id: o for o in offers_from_facebook}

        for post_id, offer in offer_post_ids.items():
            if post_id not in offer_post_ids_from_facebook:
                self.offer_repository.delete(offer.pk)

        for post_id, offer in offer_post_ids_from_facebook.items():
            if post_id not in offer_post_ids:
                self.offer_repository.save(offer)