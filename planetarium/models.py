from django.db import models
from rest_framework.exceptions import ValidationError

from user.models import User


class ShowTheme(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class AstronomyShow(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    themes = models.ManyToManyField(ShowTheme, related_name="shows")

    def __str__(self):
        return self.title


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    @property
    def capacity(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class ShowSession(models.Model):
    astronomy_show = models.ForeignKey(
        to=AstronomyShow,
        related_name="sessions",
        on_delete=models.CASCADE,
        null=False,
    )
    planetarium_dome = models.ForeignKey(
        to=PlanetariumDome,
        related_name="domes",
        on_delete=models.CASCADE,
        null=False,
    )
    show_time = models.DateTimeField(null=True)

    def __str__(self):
        return (
            f"{self.astronomy_show} in {self.planetarium_dome}"
            f" at {self.show_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="reservations"
    )

    def __str__(self):
        return self.created_at.strftime("%Y-%m-%d")


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    show_session = models.ForeignKey(
        ShowSession,
        on_delete=models.SET_NULL,
        null=True,
        related_name="tickets",
    )
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.SET_NULL,
        null=True,
        related_name="tickets",
    )

    @staticmethod
    def validate_ticket(row, seat, planetarium_dome):
        for (
            ticket_attr_value,
            ticket_attr_name,
            planetarium_dome_attr_name,
        ) in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(planetarium_dome, planetarium_dome_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise ValidationError(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {planetarium_dome_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.show_session.planetarium_dome,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return f"{str(self.show_session)} (row: {self.row}, seat: {self.seat})"

    class Meta:
        unique_together = ("show_session", "row", "seat")
        ordering = ["row", "seat"]
