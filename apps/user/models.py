# Python typing
from __future__ import annotations
from typing import Optional, ClassVar, List

# Django modules
from django.db import models
from django.utils import timezone
from django.db.models import QuerySet

from apps.abstract.models import AbstractBaseModel


class User(AbstractBaseModel):
    """User model representing customers and restaurant owners."""

    ROLE_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ('customer', 'Customer'),
        ('owner', 'Owner'),
    ]

    name: str = models.CharField(max_length=255)
    email: str = models.EmailField(unique=True)
    hashed_password: str = models.CharField(max_length=255)
    role: str = models.CharField(max_length=20, choices=ROLE_CHOICES)
    created_at: timezone.datetime = models.DateTimeField(default=timezone.now)
    updated_at: timezone.datetime = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"{self.name} ({self.role})"
