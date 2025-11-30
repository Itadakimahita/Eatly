# Python modules
from typing import Any

# from datetime import datetime, timezone

# Django modules
from django.db.models import Model, DateTimeField
from django.utils import timezone


class AbstractBaseModel(Model):
    """
    Abstract base model with common fields.
    """

    created_at = DateTimeField(
        default=timezone.now
    )
    updated_at = DateTimeField(
        default=timezone.now
    )

    class Meta:
        """Meta class for AbstractBaseModel."""

        abstract = True
