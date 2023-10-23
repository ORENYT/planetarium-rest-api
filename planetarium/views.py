import datetime

from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from django.db.models import F, Count
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
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
)


class ShowThemeViewSet(ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """Retrieve shows with filters"""
        name = self.request.query_params.get("name")
        queryset = self.queryset

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset.distinct()

    # Only for docs
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type={"type": "string"},
                description=(
                        "Filter by show name (case insensitive). "
                        "Example: ?name=aBc"
                ),
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


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
        return self.queryset.select_related(
            "astronomy_show", "planetarium_dome"
        ).annotate(
            tickets_available=(
                    F("planetarium_dome__rows")
                    * F("planetarium_dome__seats_in_row")
                    - Count("tickets")
            )
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ShowSessionDetailSerializer
        if self.action == "list":
            return self.serializer_class
        return ShowSessionEditSerializer


class OrderPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class ReservationViewSet(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    pagination_class = OrderPagination

    def get_queryset(self):
        return self.queryset.select_related("user")


class TicketViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet
):
    queryset = Ticket.objects.all()
    serializer_class = TicketEditSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAuthenticated,)

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

    def get_queryset(self):
        return self.queryset.prefetch_related("reservation", "show_session")
