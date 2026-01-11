# Vehicle Tests

This directory contains comprehensive tests for the vehicles application, organized into separate modules for better maintainability and clarity.

## Test Structure

```
vehicles/tests/
├── __init__.py              # Test package initializer
├── test_models.py          # Model-related tests
├── test_serializers.py     # Serializer tests
├── test_views.py           # ViewSet/API endpoint tests
├── test_permissions.py     # Permission class tests
└── README.md               # This file
```

## Test Files

### 1. `test_models.py`
Tests for the `Vehicle` model including:
- Vehicle creation
- String representation
- Driver-vehicle relationship (ForeignKey)
- Multiple vehicles per driver
- Cascade deletion when driver is deleted

**Test Count:** 5 tests

### 2. `test_serializers.py`
Tests for the `VehicleSerializer`:
- Serializer field validation
- Expected fields presence
- Data serialization

**Test Count:** 2 tests

### 3. `test_views.py`
Tests for the `VehicleViewSet` API endpoints:
- List vehicles (with authentication)
- Retrieve vehicle details
- Create new vehicles
- Update existing vehicles
- Delete vehicles
- Queryset filtering by authenticated user
- Permission checks for different user roles

**Test Count:** 13 tests

### 4. `test_permissions.py`
Tests for permission classes:
- Individual driver access
- Company driver access
- Company owner access
- Admin access (denied)
- Unauthenticated user access (denied)

**Test Count:** 5 tests

## Running Tests

### Run all vehicle tests:
```bash
python manage.py test vehicles
```

### Run specific test file:
```bash
python manage.py test vehicles.tests.test_models
python manage.py test vehicles.tests.test_serializers
python manage.py test vehicles.tests.test_views
python manage.py test vehicles.tests.test_permissions
```

### Run specific test class:
```bash
python manage.py test vehicles.tests.test_models.VehicleModelTest
python manage.py test vehicles.tests.test_permissions.VehiclePermissionsTest
```

### Run specific test method:
```bash
python manage.py test vehicles.tests.test_models.VehicleModelTest.test_vehicle_creation
python manage.py test vehicles.tests.test_views.VehicleViewSetTest.test_create_vehicle_as_individual_driver
```

### Run with verbose output:
```bash
python manage.py test vehicles --verbosity=2
```

### Run with test coverage:
```bash
coverage run --source='vehicles' manage.py test vehicles
coverage report
coverage html  # Generate HTML report
```

## Test Data Setup

Each test class has a `setUp` method that creates:
- Test users with different roles (Individual Driver, Company Driver, Company Owner, Admin)
- Test vehicles with all required fields and file uploads
- Mock file uploads for documents (road worthiness certificate, insurance, inspection report)

## Assertions Used

- `assertEqual` - Check for exact matches
- `assertNotEqual` - Check for non-matches
- `assertIsNotNone` - Check that values exist
- `assertIn` - Check item membership
- `assertTrue/assertFalse` - Boolean checks
- `assertRaises` - Check exception handling
- `assertGreaterEqual` - Numerical comparisons

## Common Test Patterns

### API Testing Pattern:
```python
def test_something(self):
    self.client.force_authenticate(user=self.user)
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    # Additional assertions
```

### Model Testing Pattern:
```python
def test_something(self):
    obj = Model.objects.create(**self.data)
    self.assertEqual(obj.field, expected_value)
```

## Important Notes

1. **File Uploads:** Tests use `SimpleUploadedFile` to mock file uploads
2. **Authentication:** Most view tests require user authentication via `force_authenticate()`
3. **User Roles:** Tests verify role-based access control
4. **Queryset Filtering:** Tests ensure users only see their own vehicles
5. **Database:** Tests use a separate test database that's created and destroyed automatically

## Test Coverage Goals

- **Models:** 100% coverage of model methods and properties
- **Serializers:** All fields and validation logic
- **Views:** All CRUD operations and permissions
- **Permissions:** All permission classes and edge cases

## Adding New Tests

When adding new tests:

1. **Choose the right file:** Put tests in the appropriate module
2. **Follow naming conventions:** Use `test_` prefix for test methods
3. **Write descriptive docstrings:** Explain what the test is checking
4. **Clean up:** Ensure tests clean up any created data
5. **Independence:** Each test should be independent and not rely on others

### Example New Test:
```python
def test_new_functionality(self):
    """Test description here"""
    # Setup
    data = {}
    
    # Execute
    result = something()
    
    # Assert
    self.assertEqual(result, expected)
```

## Troubleshooting

### Missing Table Errors
If you see `no such table: vehicles_vehicle`:
```bash
python manage.py makemigrations vehicles
python manage.py migrate
```

### Permission Failures
If permission tests fail, check:
- User roles are correctly assigned
- Permission classes are properly configured in views
- Permission logic matches test expectations

### File Upload Failures
Ensure test files are created with proper content type:
```python
SimpleUploadedFile("file.pdf", b"content", content_type="application/pdf")
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines. They:
- Don't require external services
- Use in-memory test database
- Complete quickly
- Provide clear failure messages

## Best Practices

1. ✅ Keep tests focused and atomic
2. ✅ Use descriptive test names
3. ✅ Test both success and failure cases
4. ✅ Mock external dependencies
5. ✅ Maintain test data isolation
6. ✅ Write tests before fixing bugs
7. ✅ Update tests when adding features

