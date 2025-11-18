"""
Tests for AdminProfile and DriverProfile models.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from accounts.models import User, AdminProfile, DriverProfile


class AdminProfileTests(TestCase):
    """Test AdminProfile model functionality."""

    def setUp(self):
        """Create an admin user with profile."""
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            role=User.Role.ADMIN,
        )
        self.profile = self.admin.profile

    def test_profile_created_automatically(self):
        """Test that AdminProfile is created automatically for admin."""
        self.assertIsNotNone(self.profile)
        self.assertEqual(self.profile.user, self.admin)

    def test_profile_str_method(self):
        """Test AdminProfile __str__ method."""
        self.assertEqual(str(self.profile), "Admin User")

    def test_profile_can_update_fields(self):
        """Test that profile fields can be updated."""
        self.profile.address = "123 Main St"
        self.profile.city = "New York"
        self.profile.state = "NY"
        self.profile.zip_code = "10001"
        self.profile.country = "USA"
        self.profile.save()

        self.profile.refresh_from_db()

        self.assertEqual(self.profile.address, "123 Main St")
        self.assertEqual(self.profile.city, "New York")
        self.assertEqual(self.profile.state, "NY")
        self.assertEqual(self.profile.zip_code, "10001")
        self.assertEqual(self.profile.country, "USA")

    def test_profile_age_calculation(self):
        """Test age property calculates correctly."""
        # Set birth date to 30 years ago
        birth_date = timezone.now().date() - timedelta(days=365 * 30)
        self.profile.date_of_birth = birth_date
        self.profile.save()

        # Age should be 29 or 30 depending on exact date
        self.assertIn(self.profile.age, [29, 30])

    def test_profile_age_with_no_birth_date(self):
        """Test age property returns None when no birth date."""
        self.profile.date_of_birth = None
        self.profile.save()

        self.assertIsNone(self.profile.age)

    def test_profile_has_timestamps(self):
        """Test that profile has created_at and updated_at."""
        self.assertIsNotNone(self.profile.created_at)
        self.assertIsNotNone(self.profile.updated_at)

    def test_deleting_user_deletes_profile(self):
        """Test that deleting user cascades to delete profile."""
        profile_id = self.profile.id
        self.admin.delete()

        with self.assertRaises(AdminProfile.DoesNotExist):
            AdminProfile.objects.get(id=profile_id)


class DriverProfileTests(TestCase):
    """Test DriverProfile model functionality."""

    def setUp(self):
        """Create a driver for tests."""
        self.driver = User.objects.create_user(
            email="driver@example.com",
            password="testpass123",
            first_name="Test",
            last_name="Driver",
            phone_number="1234567890",
            role=User.Role.INDIVIDUAL_DRIVER,
        )
        self.profile = self.driver.driver_profile

    def test_driver_profile_created_automatically(self):
        """Test that DriverProfile is created by signal."""
        self.assertIsNotNone(self.profile)
        self.assertEqual(self.profile.user, self.driver)

    def test_driver_profile_default_values(self):
        """Test DriverProfile default field values."""
        self.assertFalse(self.profile.verified)
        self.assertIsNone(self.profile.verified_at)
        self.assertEqual(self.profile.license_number, "")
        self.assertEqual(self.profile.license_class, "")

    def test_driver_profile_can_update_license_info(self):
        """Test updating driver license information."""
        future_date = timezone.now().date() + timedelta(days=365)

        self.profile.license_number = "DL123456"
        self.profile.license_class = "Class A"
        self.profile.license_expiry = future_date
        self.profile.save()

        self.profile.refresh_from_db()

        self.assertEqual(self.profile.license_number, "DL123456")
        self.assertEqual(self.profile.license_class, "Class A")
        self.assertEqual(self.profile.license_expiry, future_date)

    def test_driver_profile_can_update_emergency_contact(self):
        """Test updating emergency contact information."""
        self.profile.emergency_contact_name = "Jane Doe"
        self.profile.emergency_contact_phone = "9876543210"
        self.profile.save()

        self.profile.refresh_from_db()

        self.assertEqual(self.profile.emergency_contact_name, "Jane Doe")
        self.assertEqual(self.profile.emergency_contact_phone, "9876543210")

    def test_mark_verified_method(self):
        """Test mark_verified method sets verified and verified_at."""
        self.assertFalse(self.profile.verified)
        self.assertIsNone(self.profile.verified_at)

        self.profile.mark_verified()

        self.assertTrue(self.profile.verified)
        self.assertIsNotNone(self.profile.verified_at)

        # verified_at should be recent
        time_diff = timezone.now() - self.profile.verified_at
        self.assertLess(time_diff.total_seconds(), 10)

    def test_expired_license_validation(self):
        """Test that expired license raises validation error."""
        yesterday = timezone.now().date() - timedelta(days=1)
        self.profile.license_expiry = yesterday

        with self.assertRaises(ValidationError) as cm:
            self.profile.clean()

        self.assertIn("license_expiry", cm.exception.message_dict)

    def test_valid_future_license_passes_validation(self):
        """Test that future license date passes validation."""
        future_date = timezone.now().date() + timedelta(days=365)
        self.profile.license_expiry = future_date

        # Should not raise ValidationError
        try:
            self.profile.clean()
        except ValidationError:
            self.fail("Validation should pass for future license expiry")

    def test_verified_without_verified_at_validation(self):
        """Test that setting verified without verified_at raises error."""
        self.profile.verified = True
        self.profile.verified_at = None

        with self.assertRaises(ValidationError) as cm:
            self.profile.clean()

        self.assertIn("verified_at", cm.exception.message_dict)

    def test_is_license_expired_property_with_expired_license(self):
        """Test is_license_expired property returns True for expired license."""
        yesterday = timezone.now().date() - timedelta(days=1)
        self.profile.license_expiry = yesterday
        self.profile.save()

        self.assertTrue(self.profile.is_license_expired)

    def test_is_license_expired_property_with_valid_license(self):
        """Test is_license_expired property returns False for valid license."""
        future_date = timezone.now().date() + timedelta(days=365)
        self.profile.license_expiry = future_date
        self.profile.save()

        self.assertFalse(self.profile.is_license_expired)

    def test_is_license_expired_property_with_no_expiry(self):
        """Test is_license_expired property returns None when no expiry set."""
        self.profile.license_expiry = None
        self.profile.save()

        self.assertIsNone(self.profile.is_license_expired)

    def test_license_expiry_days_property_future(self):
        """Test license_expiry_days calculation for future date."""
        future_date = timezone.now().date() + timedelta(days=45)
        self.profile.license_expiry = future_date
        self.profile.save()

        self.assertEqual(self.profile.license_expiry_days, 45)

    def test_license_expiry_days_property_past(self):
        """Test license_expiry_days calculation for past date (negative)."""
        past_date = timezone.now().date() - timedelta(days=10)
        self.profile.license_expiry = past_date
        self.profile.save()

        self.assertEqual(self.profile.license_expiry_days, -10)

    def test_license_expiry_days_property_with_no_expiry(self):
        """Test license_expiry_days returns None when no expiry set."""
        self.profile.license_expiry = None
        self.profile.save()

        self.assertIsNone(self.profile.license_expiry_days)

    def test_driver_profile_inherits_common_profile_fields(self):
        """Test that DriverProfile has all CommonProfile fields."""
        # Update common profile fields
        self.profile.address = "456 Driver St"
        self.profile.city = "Los Angeles"
        self.profile.state = "CA"
        self.profile.zip_code = "90001"
        self.profile.country = "USA"
        birth_date = timezone.now().date() - timedelta(days=365 * 25)
        self.profile.date_of_birth = birth_date
        self.profile.save()

        self.profile.refresh_from_db()

        # All fields should be saved
        self.assertEqual(self.profile.address, "456 Driver St")
        self.assertEqual(self.profile.city, "Los Angeles")
        self.assertEqual(self.profile.state, "CA")
        self.assertEqual(self.profile.zip_code, "90001")
        self.assertEqual(self.profile.country, "USA")
        self.assertEqual(self.profile.date_of_birth, birth_date)

    def test_driver_profile_age_property(self):
        """Test that age property works for DriverProfile."""
        birth_date = timezone.now().date() - timedelta(days=365 * 28)
        self.profile.date_of_birth = birth_date
        self.profile.save()

        self.assertIn(self.profile.age, [27, 28])

    def test_driver_profile_str_method(self):
        """Test DriverProfile __str__ method."""
        self.assertEqual(str(self.profile), "Test Driver")

    def test_deleting_driver_deletes_profile(self):
        """Test that deleting driver cascades to delete profile."""
        profile_id = self.profile.id
        self.driver.delete()

        with self.assertRaises(DriverProfile.DoesNotExist):
            DriverProfile.objects.get(id=profile_id)

    def test_multiple_drivers_each_have_own_profile(self):
        """Test that each driver has their own separate profile."""
        drivers = []
        for i in range(3):
            driver = User.objects.create_user(
                email=f"driver{i}@example.com",
                password="testpass123",
                role=User.Role.INDIVIDUAL_DRIVER,
                phone_number=f"111111111{i}",
            )
            drivers.append(driver)

        # Each should have their own profile
        profile_ids = set()
        for driver in drivers:
            self.assertTrue(hasattr(driver, "driver_profile"))
            profile_ids.add(driver.driver_profile.id)

        # All profiles should be distinct
        self.assertEqual(len(profile_ids), 3)

    def test_company_owner_has_driver_profile(self):
        """Test that company owners also get DriverProfile."""
        owner = User.objects.create_user(
            email="owner@example.com",
            password="testpass123",
            role=User.Role.COMPANY_OWNER,
            phone_number="9999999999",
        )

        self.assertTrue(hasattr(owner, "driver_profile"))
        self.assertIsInstance(owner.driver_profile, DriverProfile)

    def test_company_driver_has_driver_profile(self):
        """Test that company drivers get DriverProfile."""
        company_driver = User.objects.create_user(
            email="companydriver@example.com",
            password="testpass123",
            role=User.Role.COMPANY_DRIVER,
            phone_number="8888888888",
        )

        self.assertTrue(hasattr(company_driver, "driver_profile"))
        self.assertIsInstance(company_driver.driver_profile, DriverProfile)
