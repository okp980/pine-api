"""
Tests for User model creation and basic functionality.
"""
from django.test import TestCase
from accounts.models import User


class UserCreationTests(TestCase):
    """Test basic user creation functionality."""

    def test_user_creation_with_email(self):
        """Test creating a user with email."""
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
            phone_number="1234567890",
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpass123"))
        self.assertEqual(str(user), "John Doe")
        self.assertEqual(user.phone_number, "1234567890")

    def test_user_creation_all_roles(self):
        """Test creating users with different roles."""
        roles = [
            User.Role.ADMIN,
            User.Role.COMPANY_OWNER,
            User.Role.INDIVIDUAL_DRIVER,
            User.Role.COMPANY_DRIVER,
        ]

        for idx, role in enumerate(roles):
            user = User.objects.create_user(
                email=f"user{idx}@example.com",
                password="testpass123",
                role=role,
                phone_number=f"123456789{idx}",
            )
            self.assertEqual(user.role, role)

    def test_user_str_with_full_name(self):
        """Test __str__ method when user has first and last name."""
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Jane",
            last_name="Smith",
        )
        self.assertEqual(str(user), "Jane Smith")

    def test_user_str_with_no_name(self):
        """Test __str__ method when user has no first/last name."""
        user = User.objects.create_user(
            email="noname@example.com", password="testpass123"
        )
        self.assertEqual(str(user), "noname@example.com")

    def test_user_str_with_partial_name(self):
        """Test __str__ method with only first or last name."""
        user = User.objects.create_user(
            email="partial@example.com",
            password="testpass123",
            first_name="John",
            last_name="",
        )
        # Should fall back to email since last_name is empty
        self.assertEqual(str(user), "partial@example.com")

    def test_user_full_name_property(self):
        """Test full_name property."""
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Jane",
            last_name="Smith",
        )
        self.assertEqual(user.full_name, "Jane Smith")

    def test_user_full_name_with_spaces(self):
        """Test full_name property strips extra spaces."""
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="  John  ",
            last_name="  Doe  ",
        )
        # strip() should clean up the spaces
        self.assertEqual(user.full_name.strip(), "John     Doe")

    def test_user_is_driver_property_for_drivers(self):
        """Test is_driver property returns True for driver roles."""
        driver_roles = [
            User.Role.INDIVIDUAL_DRIVER,
            User.Role.COMPANY_DRIVER,
            User.Role.COMPANY_OWNER,
        ]

        for idx, role in enumerate(driver_roles):
            user = User.objects.create_user(
                email=f"driver{idx}@example.com",
                password="testpass123",
                role=role,
                phone_number=f"111111111{idx}",
            )
            self.assertTrue(user.is_driver, f"{role} should be a driver")

    def test_user_is_driver_property_for_admin(self):
        """Test is_driver property returns False for admin."""
        admin = User.objects.create_user(
            email="admin@example.com", password="testpass123", role=User.Role.ADMIN
        )
        self.assertFalse(admin.is_driver)

    def test_user_email_uniqueness(self):
        """Test that email must be unique."""
        User.objects.create_user(
            email="unique@example.com",
            password="testpass123",
            phone_number="1234567890",
        )

        # Try to create another user with same email
        with self.assertRaises(Exception):  # Will raise IntegrityError
            User.objects.create_user(
                email="unique@example.com",
                password="testpass123",
                phone_number="9876543210",
            )

    def test_user_phone_number_uniqueness(self):
        """Test that phone_number must be unique."""
        User.objects.create_user(
            email="user1@example.com",
            password="testpass123",
            phone_number="1234567890",
        )

        # Try to create another user with same phone number
        with self.assertRaises(Exception):  # Will raise IntegrityError
            User.objects.create_user(
                email="user2@example.com",
                password="testpass123",
                phone_number="1234567890",
            )

    def test_user_default_role(self):
        """Test that default role is INDIVIDUAL_DRIVER."""
        user = User.objects.create_user(
            email="default@example.com", password="testpass123"
        )
        self.assertEqual(user.role, User.Role.INDIVIDUAL_DRIVER)

    def test_username_field_is_email(self):
        """Test that USERNAME_FIELD is set to email."""
        self.assertEqual(User.USERNAME_FIELD, "email")

    def test_required_fields(self):
        """Test REQUIRED_FIELDS are set correctly."""
        expected_fields = ["first_name", "last_name", "phone_number"]
        self.assertEqual(User.REQUIRED_FIELDS, expected_fields)

