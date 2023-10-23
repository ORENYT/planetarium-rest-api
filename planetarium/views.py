import datetime

from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from rest_framework import mixins
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from planetarium.models import (
    ShowTheme,
    AstronomyShow,
    PlanetariumDome,
    ShowSession,
    Reservation,
    Ticket,
)
from planetarium.serializers import (
    ShowThemeSerializer,
    AstronomyShowSerializer,
    PlanetariumDomeSerializer,
    ShowSessionListSerializer,
    ReservationSerializer,
    TicketSerializer,
    ShowSessionDetailSerializer,
    ShowSessionEditSerializer,
    TicketEditSerializer,
    ReservationCreateSerializer,
)


class ShowThemeViewSet(ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer


class AstronomyShowViewSet(ModelViewSet):
    queryset = AstronomyShow.objects.all()
    serializer_class = AstronomyShowSerializer

    def get_queryset(self):
        queryset = self.queryset.prefetch_related("themes")
        return queryset


class PlanetariumDomeViewSet(ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer


class ShowSessionViewSet(ModelViewSet):
    queryset = ShowSession.objects.all()
    serializer_class = ShowSessionListSerializer

    def get_queryset(self):
        queryset = self.queryset.prefetch_related(
            "astronomy_show", "planetarium_dome"
        )
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ShowSessionDetailSerializer
        if self.action == "list":
            return self.serializer_class
        return ShowSessionEditSerializer


class ReservationViewSet(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer


class TicketViewSet(ModelViewSet):
    queryset = Ticket.objects.all().select_related(
        "reservation", "show_session"
    )
    serializer_class = TicketEditSerializer

    def perform_create(self, serializer):
        """Automatically make a reservation"""
        with transaction.atomic():
            user = self.request.user
            created_at = datetime.datetime.now()
            if isinstance(self.request.user, AnonymousUser):
                raise ValidationError(
                    "Error with data. Check if you are logged in."
                )
            reservation = Reservation.objects.create(
                user=user, created_at=created_at
            )
            serializer.save(reservation=reservation)

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return TicketSerializer
        return self.serializer_class
