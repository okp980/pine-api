# Accounts App Test Suite

Comprehensive test suite for the Pine API accounts app, covering user creation, signals, profiles, companies, and role management.

## Test Structure

```
accounts/tests/
├── __init__.py                 # Test discovery and imports
├── test_user_creation.py       # User model creation tests
├── test_signals.py             # Signal handler tests
├── test_company.py             # Company and CompanyDriver tests
├── test_profiles.py            # Profile and DriverProfile tests
├── test_role_changes.py        # User role change tests
└── README.md                   # This file
```

## Running Tests

### Run All Tests
```bash
python manage.py test accounts
```

### Run Specific Test File
```bash
python manage.py test accounts.tests.test_signals
python manage.py test accounts.tests.test_company
python manage.py test accounts.tests.test_profiles
```

### Run Specific Test Class
```bash
python manage.py test accounts.tests.test_signals.SignalTests
python manage.py test accounts.tests.test_company.CompanyTests
```

### Run Specific Test Method
```bash
python manage.py test accounts.tests.test_signals.SignalTests.test_admin_gets_profile
```

### Run with Verbose Output
```bash
python manage.py test accounts --verbosity=2
```

### Run with Test Coverage
```bash
# Install coverage first
pip install coverage

# Run tests with coverage
coverage run --source='accounts' manage.py test accounts

# View coverage report
coverage report

# Generate HTML coverage report
coverage html
# Open htmlcov/index.html in your browser
```

## Test Coverage

### test_user_creation.py (17 tests)
- ✅ User creation with email and password
- ✅ User creation for all roles
- ✅ `__str__` method behavior
- ✅ `full_name` property
- ✅ `is_driver` property
- ✅ Email and phone number uniqueness
- ✅ Default role assignment
- ✅ USERNAME_FIELD and REQUIRED_FIELDS

### test_signals.py (11 tests)
- ✅ Admin users get Profile
- ✅ Individual drivers get DriverProfile
- ✅ Company owners get Company + DriverProfile
- ✅ Company drivers get DriverProfile
- ✅ Default company name from user
- ✅ Company inherits user contact info
- ✅ No duplicate profiles on update
- ✅ Multiple users get separate profiles
- ✅ Role-specific profile creation

### test_company.py (20 tests)
- ✅ Company auto-creation for owners
- ✅ Unique invite code generation
- ✅ Company `__str__` method
- ✅ Company details updates
- ✅ Active/total drivers count
- ✅ Multiple drivers per company (ForeignKey)
- ✅ Driver can work for multiple companies
- ✅ Unique constraint on driver-company pair
- ✅ CompanyDriver validation for roles
- ✅ Cascade deletion behavior

### test_profiles.py (25 tests)
- ✅ Profile auto-creation
- ✅ Profile field updates
- ✅ Age calculation from date_of_birth
- ✅ Timestamps (created_at, updated_at)
- ✅ DriverProfile license information
- ✅ Emergency contact information
- ✅ `mark_verified()` method
- ✅ License expiry validation
- ✅ `is_license_expired` property
- ✅ `license_expiry_days` calculation
- ✅ CommonProfile field inheritance
- ✅ Cascade deletion behavior

### test_role_changes.py (13 tests)
- ✅ Admin to driver creates DriverProfile
- ✅ Driver to company owner creates Company
- ✅ Multiple role changes handled correctly
- ✅ No duplicate profiles created
- ✅ Profile data preserved during role change
- ✅ Non-role field updates don't trigger signals
- ✅ Existing models retained on role change

## Key Test Scenarios

### 1. User Registration Flow
Tests verify that when a user registers with a specific role, all appropriate related models are automatically created through signals.

### 2. Signal Automation
Tests confirm that the `post_save` signals correctly create:
- `Profile` for admins
- `DriverProfile` for all driver types
- `Company` for company owners

### 3. Company Management
Tests ensure that:
- Companies can have multiple drivers (ForeignKey relationship)
- Invite codes are unique and auto-generated
- Driver counts are accurate

### 4. Profile Management
Tests validate:
- Profile fields can be updated
- Driver license validation works
- Age and license expiry calculations are correct
- Verification workflow functions properly

### 5. Role Changes
Tests verify that:
- Changing roles creates missing models
- Existing data is preserved
- No duplicates are created

## Test Data Conventions

- **Emails**: `user@example.com`, `driver1@example.com`, etc.
- **Passwords**: `testpass123` (consistent across tests)
- **Phone Numbers**: `1234567890`, `111111111X` patterns
- **Names**: Descriptive (e.g., "Admin User", "Test Driver")

## Writing New Tests

When adding new tests:

1. Choose the appropriate test file based on functionality
2. Follow existing naming conventions (`test_<description>`)
3. Use descriptive docstrings
4. Clean up test data in `setUp()` or use transactions
5. Test both success and failure cases
6. Verify edge cases (null values, empty strings, etc.)

## Common Test Patterns

### Testing Signal Creation
```python
def test_signal_creates_model(self):
    user = User.objects.create_user(
        email="test@example.com",
        password="testpass123",
        role=User.Role.SOME_ROLE
    )
    self.assertTrue(hasattr(user, 'related_model'))
```

### Testing Validation
```python
def test_validation_error(self):
    obj = SomeModel(invalid_field="bad_value")
    with self.assertRaises(ValidationError) as cm:
        obj.clean()
    self.assertIn('field_name', cm.exception.message_dict)
```

### Testing Properties
```python
def test_property_calculation(self):
    obj.some_field = value
    obj.save()
    self.assertEqual(obj.calculated_property, expected_value)
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines. Ensure:
- Database is properly configured (SQLite for testing)
- All dependencies are installed
- Migrations are up to date

## Troubleshooting

### Tests Failing After Model Changes
```bash
# Delete test database and recreate
python manage.py test accounts --keepdb=False

# Create fresh migrations
python manage.py makemigrations
python manage.py migrate
```

### Signal Tests Failing
Ensure `accounts.apps.AccountsConfig.ready()` is properly importing signals.

### Relationship Tests Failing
Check that `related_name` attributes match between models and tests.

## Total Test Count

**86 comprehensive tests** covering all aspects of the accounts app.

---

**Last Updated**: November 18, 2025
**Maintained By**: Pine API Team

