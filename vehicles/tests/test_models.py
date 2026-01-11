from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date, timedelta
from accounts.models import User
from vehicles.models import Vehicle


class VehicleModelTest(TestCase):
    """Test cases for the Vehicle model"""

    def setUp(self):
        """Set up test data"""
        self.driver = User.objects.create_user(
            email="driver@test.com",
            password="testpass123",
            first_name="John",
            last_name="Driver",
            phone_number="+1234567890",
            role=User.Role.INDIVIDUAL_DRIVER,
        )

        # Create mock files for testing
        self.road_worthiness_file = SimpleUploadedFile(
            "road_worthiness.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        self.insurance_file = SimpleUploadedFile(
            "insurance.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        self.inspection_file = SimpleUploadedFile(
            "inspection.pdf",
            b"file_content",
            content_type="application/pdf"
        )

        self.vehicle_data = {
            "driver": self.driver,
            "brand": "Toyota",
            "model": "Camry",
            "year": 2020,
            "license_number": "ABC123XY",
            "registration_number": "REG123456",
            "expiry_date": date.today() + timedelta(days=365),
            "colour": "Blue",
            "road_worthiness_certificate": self.road_worthiness_file,
            "vehicle_insurance": self.insurance_file,
            "inspection_report": self.inspection_file,
        }

    def test_vehicle_creation(self):
        """Test creating a vehicle successfully"""
        vehicle = Vehicle.objects.create(**self.vehicle_data)
        
        self.assertEqual(vehicle.driver, self.driver)
        self.assertEqual(vehicle.brand, "Toyota")
        self.assertEqual(vehicle.model, "Camry")
        self.assertEqual(vehicle.year, 2020)
        self.assertEqual(vehicle.license_number, "ABC123XY")
        self.assertEqual(vehicle.colour, "Blue")
        self.assertIsNotNone(vehicle.id)

    def test_vehicle_string_representation(self):
        """Test the string representation of vehicle"""
        vehicle = Vehicle.objects.create(**self.vehicle_data)
        # Note: Vehicle model doesn't have __str__ method, so it will use default
        self.assertIsNotNone(str(vehicle))

    def test_vehicle_driver_relationship(self):
        """Test the foreign key relationship with User"""
        vehicle = Vehicle.objects.create(**self.vehicle_data)
        self.assertEqual(vehicle.driver.email, "driver@test.com")
        self.assertEqual(vehicle.driver.role, User.Role.INDIVIDUAL_DRIVER)

    def test_multiple_vehicles_for_one_driver(self):
        """Test that a driver can have multiple vehicles"""
        vehicle1 = Vehicle.objects.create(**self.vehicle_data)
        
        # Create second vehicle with different data
        vehicle_data_2 = self.vehicle_data.copy()
        vehicle_data_2["license_number"] = "XYZ789AB"
        vehicle_data_2["registration_number"] = "REG789012"
        vehicle_data_2["road_worthiness_certificate"] = SimpleUploadedFile(
            "road2.pdf", b"file_content", content_type="application/pdf"
        )
        vehicle_data_2["vehicle_insurance"] = SimpleUploadedFile(
            "insurance2.pdf", b"file_content", content_type="application/pdf"
        )
        vehicle_data_2["inspection_report"] = SimpleUploadedFile(
            "inspection2.pdf", b"file_content", content_type="application/pdf"
        )
        
        vehicle2 = Vehicle.objects.create(**vehicle_data_2)
        
        driver_vehicles = Vehicle.objects.filter(driver=self.driver)
        self.assertEqual(driver_vehicles.count(), 2)
        self.assertIn(vehicle1, driver_vehicles)
        self.assertIn(vehicle2, driver_vehicles)

    def test_vehicle_cascade_delete(self):
        """Test that vehicles are deleted when driver is deleted"""
        vehicle = Vehicle.objects.create(**self.vehicle_data)
        vehicle_id = vehicle.id
        
        self.driver.delete()
        
        with self.assertRaises(Vehicle.DoesNotExist):
            Vehicle.objects.get(id=vehicle_id)

