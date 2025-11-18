"""
Test suite for accounts app.

This package contains comprehensive tests for:
- User creation and authentication
- Signal handlers for auto-creating related models
- Company and CompanyDriver relationships
- Profile and DriverProfile functionality
- Role change behavior

To run all tests:
    python manage.py test accounts

To run specific test file:
    python manage.py test accounts.tests.test_signals

To run specific test class:
    python manage.py test accounts.tests.test_signals.SignalTests

To run specific test method:
    python manage.py test accounts.tests.test_signals.SignalTests.test_admin_gets_profile
"""

# Import all test classes for test discovery
from .test_user_creation import UserCreationTests
from .test_signals import SignalTests
from .test_company import CompanyTests, CompanyDriverTests
from .test_profiles import AdminProfileTests, DriverProfileTests
from .test_role_changes import RoleChangeTests

__all__ = [
    "UserCreationTests",
    "SignalTests",
    "CompanyTests",
    "CompanyDriverTests",
    "AdminProfileTests",
    "DriverProfileTests",
    "RoleChangeTests",
]

