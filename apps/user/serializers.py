# Python modules
from typing import Any, Optional

# Django modules
from django.contrib.auth import get_user_model

# Django REST Framework
from rest_framework.serializers import Serializer, CharField, EmailField, IntegerField, ListField
from rest_framework.exceptions import ValidationError

# Project modules
from apps.user.models import CustomUser as User

class UserLoginSerializer(Serializer):
    """Serializer for user login."""

    email = EmailField(required=True, max_length=User.EMAIL_MAX_LENGTH)
    password = CharField(required=True, write_only=True, min_length=8, max_length=User.PASSWORD_MAX_LENGTH)

    class Meta:
        """Meta class for UserLoginSerializer."""

        fields = (
            "email",
            "password",
        )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user: Optional[User] = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError("Invalid email or password.")

        if not user.check_password(password):
            raise ValidationError("Invalid email or password.")

        attrs['user'] = user

        return super().validate(attrs)

class UserRegisterSerializer(Serializer):
    """Serializer for user registration."""

    name = CharField(required=True, max_length=User.NAME_MAX_LENGTH)
    email = EmailField(required=True, max_length=User.EMAIL_MAX_LENGTH)
    password = CharField(required=True, write_only=True, min_length=8, max_length=User.PASSWORD_MAX_LENGTH)

    class Meta:
        """Meta class for UserRegisterSerializer."""
        model = User
        fields = (
            "name",
            "email",
            "password",
        )
        extra_kwargs = {
            "password": {"write_only": True},
        }
    
    def validate_email(self, value: str) -> str:
        """Validate that the email is not already in use."""
        if User.objects.filter(email=value).exists():
            raise ValidationError("A user with this email already exists.")
        return value

    def validate(self, attrs):
        return super().validate(attrs)
    
    def create(self, validated_data):
        """Create a new user with the validated data."""
        User = get_user_model()
        
        return User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
        )

class UserLoginResponseSerializer(Serializer):
    """
    Serializer for user response.
    """

    id = IntegerField()
    name = CharField()
    email = EmailField()
    access = CharField()
    refresh = CharField()

    class Meta:
        """Customization of the Serializer metadata."""

        fields = (
            "id",
            "name",
            "email",
            "access",
            "refresh",
        )

class UserSerializer(Serializer):
    """Serializer for User model."""

    id = IntegerField(read_only=True)
    name = CharField(max_length=User.NAME_MAX_LENGTH)
    email = EmailField(max_length=User.EMAIL_MAX_LENGTH)
    role = CharField()
    is_active = CharField()
    created_at = CharField()
    updated_at = CharField()

    class Meta:
        """Meta class for UserSerializer."""

        fields = (
            "id",
            "name",
            "email",
            "role",
            "is_active",
            "created_at",
            "updated_at",
        )

class UserListSerializer(Serializer):
    """Serializer for a list of users."""

    users = ListField(child=UserSerializer())

    class Meta:
        """Meta class for UserListSerializer."""

        fields = ("users",)