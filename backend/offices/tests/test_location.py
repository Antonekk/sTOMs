from django.test import TestCase

from offices.location import serialize_office_location

from .helpers import create_office


class SerializeOfficeLocationTestCase(TestCase):
    def test_returns_none_for_missing_office(self):
        self.assertIsNone(serialize_office_location(None))

    def test_serializes_office_fields(self):
        office = create_office(room_number="101")
        localization = office.localization

        result = serialize_office_location(office)

        self.assertEqual(
            result,
            {
                "name": localization.name,
                "city": "City",
                "address": "Addr",
                "postal_code": "00-001",
                "room_number": "101",
            },
        )
