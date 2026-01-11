from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import User


class VehiclePermissionsTest(APITestCase):
    """Test cases specifically for permission classes"""

    def setUp(self):
        """Set up test users"""
        self.client = APIClient()
        
        self.individual_driver = User.objects.create_user(
            email="individual@test.com",
            password="testpass123",
            first_name="John",
            last_name="Individual",
            phone_number="+1234567890",
            role=User.Role.INDIVIDUAL_DRIVER,
        )

        self.company_driver = User.objects.create_user(
            email="company@test.com",
            password="testpass123",
            first_name="Jane",
            last_name="Company",
            phone_number="+1234567891",
            role=User.Role.COMPANY_DRIVER,
        )

        self.company_owner = User.objects.create_user(
            email="owner@test.com",
            password="testpass123",
            first_name="Bob",
            last_name="Owner",
            phone_number="+1234567892",
            role=User.Role.COMPANY_OWNER,
        )

        self.admin = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            phone_number="+1234567893",
            role=User.Role.ADMIN,
        )

        self.list_url = "/vehicles/"

    def test_individual_driver_has_permission(self):
        """Test IsIndividualDriver permission allows individual drivers"""
        self.client.force_authenticate(user=self.individual_driver)
        response = self.client.get(self.list_url)
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_company_driver_has_permission(self):
        """Test IsCompanyDriver permission allows company drivers"""
        self.client.force_authenticate(user=self.company_driver)
        response = self.client.get(self.list_url)
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_company_owner_has_permission(self):
        """Test IsCompanyDriver or IsIndividualDriver permission allows company owners"""
        self.client.force_authenticate(user=self.company_owner)
        response = self.client.get(self.list_url)
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_does_not_have_permission(self):
        """Test admin users are denied access"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_denied(self):
        """Test unauthenticated users are denied access"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

