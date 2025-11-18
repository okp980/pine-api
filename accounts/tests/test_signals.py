"""
Tests for signal handlers that auto-create related models.
"""
from django.test import TestCase
from accounts.models import User, Company, AdminProfile, DriverProfile


class SignalTests(TestCase):
    """Test that signals create appropriate related models on user creation."""

    def test_admin_gets_profile(self):
        """Test that admin user gets an AdminProfile created automatically."""
        user = User.objects.create_user(
            email="admin@example.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            role=User.Role.ADMIN,
        )

        # Check that AdminProfile was created by signal
        self.assertTrue(hasattr(user, "profile"))
        self.assertIsInstance(user.profile, AdminProfile)
        self.assertEqual(user.profile.user, user)

    def test_individual_driver_gets_driver_profile(self):
        """Test that individual driver gets DriverProfile automatically."""
        user = User.objects.create_user(
            email="driver@example.com",
            password="testpass123",
            first_name="Driver",
            last_name="One",
            phone_number="1234567890",
            role=User.Role.INDIVIDUAL_DRIVER,
        )

        # Check that DriverProfile was created by signal
        self.assertTrue(hasattr(user, "driver_profile"))
        self.assertIsInstance(user.driver_profile, DriverProfile)
        self.assertEqual(user.driver_profile.user, user)
        self.assertFalse(user.driver_profile.verified)

    def test_company_owner_gets_company_and_driver_profile(self):
        """Test that company owner gets both Company and DriverProfile."""
        user = User.objects.create_user(
            email="owner@example.com",
            password="testpass123",
            first_name="Company",
            last_name="Owner",
            phone_number="1234567890",
            role=User.Role.COMPANY_OWNER,
        )

        # Check that both Company and DriverProfile were created
        self.assertTrue(hasattr(user, "owned_company"))
        self.assertTrue(hasattr(user, "driver_profile"))
        self.assertIsInstance(user.owned_company, Company)
        self.assertIsInstance(user.driver_profile, DriverProfile)
        self.assertEqual(user.owned_company.owner, user)
        self.assertEqual(user.driver_profile.user, user)

    def test_company_driver_gets_driver_profile(self):
        """Test that company driver gets DriverProfile automatically."""
        user = User.objects.create_user(
            email="companydriver@example.com",
            password="testpass123",
            first_name="Company",
            last_name="Driver",
            phone_number="1234567890",
            role=User.Role.COMPANY_DRIVER,
        )

        self.assertTrue(hasattr(user, "driver_profile"))
        self.assertIsInstance(user.driver_profile, DriverProfile)
        self.assertEqual(user.driver_profile.user, user)

    def test_signal_sets_default_company_name(self):
        """Test that company gets default name from user's name."""
        user = User.objects.create_user(
            email="owner@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
            phone_number="1234567890",
            role=User.Role.COMPANY_OWNER,
        )

        company = user.owned_company
        self.assertIn("John Doe", company.name)

    def test_signal_copies_user_contact_info_to_company(self):
        """Test that company inherits user's email and phone."""
        user = User.objects.create_user(
            email="owner@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
            phone_number="1234567890",
            role=User.Role.COMPANY_OWNER,
        )

        company = user.owned_company
        self.assertEqual(company.email, user.email)
        self.assertEqual(company.phone_number, user.phone_number)

    def test_signal_does_not_create_duplicate_profiles(self):
        """Test that signal doesn't create duplicate profiles on subsequent saves."""
        user = User.objects.create_user(
            email="driver@example.com",
            password="testpass123",
            first_name="Driver",
            last_name="One",
            phone_number="1234567890",
            role=User.Role.INDIVIDUAL_DRIVER,
        )

        # Get the original profile ID
        original_profile_id = user.driver_profile.id

        # Update the user (should not create new profile)
        user.first_name = "Updated"
        user.save()

        # Refresh from database
        user.refresh_from_db()

        # Should still have the same profile
        self.assertEqual(user.driver_profile.id, original_profile_id)

    def test_multiple_users_each_get_their_profiles(self):
        """Test that multiple users each get their own profiles."""
        users = []
        for i in range(5):
            user = User.objects.create_user(
                email=f"driver{i}@example.com",
                password="testpass123",
                phone_number=f"123456789{i}",
                role=User.Role.INDIVIDUAL_DRIVER,
            )
            users.append(user)

        # Each user should have their own profile
        for user in users:
            self.assertTrue(hasattr(user, "driver_profile"))
            self.assertEqual(user.driver_profile.user, user)

        # Verify we have 5 distinct profiles
        profile_ids = [user.driver_profile.id for user in users]
        self.assertEqual(len(set(profile_ids)), 5)

    def test_admin_does_not_get_driver_profile(self):
        """Test that admin doesn't accidentally get DriverProfile."""
        user = User.objects.create_user(
            email="admin@example.com",
            password="testpass123",
            role=User.Role.ADMIN,
        )

        # Should have profile but not driver_profile
        self.assertTrue(hasattr(user, "profile"))
        self.assertFalse(hasattr(user, "driver_profile"))

    def test_admin_does_not_get_company(self):
        """Test that admin doesn't accidentally get Company."""
        user = User.objects.create_user(
            email="admin@example.com",
            password="testpass123",
            role=User.Role.ADMIN,
        )

        # Should not have company
        self.assertFalse(hasattr(user, "owned_company"))

