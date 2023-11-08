from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from planetarium.models import (
    ShowTheme,
    ShowSession,
    Ticket,
    PlanetariumDome,
    AstronomyShow,
    Reservation,
)
from planetarium.serializers import (
    ShowThemeSerializer,
    ShowSessionListSerializer,
)

SHOWS_URL = reverse("planetarium:showtheme-list")
SESSIONS_URL = reverse("planetarium:showsession-list")


def sample_theme(**params):
    defaults = {
        "name": "test_name",
    }
    defaults.update(params)
    return ShowTheme.objects.create(**defaults)


class UnauthenticatedApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(SHOWS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class FilteringTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test2user@tests.test", password="testUser123"
        )
        self.client.force_authenticate(self.user)

    def test_expected_list(self):
        sample_theme()
        sample_theme()
        res = self.client.get(SHOWS_URL)
        shows = ShowTheme.objects.all()
        serializer = ShowThemeSerializer(shows, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_by_name(self):
        theme1 = sample_theme(name="name")
        theme2 = sample_theme(name="Coolname")
        theme3 = sample_theme(name="name1Coolname")
        theme4 = sample_theme(name="not_included")
        res = self.client.get(SHOWS_URL, {"name": "name"})
        serializer1 = ShowThemeSerializer(theme1)
        serializer2 = ShowThemeSerializer(theme2)
        serializer3 = ShowThemeSerializer(theme3)
        serializer4 = ShowThemeSerializer(theme4)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertIn(serializer3.data, res.data)
        self.assertNotIn(serializer4.data, res.data)


class AuthenticatedApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test2user@tests.test", password="testUser123"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve(self):
        theme = sample_theme()
        url = reverse("planetarium:showtheme-detail", args=[theme.id])
        res = self.client.get(url)
        serializer = ShowThemeSerializer(theme)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_forbidden(self):
        payload = {
            "title": "new_test_title",
        }
        res = self.client.post(SHOWS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@tests.test",
            password="testUser123",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_admin_has_correct_permission_to_post(self):
        payload = {
            "name": "test_title",
        }
        res = self.client.post(SHOWS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        theme = ShowTheme.objects.get(id=res.data["id"])
        for key in payload:
            self.assertEqual(payload[key], getattr(theme, key))


class CustomLogicApiTests(TestCase):
    def setUp(self) -> None:
        self.show = AstronomyShow.objects.create(
            title="TestTitle", description="TestDescription"
        )
        self.dome = PlanetariumDome.objects.create(
            name="TestName",
            rows=5,
            seats_in_row=10,
        )
        self.session = ShowSession.objects.create(
            astronomy_show=self.show, planetarium_dome=self.dome
        )

        self.serializer = ShowSessionListSerializer(self.session)
        self.reservation = Reservation.objects.create()

        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@tests.test",
            password="testUser123",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_tickets_available_calculation(self):
        reservation = Reservation.objects.create()
        Ticket.objects.create(
            row=1,
            seat=1,
            show_session=self.session,
            reservation=reservation,
        )
        Ticket.objects.create(
            row=1, seat=2, show_session=self.session, reservation=reservation
        )
        request = self.client.get(SESSIONS_URL)
        queryset = request.data

        tickets_available = queryset[0]["tickets_available"]
        expected_tickets_available = 5 * 10 - 2
        self.assertEqual(
            tickets_available,
            expected_tickets_available,
        )

    def test_ticket_out_of_border(self):
        with self.assertRaises(ValidationError):
            Ticket.objects.create(
                row=1,
                seat=11,
                show_session=self.session,
                reservation=self.reservation,
            )

        with self.assertRaises(ValidationError):
            Ticket.objects.create(
                row=6,
                seat=1,
                show_session=self.session,
                reservation=self.reservation,
            )

        with self.assertRaises(ValidationError):
            Ticket.objects.create(
                row=0,
                seat=2,
                show_session=self.session,
                reservation=self.reservation,
            )

        with self.assertRaises(ValidationError):
            Ticket.objects.create(
                row=2,
                seat=0,
                show_session=self.session,
                reservation=self.reservation,
            )
