# Python modules
from typing import Any

# Django REST Framework modules
from rest_framework.permissions import BasePermission
from rest_framework.request import Request as DRFRequest
from rest_framework.viewsets import ViewSet

# Project modules
from apps.restaurant.models import Restaurant
from apps.user.models import CustomUser
from apps.user.entities.role_entity import UserRoleEntity

class IsRestaurantOwner(BasePermission):
    """
    Custom permission to only allow owners of a restaurant to access it.
    """

    message = "Forbidden! You are not the owner of this restaurant."

    def has_object_permission(
        self, request: DRFRequest, view: ViewSet, obj: Restaurant | int
    ) -> bool:
        
        # If DRF passed the actual Restaurant instance:
        if isinstance(obj, Restaurant):
            return obj.owner_id == request.user.id

        # If obj is actually a restaurant id (int):
        if isinstance(obj, int):
            restaurant = Restaurant.objects.filter(id=obj).first()
            if not restaurant:
                return False
            return restaurant.owner_id == request.user.id

        return False
