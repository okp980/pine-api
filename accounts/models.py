from django.db import models
from django.contrib.auth.models import AbstractUser
from hashids import Hashids
from django.conf import settings
from django.utils import timezone

# Create your models here.


class User(AbstractUser):
    username = None
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        COMPANY_OWNER = "COMPANY_OWNER", "Company Owner"
        INDIVIDUAL_DRIVER = "INDIVIDUAL_DRIVER", "Individual Driver"
        COMPANY_DRIVER = "COMPANY_DRIVER", "Company Driver"

    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.INDIVIDUAL_DRIVER
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone_number"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Company(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    website = models.URLField(max_length=255, null=True, blank=True)
    logo = models.ImageField(upload_to="company/logos/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    invite_code = models.CharField(max_length=12, unique=True, editable=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.invite_code:  # Only generate if not already set
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
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)


class CompanyDriver(models.Model):
    driver = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.OneToOneField(Company, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.driver.first_name} {self.driver.last_name}"

    class Meta:
        unique_together = ["driver", "company"]


class CommonProfile(models.Model):
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

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    class Meta:
        abstract = True


class Profile(CommonProfile):
    pass


class DriverProfile(CommonProfile):
    license_number = models.CharField(max_length=64, blank=True)
    license_class = models.CharField(max_length=32, blank=True)
    license_expiry = models.DateField(null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=128, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)

    verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def mark_verified(self):
        self.verified = True
        self.verified_at = timezone.now()
        self.save(update_fields=["verified", "verified_at"])
