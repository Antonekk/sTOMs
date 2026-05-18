from rest_framework.test import APIClient, APITestCase

from .helpers import add_weekly_schedule, create_appointment_types, create_client, create_therapist


class ReservationAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.therapist_user, cls.therapist = create_therapist()
        cls.client_user, cls.patient = create_client()
        cls.periodic_type, cls.one_time_type = create_appointment_types()
        add_weekly_schedule(cls.therapist)

    def setUp(self):
        self.api = APIClient()
