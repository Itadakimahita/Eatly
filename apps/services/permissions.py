from rest_framework.permissions import BasePermission

from apps.services.models import Post,Comment
from apps.user.models import CustomUser

class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Assumes the model instance has an `user` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True

        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        if isinstance(obj, Post):
            restaurant = getattr(obj, 'restaurant', None)
            if restaurant and getattr(restaurant, 'owner_id', None) == user.id:
                return True
            if getattr(obj, 'user_id', None) == user.id:
                return True
        return False
    
class IsSubscriptionOwner(BasePermission):
    """
    Custom permission to only allow owners of a subscription to view or edit it.
    """
    message = "You must be the owner of this subscription to access it."

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.user_id == request.user.id
    

    