# Python typing
from __future__ import annotations
from typing import Optional, ClassVar, List

# Django modules
from django.db import models
from django.utils import timezone
from django.db.models import QuerySet

from apps.eatly.abstract_model import AbstractBaseModel


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


class Restaurant(AbstractBaseModel):
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


class Post(AbstractBaseModel):
    """Restaurant posts for promotions or announcements."""

    restaurant: Restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name='posts'
    )
    title: str = models.CharField(max_length=255)
    description: Optional[str] = models.TextField(blank=True, null=True)
    image_url: Optional[str] = models.URLField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.title} ({self.restaurant.name})"


class Comment(AbstractBaseModel):
    """User comments on posts."""

    user: User = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments'
    )
    post: Post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments'
    )
    content: str = models.TextField()

    def __str__(self) -> str:
        return f"{self.user.name}: {self.content[:25]}..."


class UserLike(models.Model):
    """Likes made by users on discount posts."""

    user: User = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='likes'
    )
    discount_post: Post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='liked_by'
    )
    liked_at: timezone.datetime = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'discount_post')

    def __str__(self) -> str:
        return f"{self.user.name} ❤️ {self.discount_post.title}"


class UserSubscription(models.Model):
    """User subscriptions to restaurants."""

    user: User = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriptions'
    )
    restaurant: Restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name='subscribers'
    )
    subscribed_at: timezone.datetime = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'restaurant')

    def __str__(self) -> str:
        return f"{self.user.name} → {self.restaurant.name}"


class Notification(models.Model):
    """Notifications sent to users."""

    user: User = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications'
    )
    title: str = models.CharField(max_length=255)
    message: str = models.TextField()
    is_read: bool = models.BooleanField(default=False)
    created_at: timezone.datetime = models.DateTimeField(default=timezone.now)
    expires_at: Optional[timezone.datetime] = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        return f"To {self.user.name}: {self.title}"
