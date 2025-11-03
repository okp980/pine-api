from auth_kit.serializers import RegisterSerializer
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.validators import PhoneNumberValidator
from accounts.models import User
from rest_framework.validators import UniqueValidator


class RegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required=True, max_length=30)
    phone_number = serializers.CharField(required=False, max_length=20)
    email = serializers.EmailField(
        required=True,
        max_length=255,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    password = serializers.CharField(required=True, max_length=128)
    role = serializers.ChoiceField(choices=User.Role.choices, required=True)

    def validate_phone_number(self, value):
        if value and not value.startswith("+"):
            raise serializers.ValidationError("Phone number must start with '+'")
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already exists")
        return value
