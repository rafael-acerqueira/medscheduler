from django.test import TestCase, Client
import json

class SimulateNotificationTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_simulate_notification_success(self):
        payload = {
            "appointment_id": 1,
            "type": "reminder"
        }
        response = self.client.post(
            "/notifications/simulate/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Simulated", response.json()["message"])