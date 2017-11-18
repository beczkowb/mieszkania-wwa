from django.conf.urls import url

from city_map import views as city_map_views
from offers import views as offers_views

urlpatterns = [
    url(r'^offers$', offers_views.get_offers),
    url(r'^', city_map_views.index),
]
