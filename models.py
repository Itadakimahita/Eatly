from django.db import models
from django.utils import timezone



class User(models.Model):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('owner', 'Owner'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    hashed_password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} ({self.role})"



class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    address_link = models.URLField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restaurants')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    categories = models.ManyToManyField(
        'Category',
        through='RestaurantCategory',
        related_name='restaurants'
    )

    def __str__(self):
        return self.name



class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name



class RestaurantCategory(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('restaurant', 'category')

    def __str__(self):
        return f"{self.restaurant.name} → {self.category.name}"



class DeliveryLink(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='delivery_links')
    platform_name = models.CharField(max_length=100)
    platform_url = models.URLField()

    def __str__(self):
        return f"{self.platform_name} ({self.restaurant.name})"



class Post(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} ({self.restaurant.name})"



class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.name}: {self.content[:25]}..."



class UserLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    discount_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='liked_by')
    liked_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'discount_post')

    def __str__(self):
        return f"{self.user.name} ❤️ {self.discount_post.title}"



class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='subscribers')
    subscribed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'restaurant')

    def __str__(self):
        return f"{self.user.name} → {self.restaurant.name}"



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"To {self.user.name}: {self.title}"
