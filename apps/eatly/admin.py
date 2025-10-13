# Django modules
#from django.contrib.admin import ModelAdmin, register
from typing import Optional
import unfold
from .models import *

from django.contrib import admin
from unfold.admin import ModelAdmin
from django.core.handlers.wsgi import WSGIRequest
from django.utils.html import format_html



@admin.register(User)
class User(ModelAdmin):
    """
    user conf
    """
    @admin.display(description="Role")
    def colored_role(self, obj):
        colors = {
            "customer": "#ef4444",
            "owner": "#eab308",
        }
        color= colors.get(obj.role.lower(), "#9ca3af")
        return format_html(f'<span style="color:{color}; font-weight:bold;">{obj.role.capitalize()}</span>')
    
    list_display = (
        "name",
        "email",
        "colored_role",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "name",
        "email",
    )

    list_per_page = 20

    list_display_links = (
        "name",
    )
    ordering = (
        "-name",
    )
    list_filter = (
        "name",
    )
    readonly_fields = (
        "created_at",
    )
    save_on_top = True

    fieldsets = (
        (
            "User Information",
            {
                "fields": (
                    "name",
                    "email",
                )
            }
        ),
        (
            "Date and Time Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            }
        )
    )
    '''
    def has_add_permission(self, request: WSGIRequest) -> bool:
        return False

    def has_delete_permission(self, request: WSGIRequest, obj: Optional[User] = None) -> bool:
        return False

    def has_change_permission(self, request: WSGIRequest, obj: Optional[User] = None) -> bool:
        return False
    '''

@admin.register(Restaurant)
class Restaurant(ModelAdmin):
    """
    Restaurant conf
    """
    list_display = (
        "name",
        "description",
        "address",
        "owner",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "name",
        "address",
    )
    
   
@admin.register(Category)
class Category(ModelAdmin):
    list_display = (
        "name",
        "description",
        "created_at",
    )

    search_fields = (
        "name",
    )

@admin.register(RestaurantCategory)
class RestaurantCategory(ModelAdmin):
    list_display = (
        "restaurant",
        "category",
        "created_at",
    )

    search_fields = (
        "restaurant",
        "category",
    )
    
@admin.register(DeliveryLink)
class DeliveryLink(ModelAdmin):
    list_display = (
        "restaurant",
        "platform_name",
    )

    search_fields = (
        "restaurant",
        "platform_name",
    )

@admin.register(Post)
class Post(ModelAdmin):
    list_display = (
        "restaurant",
        "title",
        "description",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "restaurant",
        "title",
    )

@admin.register(Comment)
class Comment(ModelAdmin):
    list_display = (
        "user",
        "post",
        "content",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "user",
        "post",
        "content",
    )

@admin.register(UserLike)
class UserLike(ModelAdmin):
    list_display = (
        "user",
        "discount_post",
        "liked_at",
    )

    search_fields = (
        "user",
    )

@admin.register(UserSubscription)
class UserSubscription(ModelAdmin):
    list_display = (
        "user",
        "restaurant",
        "subscribed_at"
    )

    search_fields = (
        "user",
        "restaurant",
    )
    

@admin.register(Notification)
class Notification(ModelAdmin):
    list_display = (
        "user",
        "title",
        "message",
        "is_read",
        "created_at",
        "expires_at",
    )

    search_fields = (
        "user",
        "title",
    )


admin.site.site_header="Eatly Admin Panel"
admin.site.site_title="Eatly Dashboard"



"""
used in admin panel:
search
list display
list_per_page
list_display_links
ordering
list_filter
readonly_fields
save_on_top
fieldsets
has_change_permission
has_add_permission
has_delete_permission
def colored_role
titles
colors
"""
#admin.site.register(Restaurant)
#admin.site.register(Category)
#admin.site.register(RestaurantCategory)
#admin.site.register(DeliveryLink)
#admin.site.register(Post)
#admin.site.register(Comment)
#admin.site.register(UserLike)
#admin.site.register(UserSubscription)
#admin.site.register(Notification)


