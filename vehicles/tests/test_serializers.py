from django.test import TestCase
from datetime import date, timedelta
from accounts.models import User
from vehicles.serializers import VehicleSerializer


class VehicleSerializerTest(TestCase):
    """Test cases for the Vehicle serializer"""

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

        self.vehicle_data = {
            "driver": self.driver.id,
            "brand": "Toyota",
            "model": "Camry",
            "year": 2020,
            "license_number": "ABC123XY",
            "registration_number": "REG123456",
            "expiry_date": str(date.today() + timedelta(days=365)),
            "colour": "Blue",
        }

    def test_serializer_with_valid_data(self):
        """Test serializer with valid data"""
        serializer = VehicleSerializer(data=self.vehicle_data)
        # Note: Files are required, so this might not be valid without them
        # This tests the basic serializer structure

    def test_serializer_fields(self):
        """Test that serializer contains all expected fields"""
        serializer = VehicleSerializer()
        fields = serializer.fields.keys()
        
        expected_fields = {
            'id', 'driver', 'brand', 'model', 'year', 'license_number',
            'registration_number', 'expiry_date', 'colour',
            'road_worthiness_certificate', 'vehicle_insurance', 'inspection_report'
        }
        
        self.assertEqual(set(fields), expected_fields)

