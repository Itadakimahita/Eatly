# Python typing
from __future__ import annotations
from typing import Any, Optional, ClassVar, List

# Django modules
from django.db.models import (
    EmailField,
    CharField,
    BooleanField,
)
from django.db import models
from django.utils import timezone
from django.db.models import QuerySet
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from pydantic import ValidationError

from apps.abstract.models import AbstractBaseModel
from apps.user.validators import (
    validate_email_domain,
    validate_password,
)

class CustomUserManager(BaseUserManager):
    """Custom User Manager to make database requests."""

    def __obtain_user_instance(
        self,
        email: str,
        name: str,
        password: str,
        **kwargs: dict[str, Any],
    ) -> 'User':
        """Get user instance."""
        if not email:
            raise ValidationError(
                message="Email field is required", code="email_empty"
            )
        if not name:
            raise ValidationError(
                message="Full name name is required.", code="name_empty"
            )

        new_user: 'User' = self.model(
            email=self.normalize_email(email),
            name=name,
            password=password,
            **kwargs,
        )
        return new_user

    def create_user(
        self,
        email: str,
        name: str,
        password: str,
        **kwargs: dict[str, Any],
    ) -> 'User':
        """Create Custom user. TODO where is this used?"""
        new_user: 'User' = self.__obtain_user_instance(
            email=email,
            name=name,
            password=password,
            **kwargs,
        )
        new_user.set_password(password)
        new_user.save(using=self._db)
        return new_user

    def create_superuser(
        self,
        email: str,
        name: str,
        password: str,
        **kwargs: dict[str, Any],
    ) -> 'User':
        """Create super user. Used by manage.py createsuperuser."""
        new_user: 'User' = self.__obtain_user_instance(
            email=email,
            name=name,
            password=password,
            is_admin=True,
            is_superuser=True,
            **kwargs,
        )
        new_user.set_password(password)
        new_user.save(using=self._db)
        return new_user


class User(AbstractBaseModel, AbstractBaseUser, PermissionsMixin):
    """User model representing customers and restaurant owners."""

    ROLE_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ('customer', 'Customer'),
        ('owner', 'Owner'),
    ]
    EMAIL_MAX_LENGTH = 150
    NAME_MAX_LENGTH = 150
    PASSWORD_MAX_LENGTH = 254

    email = EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        db_index=True,
        validators=[validate_email_domain],
        verbose_name="Email address",
        help_text="User's email address",
    )
    name = CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name="User name",
    )
    password = CharField(
        max_length=PASSWORD_MAX_LENGTH,
        validators=[validate_password],
        verbose_name="Password",
        help_text="User's hash representation of the password",
    )
    role: str = CharField(
        max_length=20, 
        choices=ROLE_CHOICES
    )
    
    # True iff the user is part of the corporoom team, allowing them to access the admin panel
    is_admin = BooleanField(
        default=False,
        verbose_name="Admin status",
        help_text="True if the user is an admin and has an access to the admin panel",
    )
    # True iff the user can make requests to the backend (include in company)
    is_active = BooleanField(
        default=True,
        verbose_name="Active status",
        help_text="True if the user is active and has an access to request data",
    )

    REQUIRED_FIELDS = ["password", "name", "role"]
    USERNAME_FIELD = "email"
    objects = CustomUserManager()

    class Meta:
        """Meta options for CustomUser model."""

        verbose_name = "Custom User"
        verbose_name_plural = "Custom Users"
        ordering = ["-created_at"]

    def clean(self) -> None:
        """Validate the model instance before saving."""
        return super().clean()

    def __str__(self) -> str:
        return f"{self.name} ({self.role})"
