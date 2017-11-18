import logging

from offers.repositories import OfferRepository, CouldNotGetOffersError
from utils.metrics import MetricReporter
from utils.views import return_entities, InternalServerError

logger = logging.getLogger("offers")


@return_entities
@MetricReporter.metered_view
def get_offers(request):
    try:
        offers = OfferRepository.instance().all()
        return None, offers
    except CouldNotGetOffersError as e:
        logger.error(e.message)
        return InternalServerError(), None