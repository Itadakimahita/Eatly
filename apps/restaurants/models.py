# Python typing
from __future__ import annotations
from typing import Optional, ClassVar, List

# Django modules
from django.db import models
from django.utils import timezone
from django.db.models import QuerySet

from apps.abstract.models import AbstractBaseModel, AbstractSoftDeleteModel
from apps.users.models import CustomUser as User


class Restaurant(AbstractBaseModel, AbstractSoftDeleteModel):
    """
    Restaurant model.
    Contains information about a restaurant.

    Constants:
        MAX_LENGTH (int): Maximum length for character fields.
    Attributes:
        name (str): The name of the restaurant.
        description (str): A brief description of the restaurant.
        image_url (str): URL to an image representing the restaurant.
        address (str): The physical address of the restaurant.
        address_link (str): A URL link to the restaurant's location on a map.
        owner (User): The owner of the restaurant, linked to the CustomUser model.
    """

    MAX_LENGTH = 255
    name = models.CharField(max_length=MAX_LENGTH)
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    address = models.CharField(max_length=MAX_LENGTH, blank=True, null=True)
    address_link = models.URLField(blank=True, null=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='restaurants'
    )

    categories = models.ManyToManyField(
        'Category',
        through='RestaurantCategory',
        related_name='restaurants',
    )

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    """
    Food category model.
    Contains information about a food category.

    Attributes:
        name (str): The name of the category.
        description (str): A brief description of the category.
        icon_url (str): URL to an icon representing the category.
    """

    NAME_MAX_LENGTH = 100
    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    description = models.TextField(blank=True, null=True)
    icon_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self) -> str:
        return self.name


class RestaurantCategory(models.Model):
    """
    Intermediate model between Restaurant and Category.
    Links restaurants to their categories.

    Attributes:
        restaurant (Restaurant): The restaurant instance.
        category (Category): The category instance.
        created_at (datetime): The timestamp when the relationship was created.
    """

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('restaurant', 'category')

    def __str__(self) -> str:
        return f"{self.restaurant.name} → {self.category.name}"


class DeliveryLink(models.Model):
    """
    Links to external delivery platforms.
    
    Attributes:
        restaurant (Restaurant): The restaurant associated with the delivery link.
        platform_name (str): The name of the delivery platform.
        platform_url (str): The URL to the restaurant's page on the delivery platform.
    """

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='delivery_links',
    )
    platform_name = models.CharField(max_length=100)
    platform_url = models.URLField()

    def __str__(self) -> str:
        return f"{self.platform_name} ({self.restaurant.name})"
