"""
Tests for Company and CompanyDriver models.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from accounts.models import User, Company, CompanyDriver


class CompanyTests(TestCase):
    """Test Company model functionality."""

    def setUp(self):
        """Create a company owner for tests."""
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="testpass123",
            first_name="John",
            last_name="Owner",
            phone_number="1234567890",
            role=User.Role.COMPANY_OWNER,
        )
        self.company = self.owner.owned_company

    def test_company_created_automatically(self):
        """Test that company is created automatically for owner."""
        self.assertIsNotNone(self.company)
        self.assertEqual(self.company.owner, self.owner)

    def test_company_has_invite_code(self):
        """Test that company gets an invite code generated."""
        self.assertIsNotNone(self.company.invite_code)
        self.assertEqual(len(self.company.invite_code), 12)

    def test_invite_code_is_unique(self):
        """Test that each company gets a unique invite code."""
        owner2 = User.objects.create_user(
            email="owner2@example.com",
            password="testpass123",
            phone_number="9876543210",
            role=User.Role.COMPANY_OWNER,
        )
        company2 = owner2.owned_company

        self.assertNotEqual(self.company.invite_code, company2.invite_code)

    def test_company_str_with_name(self):
        """Test Company __str__ method with name."""
        self.assertIn("Owner", str(self.company))

    def test_company_str_without_name(self):
        """Test Company __str__ when name is None."""
        self.company.name = None
        self.company.save()
        self.assertIn("Company #", str(self.company))

    def test_company_can_update_details(self):
        """Test that company details can be updated."""
        self.company.name = "Updated Company Name"
        self.company.address = "123 Main St"
        self.company.website = "https://example.com"
        self.company.save()

        # Refresh from database
        self.company.refresh_from_db()

        self.assertEqual(self.company.name, "Updated Company Name")
        self.assertEqual(self.company.address, "123 Main St")
        self.assertEqual(self.company.website, "https://example.com")

    def test_company_active_drivers_count_property(self):
        """Test active_drivers_count property."""
        # Initially no drivers
        self.assertEqual(self.company.active_drivers_count, 0)

        # Add active driver
        driver1 = User.objects.create_user(
            email="driver1@example.com",
            password="testpass123",
            role=User.Role.COMPANY_DRIVER,
            phone_number="1111111111",
        )
        CompanyDriver.objects.create(driver=driver1, company=self.company, is_active=True)
        self.assertEqual(self.company.active_drivers_count, 1)

        # Add inactive driver
        driver2 = User.objects.create_user(
            email="driver2@example.com",
            password="testpass123",
            role=User.Role.COMPANY_DRIVER,
            phone_number="2222222222",
        )
        CompanyDriver.objects.create(
            driver=driver2, company=self.company, is_active=False
        )
        self.assertEqual(self.company.active_drivers_count, 1)  # Still 1 active

    def test_company_total_drivers_count_property(self):
        """Test total_drivers_count property."""
        # Initially no drivers
        self.assertEqual(self.company.total_drivers_count, 0)

        # Add drivers
        for i in range(3):
            driver = User.objects.create_user(
                email=f"driver{i}@example.com",
                password="testpass123",
                role=User.Role.COMPANY_DRIVER,
                phone_number=f"111111111{i}",
            )
            is_active = i < 2  # First two active
            CompanyDriver.objects.create(
                driver=driver, company=self.company, is_active=is_active
            )

        self.assertEqual(self.company.total_drivers_count, 3)
        self.assertEqual(self.company.active_drivers_count, 2)

    def test_deleting_owner_deletes_company(self):
        """Test that deleting owner cascades to delete company."""
        company_id = self.company.id
        self.owner.delete()

        # Company should be deleted
        with self.assertRaises(Company.DoesNotExist):
            Company.objects.get(id=company_id)


class CompanyDriverTests(TestCase):
    """Test CompanyDriver junction model."""

    def setUp(self):
        """Set up test data."""
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="testpass123",
            role=User.Role.COMPANY_OWNER,
            phone_number="1234567890",
        )
        self.company = self.owner.owned_company

    def test_add_driver_to_company(self):
        """Test adding a driver to a company."""
        driver = User.objects.create_user(
            email="driver@example.com",
            password="testpass123",
            role=User.Role.COMPANY_DRIVER,
            phone_number="1111111111",
        )

        company_driver = CompanyDriver.objects.create(
            driver=driver, company=self.company
        )

        self.assertEqual(company_driver.driver, driver)
        self.assertEqual(company_driver.company, self.company)
        self.assertTrue(company_driver.is_active)

    def test_multiple_drivers_per_company(self):
        """Test that a company can have multiple drivers."""
        drivers = []
        for i in range(5):
            driver = User.objects.create_user(
                email=f"driver{i}@example.com",
                password="testpass123",
                role=User.Role.COMPANY_DRIVER,
                phone_number=f"111111111{i}",
            )
            CompanyDriver.objects.create(driver=driver, company=self.company)
            drivers.append(driver)

        # Test that company has all 5 drivers
        self.assertEqual(self.company.drivers.count(), 5)
        self.assertEqual(self.company.total_drivers_count, 5)

    def test_driver_can_work_for_multiple_companies(self):
        """Test that a driver can be associated with multiple companies."""
        # Create another owner and company
        owner2 = User.objects.create_user(
            email="owner2@example.com",
            password="testpass123",
            role=User.Role.COMPANY_OWNER,
            phone_number="9876543210",
        )
        company2 = owner2.owned_company

        # Create a driver
        driver = User.objects.create_user(
            email="driver@example.com",
            password="testpass123",
            role=User.Role.COMPANY_DRIVER,
            phone_number="1111111111",
        )

        # Add driver to both companies
        CompanyDriver.objects.create(driver=driver, company=self.company)
        CompanyDriver.objects.create(driver=driver, company=company2)

        # Verify driver is in both companies
        self.assertEqual(driver.company_memberships.count(), 2)

    def test_cannot_add_same_driver_twice_to_same_company(self):
        """Test that unique_together constraint prevents duplicates."""
        driver = User.objects.create_user(
            email="driver@example.com",
            password="testpass123",
            role=User.Role.COMPANY_DRIVER,
            phone_number="1111111111",
        )

        CompanyDriver.objects.create(driver=driver, company=self.company)

        # Try to add same driver again to same company
        with self.assertRaises(Exception):  # Will raise IntegrityError
            CompanyDriver.objects.create(driver=driver, company=self.company)

    def test_company_driver_str_method(self):
        """Test CompanyDriver __str__ method."""
        driver = User.objects.create_user(
            email="driver@example.com",
            password="testpass123",
            first_name="Test",
            last_name="Driver",
            role=User.Role.COMPANY_DRIVER,
            phone_number="1111111111",
        )

        company_driver = CompanyDriver.objects.create(
            driver=driver, company=self.company
        )

        str_repr = str(company_driver)
        self.assertIn("Test Driver", str_repr)

    def test_company_driver_is_active_default(self):
        """Test that is_active defaults to True."""
        driver = User.objects.create_user(
            email="driver@example.com",
            password="testpass123",
            role=User.Role.COMPANY_DRIVER,
            phone_number="1111111111",
        )

        company_driver = CompanyDriver.objects.create(
            driver=driver, company=self.company
        )

        self.assertTrue(company_driver.is_active)

    def test_deactivate_company_driver(self):
        """Test deactivating a company driver."""
        driver = User.objects.create_user(
            email="driver@example.com",
            password="testpass123",
            role=User.Role.COMPANY_DRIVER,
            phone_number="1111111111",
        )

        company_driver = CompanyDriver.objects.create(
            driver=driver, company=self.company
        )

        # Deactivate
        company_driver.is_active = False
        company_driver.save()

        company_driver.refresh_from_db()
        self.assertFalse(company_driver.is_active)

    def test_company_driver_validation_wrong_role(self):
        """Test that only appropriate roles can be company drivers."""
        admin = User.objects.create_user(
            email="admin@example.com", password="testpass123", role=User.Role.ADMIN
        )

        company_driver = CompanyDriver(driver=admin, company=self.company)

        # Should raise ValidationError when clean() is called
        with self.assertRaises(ValidationError) as cm:
            company_driver.clean()

        self.assertIn("role", str(cm.exception).lower())

    def test_company_driver_validation_accepts_company_driver_role(self):
        """Test that COMPANY_DRIVER role passes validation."""
        driver = User.objects.create_user(
            email="driver@example.com",
            password="testpass123",
            role=User.Role.COMPANY_DRIVER,
            phone_number="1111111111",
        )

        company_driver = CompanyDriver(driver=driver, company=self.company)

        # Should not raise ValidationError
        try:
            company_driver.clean()
        except ValidationError:
            self.fail("Validation should pass for COMPANY_DRIVER role")

    def test_company_driver_validation_accepts_company_owner_role(self):
        """Test that COMPANY_OWNER role passes validation."""
        owner = User.objects.create_user(
            email="owner2@example.com",
            password="testpass123",
            role=User.Role.COMPANY_OWNER,
            phone_number="9999999999",
        )

        company_driver = CompanyDriver(driver=owner, company=self.company)

        # Should not raise ValidationError
        try:
            company_driver.clean()
        except ValidationError:
            self.fail("Validation should pass for COMPANY_OWNER role")

    def test_deleting_driver_deletes_company_driver_relation(self):
        """Test that deleting driver cascades to delete CompanyDriver."""
        driver = User.objects.create_user(
            email="driver@example.com",
            password="testpass123",
            role=User.Role.COMPANY_DRIVER,
            phone_number="1111111111",
        )

        company_driver = CompanyDriver.objects.create(
            driver=driver, company=self.company
        )
        cd_id = company_driver.id

        driver.delete()

        # CompanyDriver should be deleted
        with self.assertRaises(CompanyDriver.DoesNotExist):
            CompanyDriver.objects.get(id=cd_id)

    def test_deleting_company_deletes_company_driver_relation(self):
        """Test that deleting company cascades to delete CompanyDriver."""
        driver = User.objects.create_user(
            email="driver@example.com",
            password="testpass123",
            role=User.Role.COMPANY_DRIVER,
            phone_number="1111111111",
        )

        company_driver = CompanyDriver.objects.create(
            driver=driver, company=self.company
        )
        cd_id = company_driver.id

        self.company.delete()

        # CompanyDriver should be deleted
        with self.assertRaises(CompanyDriver.DoesNotExist):
            CompanyDriver.objects.get(id=cd_id)

