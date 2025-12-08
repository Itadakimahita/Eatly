# Python typing
from typing import Any, Optional, Tuple, Dict, Type

# Django modules
from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from django.utils.html import format_html
from unfold.admin import ModelAdmin
import unfold

# Project models
from apps.user.models import CustomUser as User
from apps.restaurant.models import Restaurant, Category, RestaurantCategory, DeliveryLink
from apps.services.models import Post, Comment, UserLike, UserSubscription, Notification


@admin.register(User)
class UserAdmin(ModelAdmin):
    """User admin configuration."""

    # --- Type-safe colored_role ---
    @admin.display(description="Role")
    def colored_role(self, obj: User) -> str:
        colors: Dict[str, str] = {
            "customer": "#ef4444",
            "owner": "#eab308",
        }
        color: str = colors.get(obj.role.lower(), "#9ca3af")
        return format_html(
            f'<span style="color:{color}; font-weight:bold;">'
            f'{obj.role.capitalize()}</span>'
        )

    list_display = (
        "name",
        "email",
        "colored_role",
        "created_at",
        "updated_at",
    )

    search_fields = ("name", "email")

    list_per_page: int = 20
    list_display_links = ("name",)
    ordering = ("-name",)
    list_filter = ("name",)
    readonly_fields = ("created_at",)
    save_on_top: bool = True

    fieldsets = (
        (
            "User Information",
            {
                "fields": (
                    "name",
                    "email",
                )
            },
        ),
        (
            "Date and Time Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    # Uncomment if permissions should be restricted
    """
    def has_add_permission(self, request: WSGIRequest) -> bool:
        return False

    def has_delete_permission(
        self, request: WSGIRequest, obj: Optional[User] = None
    ) -> bool:
        return False

    def has_change_permission(
        self, request: WSGIRequest, obj: Optional[User] = None
    ) -> bool:
        return False
    """


@admin.register(Restaurant)
class RestaurantAdmin(ModelAdmin):
    """Restaurant admin configuration."""

    list_display = (
        "name",
        "description",
        "address",
        "owner",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "address")


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    """Category admin configuration."""

    list_display = ("name", "description", "created_at")
    search_fields = ("name",)


@admin.register(RestaurantCategory)
class RestaurantCategoryAdmin(ModelAdmin):
    """RestaurantCategory admin configuration."""

    list_display = ("restaurant", "category", "created_at")
    search_fields = ("restaurant", "category")


@admin.register(DeliveryLink)
class DeliveryLinkAdmin(ModelAdmin):
    """DeliveryLink admin configuration."""

    list_display = ("restaurant", "platform_name")
    search_fields = ("restaurant", "platform_name")


@admin.register(Post)
class PostAdmin(ModelAdmin):
    """Post admin configuration."""

    list_display = (
        "restaurant",
        "title",
        "description",
        "created_at",
        "updated_at",
    )
    search_fields = ("restaurant", "title")


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    """Comment admin configuration."""

    list_display = (
        "user",
        "post",
        "content",
        "created_at",
        "updated_at",
    )
    search_fields = ("user", "post", "content")


@admin.register(UserLike)
class UserLikeAdmin(ModelAdmin):
    """UserLike admin configuration."""

    list_display = ("user", "discount_post", "liked_at")
    search_fields = ("user",)


@admin.register(UserSubscription)
class UserSubscriptionAdmin(ModelAdmin):
    """UserSubscription admin configuration."""

    list_display = ("user", "restaurant", "subscribed_at")
    search_fields = ("user", "restaurant")


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    """Notification admin configuration."""

    list_display = (
        "user",
        "title",
        "message",
        "is_read",
        "created_at",
        "expires_at",
    )
    search_fields = ("user", "title")


# --- Admin site info ---
admin.site.site_header = "Eatly Admin Panel"
admin.site.site_title = "Eatly Dashboard"
