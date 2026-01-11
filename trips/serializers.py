from rest_framework import serializers
from trips.models import Trip
from accounts.models import User


class TripSerializer(serializers.ModelSerializer):

    class Meta:
        model = Trip
        fields = "__all__"


class TripAssignSerializer(serializers.Serializer):
    driver = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.COMPANY_DRIVER)
    )

    def validate(self, attrs):
        if attrs.get("driver") is None:
            raise serializers.ValidationError({"driver": "Driver is required"})
        if attrs.get("driver").role != User.Role.COMPANY_DRIVER:
            raise serializers.ValidationError(
                {"driver": "Driver must be a company driver"}
            )
        return attrs
