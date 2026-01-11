from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import date, timedelta
from accounts.models import User
from vehicles.models import Vehicle


class VehicleViewSetTest(APITestCase):
    """Test cases for the Vehicle ViewSet API endpoints"""

    def setUp(self):
        """Set up test data and authenticate users"""
        self.client = APIClient()

        # Create different types of users
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

        self.admin_user = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            phone_number="+1234567893",
            role=User.Role.ADMIN,
        )

        # Create test vehicles
        self.vehicle1 = Vehicle.objects.create(
            driver=self.individual_driver,
            brand="Toyota",
            model="Camry",
            year=2020,
            license_number="ABC123",
            registration_number="REG123",
            expiry_date=date.today() + timedelta(days=365),
            colour="Blue",
            road_worthiness_certificate=SimpleUploadedFile(
                "road1.pdf", b"content", content_type="application/pdf"
            ),
            vehicle_insurance=SimpleUploadedFile(
                "insurance1.pdf", b"content", content_type="application/pdf"
            ),
            inspection_report=SimpleUploadedFile(
                "inspection1.pdf", b"content", content_type="application/pdf"
            ),
        )

        self.vehicle2 = Vehicle.objects.create(
            driver=self.company_driver,
            brand="Honda",
            model="Accord",
            year=2021,
            license_number="XYZ789",
            registration_number="REG789",
            expiry_date=date.today() + timedelta(days=365),
            colour="Red",
            road_worthiness_certificate=SimpleUploadedFile(
                "road2.pdf", b"content", content_type="application/pdf"
            ),
            vehicle_insurance=SimpleUploadedFile(
                "insurance2.pdf", b"content", content_type="application/pdf"
            ),
            inspection_report=SimpleUploadedFile(
                "inspection2.pdf", b"content", content_type="application/pdf"
            ),
        )

        self.list_url = "/vehicles/"
        self.detail_url = f"/vehicles/{self.vehicle1.id}/"

    def test_list_vehicles_unauthenticated(self):
        """Test that unauthenticated users cannot access vehicles"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_vehicles_as_individual_driver(self):
        """Test individual driver can list only their own vehicles"""
        self.client.force_authenticate(user=self.individual_driver)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["license_number"], "ABC123")

    def test_list_vehicles_as_company_driver(self):
        """Test company driver can list only their own vehicles"""
        self.client.force_authenticate(user=self.company_driver)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["license_number"], "XYZ789")

    def test_list_vehicles_as_admin(self):
        """Test admin user cannot access vehicles (no permission)"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url)
        
        # Admin doesn't have IsCompanyDriver or IsIndividualDriver permission
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_own_vehicle(self):
        """Test driver can retrieve their own vehicle details"""
        self.client.force_authenticate(user=self.individual_driver)
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["brand"], "Toyota")
        self.assertEqual(response.data["model"], "Camry")

    def test_cannot_retrieve_other_driver_vehicle(self):
        """Test driver cannot retrieve another driver's vehicle"""
        self.client.force_authenticate(user=self.company_driver)
        response = self.client.get(self.detail_url)
        
        # Should return 404 because queryset is filtered by driver
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_vehicle_as_individual_driver(self):
        """Test individual driver can create a vehicle"""
        self.client.force_authenticate(user=self.individual_driver)
        
        vehicle_data = {
            "driver": self.individual_driver.id,
            "brand": "Ford",
            "model": "Focus",
            "year": 2022,
            "license_number": "NEW123",
            "registration_number": "NEWREG123",
            "expiry_date": str(date.today() + timedelta(days=365)),
            "colour": "Black",
            "road_worthiness_certificate": SimpleUploadedFile(
                "new_road.pdf", b"content", content_type="application/pdf"
            ),
            "vehicle_insurance": SimpleUploadedFile(
                "new_insurance.pdf", b"content", content_type="application/pdf"
            ),
            "inspection_report": SimpleUploadedFile(
                "new_inspection.pdf", b"content", content_type="application/pdf"
            ),
        }
        
        response = self.client.post(self.list_url, vehicle_data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vehicle.objects.filter(driver=self.individual_driver).count(), 2)

    def test_update_own_vehicle(self):
        """Test driver can update their own vehicle"""
        self.client.force_authenticate(user=self.individual_driver)
        
        update_data = {
            "driver": self.individual_driver.id,
            "brand": "Toyota",
            "model": "Camry Updated",
            "year": 2020,
            "license_number": "ABC123",
            "registration_number": "REG123",
            "expiry_date": str(date.today() + timedelta(days=365)),
            "colour": "Green",
        }
        
        response = self.client.patch(self.detail_url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.vehicle1.refresh_from_db()
        self.assertEqual(self.vehicle1.model, "Camry Updated")
        self.assertEqual(self.vehicle1.colour, "Green")

    def test_cannot_update_other_driver_vehicle(self):
        """Test driver cannot update another driver's vehicle"""
        self.client.force_authenticate(user=self.company_driver)
        
        update_data = {"colour": "Purple"}
        response = self.client.patch(self.detail_url, update_data, format="json")
        
        # Should return 404 because queryset is filtered
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_own_vehicle(self):
        """Test driver can delete their own vehicle"""
        self.client.force_authenticate(user=self.individual_driver)
        
        vehicle_count_before = Vehicle.objects.filter(driver=self.individual_driver).count()
        response = self.client.delete(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        vehicle_count_after = Vehicle.objects.filter(driver=self.individual_driver).count()
        self.assertEqual(vehicle_count_after, vehicle_count_before - 1)

    def test_cannot_delete_other_driver_vehicle(self):
        """Test driver cannot delete another driver's vehicle"""
        self.client.force_authenticate(user=self.company_driver)
        
        response = self.client.delete(self.detail_url)
        
        # Should return 404 because queryset is filtered
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Vehicle.objects.filter(id=self.vehicle1.id).exists())

    def test_company_owner_can_access_vehicles(self):
        """Test company owner has access to vehicle endpoints"""
        self.client.force_authenticate(user=self.company_owner)
        response = self.client.get(self.list_url)
        
        # Company owner should have no vehicles yet
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_queryset_filtering(self):
        """Test that queryset properly filters vehicles by driver"""
        # Create a vehicle for company owner
        vehicle3 = Vehicle.objects.create(
            driver=self.company_owner,
            brand="BMW",
            model="X5",
            year=2023,
            license_number="BMW999",
            registration_number="BMWREG999",
            expiry_date=date.today() + timedelta(days=365),
            colour="White",
            road_worthiness_certificate=SimpleUploadedFile(
                "road3.pdf", b"content", content_type="application/pdf"
            ),
            vehicle_insurance=SimpleUploadedFile(
                "insurance3.pdf", b"content", content_type="application/pdf"
            ),
            inspection_report=SimpleUploadedFile(
                "inspection3.pdf", b"content", content_type="application/pdf"
            ),
        )

        # Test each user sees only their vehicles
        self.client.force_authenticate(user=self.individual_driver)
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["driver"], self.individual_driver.id)

        self.client.force_authenticate(user=self.company_driver)
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["driver"], self.company_driver.id)

        self.client.force_authenticate(user=self.company_owner)
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["driver"], self.company_owner.id)

