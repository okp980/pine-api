from django.db import models
from accounts.models import User


# Create your models here.
class Vehicle(models.Model):
    driver = models.ForeignKey(User, on_delete=models.CASCADE)
    brand = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    year = models.IntegerField()
    license_number = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=255)
    expiry_date = models.DateField()
    colour = models.CharField(max_length=255)
    road_worthiness_certificate = models.FileField(upload_to="road_worthiness/")
    vehicle_insurance = models.FileField(upload_to="vehicle_insurances/")
    inspection_report = models.FileField(upload_to="inspection_reports/")
