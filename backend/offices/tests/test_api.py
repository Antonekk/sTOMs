from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .helpers import create_localization, create_office


class LocalizationAPITestCase(APITestCase):
    def setUp(self):
        self.api = APIClient()
        self.localization = create_localization()
        self.office = create_office(localization=self.localization, room_number="1")

    def test_list_localizations(self):
        response = self.api.get("/api/v1/localizations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], self.localization.name)
        self.assertEqual(response.data[0]["offices"][0]["room_number"], self.office.room_number)

    def test_retrieve_localization(self):
        response = self.api.get(f"/api/v1/localizations/{self.localization.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.localization.id))
        self.assertEqual(len(response.data["offices"]), 1)


class OfficeAPITestCase(APITestCase):
    def setUp(self):
        self.api = APIClient()
        self.office = create_office(room_number="2")

    def test_list_offices(self):
        response = self.api.get("/api/v1/offices/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["room_number"], self.office.room_number)

    def test_retrieve_office(self):
        response = self.api.get(f"/api/v1/offices/{self.office.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.office.id))
