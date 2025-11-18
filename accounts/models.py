from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from hashids import Hashids
from django.conf import settings
from django.utils import timezone

# Create your models here.


class User(AbstractUser):
    """
    Custom User model with email as the primary identifier.
    Supports multiple roles: Admin, Company Owner, Individual Driver, Company Driver.
    """

    username = None
    phone_number = models.CharField(
        max_length=20, unique=True, null=True, blank=True, db_index=True
    )
    email = models.EmailField(max_length=255, unique=True, db_index=True)

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        COMPANY_OWNER = "COMPANY_OWNER", "Company Owner"
        INDIVIDUAL_DRIVER = "INDIVIDUAL_DRIVER", "Individual Driver"
        COMPANY_DRIVER = "COMPANY_DRIVER", "Company Driver"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.INDIVIDUAL_DRIVER,
        db_index=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone_number"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]
        indexes = [
            models.Index(fields=["email", "role"]),
        ]

    def __str__(self):
        """Return user's full name or fallback to email/id."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email or f"User #{self.id}"

    @property
    def is_driver(self):
        """Check if user has any driver role."""
        return self.role in [
            self.Role.INDIVIDUAL_DRIVER,
            self.Role.COMPANY_DRIVER,
            self.Role.COMPANY_OWNER,
        ]

    @property
    def full_name(self):
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}".strip()


class Company(models.Model):
    """
    Company model representing a business entity with an owner and drivers.
    Each company has a unique invite code for driver onboarding.
    """

    name = models.CharField(max_length=255, null=True, blank=True)
    owner = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="owned_company"
    )
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    website = models.URLField(max_length=255, null=True, blank=True)
    logo = models.ImageField(upload_to="company/logos/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    invite_code = models.CharField(
        max_length=12, unique=True, editable=False, blank=True, db_index=True
    )

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ["-created_at"]

    def __str__(self):
        """Return company name or fallback to company ID."""
        return self.name or f"Company #{self.id}"

    def save(self, *args, **kwargs):
        """Override save to generate unique invite code."""
        if not self.invite_code:
            # Save first to get an ID
            if not self.pk:
                super().save(*args, **kwargs)

            # Now generate the invite code with the ID
            hashids = Hashids(
                salt=settings.SECRET_KEY,
                min_length=12,
                alphabet="ABCDEFGHJKLMNPQRSTUVWXYZ23456789",
            )
            self.invite_code = hashids.encode(self.id)
            # Only update the invite_code field to avoid double save overhead
            super().save(update_fields=["invite_code"])
        else:
            super().save(*args, **kwargs)

    @property
    def active_drivers_count(self):
        """Get count of active drivers in the company."""
        return self.drivers.filter(is_active=True).count()

    @property
    def total_drivers_count(self):
        """Get total count of all drivers (active and inactive)."""
        return self.drivers.count()


class CompanyDriver(models.Model):
    """
    Junction model representing the relationship between drivers and companies.
    A company can have multiple drivers, and a driver can work for multiple companies.
    """

    driver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="company_memberships"
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="drivers"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Company Driver"
        verbose_name_plural = "Company Drivers"
        unique_together = ["driver", "company"]
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "is_active"]),
            models.Index(fields=["driver", "is_active"]),
        ]

    def __str__(self):
        """Return driver's full name and company."""
        return f"{self.driver.full_name} - {self.company.name or 'Company'}"

    def clean(self):
        """Validate that driver has appropriate role."""
        super().clean()
        if self.driver.role not in [
            User.Role.COMPANY_DRIVER,
            User.Role.COMPANY_OWNER,
        ]:
            raise ValidationError(
                "User must have COMPANY_DRIVER or COMPANY_OWNER role to be added to a company."
            )


class CommonProfile(models.Model):
    """
    Abstract base class for user profiles.
    Contains common fields shared by all profile types.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="profile/images/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=128, blank=True)
    state = models.CharField(max_length=128, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=128, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        """Return user's full name."""
        return self.user.full_name or str(self.user)

    @property
    def age(self):
        """Calculate user's age from date of birth."""
        if not self.date_of_birth:
            return None
        today = timezone.now().date()
        return (
            today.year
            - self.date_of_birth.year
            - (
                (today.month, today.day)
                < (self.date_of_birth.month, self.date_of_birth.day)
            )
        )


class Profile(CommonProfile):
    """
    Basic profile for non-driver users (e.g., admins).
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        ordering = ["-created_at"]


class DriverProfile(CommonProfile):
    """
    Extended profile for drivers with license and verification information.
    Used by Individual Drivers, Company Drivers, and Company Owners.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="driver_profile"
    )
    license_number = models.CharField(max_length=64, blank=True)
    license_class = models.CharField(max_length=32, blank=True)
    license_expiry = models.DateField(null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=128, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Driver Profile"
        verbose_name_plural = "Driver Profiles"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["verified", "license_expiry"]),
        ]

    def clean(self):
        """Validate driver profile data."""
        super().clean()
        if self.license_expiry and self.license_expiry < timezone.now().date():
            raise ValidationError(
                {
                    "license_expiry": "License has expired. Please update with valid license."
                }
            )
        if self.verified and not self.verified_at:
            raise ValidationError(
                {"verified_at": "Verified date must be set when profile is verified."}
            )

    def mark_verified(self):
        """Mark the driver profile as verified."""
        self.verified = True
        self.verified_at = timezone.now()
        self.save(update_fields=["verified", "verified_at"])

    @property
    def is_license_expired(self):
        """Check if driver's license is expired."""
        if not self.license_expiry:
            return None
        return self.license_expiry < timezone.now().date()

    @property
    def license_expiry_days(self):
        """Calculate days until license expires (negative if expired)."""
        if not self.license_expiry:
            return None
        delta = self.license_expiry - timezone.now().date()
        return delta.days
