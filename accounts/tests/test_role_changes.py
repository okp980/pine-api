"""
Tests for user role changes and the signals that handle them.
"""
from django.test import TestCase
from accounts.models import User, Company, AdminProfile, DriverProfile


class RoleChangeTests(TestCase):
    """Test behavior when user roles change after creation."""

    def test_admin_to_individual_driver_creates_driver_profile(self):
        """Test changing from admin to individual driver creates DriverProfile."""
        user = User.objects.create_user(
            email="user@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            phone_number="1234567890",
            role=User.Role.ADMIN,
        )

        # Should have Profile, not DriverProfile
        self.assertTrue(hasattr(user, "profile"))
        self.assertFalse(hasattr(user, "driver_profile"))

        # Change to individual driver
        user.role = User.Role.INDIVIDUAL_DRIVER
        user.save()

        # Refresh from database
        user.refresh_from_db()

        # Should now have DriverProfile
        self.assertTrue(hasattr(user, "driver_profile"))

    def test_admin_to_company_driver_creates_driver_profile(self):
        """Test changing from admin to company driver creates DriverProfile."""
        user = User.objects.create_user(
            email="user@example.com",
            password="testpass123",
            phone_number="1234567890",
            role=User.Role.ADMIN,
        )

        # Should have Profile
        self.assertTrue(hasattr(user, "profile"))

        # Change to company driver
        user.role = User.Role.COMPANY_DRIVER
        user.save()

        # Refresh from database
        user.refresh_from_db()

        # Should now have DriverProfile
        self.assertTrue(hasattr(user, "driver_profile"))

    def test_individual_driver_to_company_owner_creates_company(self):
        """Test changing from driver to company owner creates Company."""
        user = User.objects.create_user(
            email="driver@example.com",
            password="testpass123",
            first_name="Test",
            last_name="Driver",
            phone_number="1234567890",
            role=User.Role.INDIVIDUAL_DRIVER,
        )

        # Should have DriverProfile but not Company
        self.assertTrue(hasattr(user, "driver_profile"))
        self.assertFalse(hasattr(user, "owned_company"))

        # Change to company owner
        user.role = User.Role.COMPANY_OWNER
        user.save()

        # Refresh from database
        user.refresh_from_db()

        # Should now have Company
        self.assertTrue(hasattr(user, "owned_company"))
        self.assertIsInstance(user.owned_company, Company)
        # Should still have DriverProfile
        self.assertTrue(hasattr(user, "driver_profile"))

    def test_admin_to_company_owner_creates_both_company_and_driver_profile(self):
        """Test changing from admin to company owner creates both models."""
        user = User.objects.create_user(
            email="admin@example.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            phone_number="1234567890",
            role=User.Role.ADMIN,
        )

        # Should have Profile
        self.assertTrue(hasattr(user, "profile"))

        # Change to company owner
        user.role = User.Role.COMPANY_OWNER
        user.save()

        # Refresh from database
        user.refresh_from_db()

        # Should now have both Company and DriverProfile
        self.assertTrue(hasattr(user, "owned_company"))
        self.assertTrue(hasattr(user, "driver_profile"))

    def test_company_driver_to_individual_driver_keeps_driver_profile(self):
        """Test that switching between driver types keeps the same profile."""
        user = User.objects.create_user(
            email="driver@example.com",
            password="testpass123",
            phone_number="1234567890",
            role=User.Role.COMPANY_DRIVER,
        )

        # Get original profile ID
        original_profile_id = user.driver_profile.id

        # Change to individual driver
        user.role = User.Role.INDIVIDUAL_DRIVER
        user.save()

        # Refresh from database
        user.refresh_from_db()

        # Should still have the same DriverProfile
        self.assertEqual(user.driver_profile.id, original_profile_id)

    def test_company_owner_to_individual_driver_keeps_driver_profile_and_company(self):
        """Test that changing from owner to driver keeps both models."""
        user = User.objects.create_user(
            email="owner@example.com",
            password="testpass123",
            phone_number="1234567890",
            role=User.Role.COMPANY_OWNER,
        )

        # Should have both
        self.assertTrue(hasattr(user, "owned_company"))
        self.assertTrue(hasattr(user, "driver_profile"))

        original_company_id = user.owned_company.id
        original_profile_id = user.driver_profile.id

        # Change to individual driver
        user.role = User.Role.INDIVIDUAL_DRIVER
        user.save()

        # Refresh from database
        user.refresh_from_db()

        # Should still have both (role change doesn't delete existing models)
        self.assertEqual(user.owned_company.id, original_company_id)
        self.assertEqual(user.driver_profile.id, original_profile_id)

    def test_role_change_signal_only_runs_on_update(self):
        """Test that role change signal doesn't run on initial creation."""
        # Create user - signal should run once for creation
        user = User.objects.create_user(
            email="driver@example.com",
            password="testpass123",
            phone_number="1234567890",
            role=User.Role.INDIVIDUAL_DRIVER,
        )

        # Should have exactly one DriverProfile
        self.assertEqual(DriverProfile.objects.filter(user=user).count(), 1)

        # Update user without changing role
        user.first_name = "Updated"
        user.save()

        # Should still have exactly one DriverProfile (no duplicates)
        self.assertEqual(DriverProfile.objects.filter(user=user).count(), 1)

    def test_multiple_role_changes(self):
        """Test multiple role changes work correctly."""
        user = User.objects.create_user(
            email="user@example.com",
            password="testpass123",
            phone_number="1234567890",
            role=User.Role.ADMIN,
        )

        # Admin -> Individual Driver
        user.role = User.Role.INDIVIDUAL_DRIVER
        user.save()
        user.refresh_from_db()
        self.assertTrue(hasattr(user, "driver_profile"))

        # Individual Driver -> Company Owner
        user.role = User.Role.COMPANY_OWNER
        user.save()
        user.refresh_from_db()
        self.assertTrue(hasattr(user, "owned_company"))
        self.assertTrue(hasattr(user, "driver_profile"))

        # Company Owner -> Company Driver
        user.role = User.Role.COMPANY_DRIVER
        user.save()
        user.refresh_from_db()
        # Should still have all models (nothing gets deleted)
        self.assertTrue(hasattr(user, "owned_company"))
        self.assertTrue(hasattr(user, "driver_profile"))

    def test_role_change_does_not_create_duplicate_profiles(self):
        """Test that changing roles doesn't create duplicate profiles."""
        user = User.objects.create_user(
            email="driver@example.com",
            password="testpass123",
            phone_number="1234567890",
            role=User.Role.INDIVIDUAL_DRIVER,
        )

        original_profile_id = user.driver_profile.id

        # Change to company driver (both use DriverProfile)
        user.role = User.Role.COMPANY_DRIVER
        user.save()
        user.refresh_from_db()

        # Should have the same profile, not a new one
        self.assertEqual(user.driver_profile.id, original_profile_id)
        self.assertEqual(DriverProfile.objects.filter(user=user).count(), 1)

    def test_role_change_preserves_profile_data(self):
        """Test that role changes don't lose existing profile data."""
        user = User.objects.create_user(
            email="driver@example.com",
            password="testpass123",
            phone_number="1234567890",
            role=User.Role.INDIVIDUAL_DRIVER,
        )

        # Add data to driver profile
        profile = user.driver_profile
        profile.license_number = "DL123456"
        profile.address = "123 Test St"
        profile.city = "Test City"
        profile.save()

        # Change role
        user.role = User.Role.COMPANY_DRIVER
        user.save()
        user.refresh_from_db()

        # Profile data should still be there
        self.assertEqual(user.driver_profile.license_number, "DL123456")
        self.assertEqual(user.driver_profile.address, "123 Test St")
        self.assertEqual(user.driver_profile.city, "Test City")

    def test_updating_non_role_fields_does_not_trigger_role_change_logic(self):
        """Test that updating other fields doesn't trigger role change signal logic."""
        user = User.objects.create_user(
            email="driver@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
            phone_number="1234567890",
            role=User.Role.INDIVIDUAL_DRIVER,
        )

        profile_count_before = DriverProfile.objects.filter(user=user).count()

        # Update non-role fields
        user.first_name = "Jane"
        user.last_name = "Smith"
        user.email = "newdriver@example.com"
        user.save()

        # Should not create new profiles
        profile_count_after = DriverProfile.objects.filter(user=user).count()
        self.assertEqual(profile_count_before, profile_count_after)

