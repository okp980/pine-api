from django.db import models
from accounts.models import User
from vehicles.models import Vehicle
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class Trip(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ASSIGNED = "ASSIGNED", "Assigned"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    recipient_name = models.CharField(max_length=255)
    recipient_phone = models.CharField(max_length=20)
    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="driver_trips",
        null=True,
        blank=True,
    )
    company = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="company_trips",
    )
    vehicle_type = models.CharField(max_length=255, choices=Vehicle.Type.choices)
    pickup_address = models.TextField(max_length=255)
    delivery_address = models.TextField(max_length=255)
    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    delivery_latitude = models.FloatField()
    delivery_longitude = models.FloatField()
    pickup_time = models.DateTimeField()
    assigned_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    otp_code = models.CharField(max_length=6, null=True, blank=True)
    status = models.CharField(
        max_length=255, choices=Status.choices, default=Status.PENDING
    )
    rating = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
