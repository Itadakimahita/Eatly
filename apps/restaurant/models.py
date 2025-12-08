# Python typing
from __future__ import annotations
from typing import Optional, ClassVar, List

# Django modules
from django.db import models
from django.utils import timezone
from django.db.models import QuerySet

from apps.abstract.models import AbstractBaseModel, AbstractSoftDeleteModel
from apps.user.models import CustomUser as User


class Restaurant(AbstractBaseModel, AbstractSoftDeleteModel):
    """Restaurant model."""

    name: str = models.CharField(max_length=255)
    description: Optional[str] = models.TextField(blank=True, null=True)
    image_url: Optional[str] = models.URLField(blank=True, null=True)
    address: Optional[str] = models.CharField(max_length=255, blank=True, null=True)
    address_link: Optional[str] = models.URLField(blank=True, null=True)
    owner: User = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='restaurants'
    )

    categories: models.ManyToManyField = models.ManyToManyField(
        'Category',
        through='RestaurantCategory',
        related_name='restaurants',
    )

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    """Food category model."""

    name: str = models.CharField(max_length=100, unique=True)
    description: Optional[str] = models.TextField(blank=True, null=True)
    icon_url: Optional[str] = models.URLField(blank=True, null=True)
    created_at: timezone.datetime = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.name


class RestaurantCategory(models.Model):
    """Intermediate model between Restaurant and Category."""

    restaurant: Restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    category: Category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at: timezone.datetime = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('restaurant', 'category')

    def __str__(self) -> str:
        return f"{self.restaurant.name} → {self.category.name}"


class DeliveryLink(models.Model):
    """Links to external delivery platforms."""

    restaurant: Restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='delivery_links',
    )
    platform_name: str = models.CharField(max_length=100)
    platform_url: str = models.URLField()

    def __str__(self) -> str:
        return f"{self.platform_name} ({self.restaurant.name})"
