from django.contrib.auth import get_user_model
from rest_framework import serializers

from planetarium.models import (
    ShowTheme,
    AstronomyShow,
    PlanetariumDome,
    ShowSession,
    Reservation,
    Ticket,
)


class ShowThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowTheme
        fields = "__all__"


class AstronomyShowSerializer(serializers.ModelSerializer):
    themes = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field="name",
        queryset=ShowTheme.objects.all(),
    )

    class Meta:
        model = AstronomyShow
        fields = ("title", "description", "themes")


class PlanetariumDomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanetariumDome
        fields = ("id", "name", "rows", "seats_in_row", "capacity")


class AstronomyShowShortSerializer(serializers.ModelSerializer):
    themes = serializers.SerializerMethodField()

    class Meta:
        model = AstronomyShow
        fields = ("title", "themes")

    def get_themes(self, obj):
        return ", ".join(obj.themes.values_list("name", flat=True))


class PlanetariumDomeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanetariumDome
        fields = ("name", "capacity")


class ShowSessionListSerializer(serializers.ModelSerializer):
    astronomy_show = AstronomyShowShortSerializer(many=False, read_only=True)
    planetarium_dome = PlanetariumDomeShortSerializer(
        many=False, read_only=True
    )

    class Meta:
        model = ShowSession
        fields = ("id", "astronomy_show", "planetarium_dome", "show_time")


class ShowSessionEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowSession
        fields = ("id", "astronomy_show", "planetarium_dome", "show_time")


class ShowSessionDetailSerializer(serializers.ModelSerializer):
    astronomy_show = AstronomyShowSerializer(many=False, read_only=True)
    planetarium_dome = PlanetariumDomeSerializer(many=False, read_only=True)

    class Meta:
        model = ShowSession
        fields = "__all__"


class ReservationSerializer(serializers.ModelSerializer):
    user = serializers.EmailField(read_only=True)
    created_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S", read_only=True
    )

    class Meta:
        model = Reservation
        fields = "__all__"


class ReservationCreateSerializer(serializers.ModelSerializer):
    user = serializers.EmailField(read_only=False)
    created_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S", read_only=True
    )

    class Meta:
        model = Reservation
        fields = "__all__"


class TicketEditSerializer(serializers.ModelSerializer):
    reservation = ReservationSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ("row", "seat", "show_session", "reservation")
        read_only_fields = ("reservation",)


class TicketSerializer(serializers.ModelSerializer):
    show_session = serializers.StringRelatedField()
    reservation = ReservationSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "show_session", "reservation")
        read_only_fields = ("reservation",)
