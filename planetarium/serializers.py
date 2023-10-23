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


class ShowSessionSerializer(serializers.ModelSerializer):
    astronomy_show = AstronomyShowShortSerializer(many=False, read_only=False)
    planetarium_dome = PlanetariumDomeShortSerializer(
        many=False, read_only=False
    )

    class Meta:
        model = ShowSession
        fields = ("id", "astronomy_show", "planetarium_dome", "show_time")


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = "__all__"


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"
