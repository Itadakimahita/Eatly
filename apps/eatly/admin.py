# Python typing
from typing import Any, Optional, Tuple, Dict, Type

# Django modules
from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from django.utils.html import format_html
from unfold.admin import ModelAdmin

# Project models
from .models import (
    User,
    Restaurant,
    Category,
    RestaurantCategory,
    DeliveryLink,
    Post,
    Comment,
    UserLike,
    UserSubscription,
    Notification,
)

import unfold


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

    list_display: Tuple[str, ...] = (
        "name",
        "email",
        "colored_role",
        "created_at",
        "updated_at",
    )

    search_fields: Tuple[str, ...] = ("name", "email")

    list_per_page: int = 20
    list_display_links: Tuple[str, ...] = ("name",)
    ordering: Tuple[str, ...] = ("-name",)
    list_filter: Tuple[str, ...] = ("name",)
    readonly_fields: Tuple[str, ...] = ("created_at",)
    save_on_top: bool = True

    fieldsets: Tuple[
        Tuple[str, Dict[str, Tuple[str, ...]]],
        ...
    ] = (
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

    list_display: Tuple[str, ...] = (
        "name",
        "description",
        "address",
        "owner",
        "created_at",
        "updated_at",
    )
    search_fields: Tuple[str, ...] = ("name", "address")


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    """Category admin configuration."""

    list_display: Tuple[str, ...] = ("name", "description", "created_at")
    search_fields: Tuple[str, ...] = ("name",)


@admin.register(RestaurantCategory)
class RestaurantCategoryAdmin(ModelAdmin):
    """RestaurantCategory admin configuration."""

    list_display: Tuple[str, ...] = ("restaurant", "category", "created_at")
    search_fields: Tuple[str, ...] = ("restaurant", "category")


@admin.register(DeliveryLink)
class DeliveryLinkAdmin(ModelAdmin):
    """DeliveryLink admin configuration."""

    list_display: Tuple[str, ...] = ("restaurant", "platform_name")
    search_fields: Tuple[str, ...] = ("restaurant", "platform_name")


@admin.register(Post)
class PostAdmin(ModelAdmin):
    """Post admin configuration."""

    list_display: Tuple[str, ...] = (
        "restaurant",
        "title",
        "description",
        "created_at",
        "updated_at",
    )
    search_fields: Tuple[str, ...] = ("restaurant", "title")


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    """Comment admin configuration."""

    list_display: Tuple[str, ...] = (
        "user",
        "post",
        "content",
        "created_at",
        "updated_at",
    )
    search_fields: Tuple[str, ...] = ("user", "post", "content")


@admin.register(UserLike)
class UserLikeAdmin(ModelAdmin):
    """UserLike admin configuration."""

    list_display: Tuple[str, ...] = ("user", "discount_post", "liked_at")
    search_fields: Tuple[str, ...] = ("user",)


@admin.register(UserSubscription)
class UserSubscriptionAdmin(ModelAdmin):
    """UserSubscription admin configuration."""

    list_display: Tuple[str, ...] = ("user", "restaurant", "subscribed_at")
    search_fields: Tuple[str, ...] = ("user", "restaurant")


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    """Notification admin configuration."""

    list_display: Tuple[str, ...] = (
        "user",
        "title",
        "message",
        "is_read",
        "created_at",
        "expires_at",
    )
    search_fields: Tuple[str, ...] = ("user", "title")


# --- Admin site info ---
admin.site.site_header = "Eatly Admin Panel"
admin.site.site_title = "Eatly Dashboard"
