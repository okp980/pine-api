from auth_kit.serializers import RegisterSerializer
from auth_kit.serializers.login_factors import LoginRequestSerializer
from rest_framework import serializers
from accounts.models import User
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator
import re


EMAIL_RE = re.compile(r".+@.+\..+")


def normalize_phone(s: str) -> str:
    # minimal normalization; swap to `phonenumbers` for strict parsing
    return s.replace(" ", "").replace("-", "")


class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required=True, max_length=30)
    phone_number = serializers.CharField(
        required=False,
        min_length=11,
        max_length=11,
        validators=[
            RegexValidator(
                regex=r"^\d+$",
                message="Invalid phone number",
                code="invalid_phone_number",
            ),
            UniqueValidator(
                queryset=User.objects.all(), message="Phone number already exists"
            ),
        ],
    )
    email = serializers.EmailField(
        required=True,
        max_length=255,
        validators=[
            UniqueValidator(queryset=User.objects.all(), message="Email already exists")
        ],
    )
    role = serializers.ChoiceField(choices=User.Role.choices, required=True)

    def validate(self, attrs):
        if attrs.get("password1") != attrs.get("password2"):
            raise serializers.ValidationError(
                {
                    "password2": "Passwords do not match",
                }
            )
        return attrs

    def save(self, **kwargs):
        user = super().save(**kwargs)
        user.email = self.validated_data.get("email")
        user.phone_number = self.validated_data.get("phone_number")
        user.role = self.validated_data.get("role")
        user.first_name = self.validated_data.get("first_name")
        user.last_name = self.validated_data.get("last_name")
        user.set_password(self.validated_data.get("password1"))
        user.save()
        return user


class EmailorPhoneNumberLoginRequestSerializer(LoginRequestSerializer):
    email = None
    identifier = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        ident = attrs.get("identifier", "").strip()
        password = attrs.get("password")

        if EMAIL_RE.match(ident):
            qs = User.objects.filter(email__iexact=ident)
        else:
            qs = User.objects.filter(phone_number=normalize_phone(ident))
        user = qs.first()
        if not user or not user.check_password(password):
            raise serializers.ValidationError({"message": "Invalid credentials."})

        self.context["user"] = user
        return attrs
