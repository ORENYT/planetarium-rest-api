from django.urls import path, include
from rest_framework import routers

from planetarium.views import ShowThemeViewSet, AstronomyShowViewSet, \
    PlanetariumDomeViewSet, ShowSessionViewSet, ReservationViewSet, \
    TicketViewSet

router = routers.DefaultRouter()
router.register("theme", ShowThemeViewSet)
router.register("show", AstronomyShowViewSet)
router.register("dome", PlanetariumDomeViewSet)
router.register("session", ShowSessionViewSet)
router.register("reservation", ReservationViewSet)
router.register("ticket", TicketViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "planetarium"
