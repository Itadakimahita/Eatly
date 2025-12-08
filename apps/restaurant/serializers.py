# Django REST Framework modules
from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    IntegerField,
    Field
)

# Project modules
from apps.restaurant.models import Restaurant


class CurrentPKURLDefault:
    """Default value for the primary key URL field in serializers."""

    requires_context = True

    def __call__(self, serializer_field: Field) -> int:
        """Get the current primary key from the request."""
        assert "pk" in serializer_field.context, (
            "CurrentPKURLDefault requires 'pk' in the serializer context."
        )
        return int(serializer_field.context["pk"])

    def __repr__(self) -> str:
        """Return a string representation of the default."""
        return "%s()" % self.__class__.__name__

class RestaurantBaseSerializer(ModelSerializer):
    """
    Base serializer for the Restaurant model.
    """

    class Meta:
        model = Restaurant
        fields = '__all__'

class RestaurantListSerializer(ModelSerializer):
    """
    Serializer for listing Restaurant instances.
    """

    class Meta:
        model = Restaurant
        fields = [
            'id',
            'name',
            'description',
            'image_url',
            'address',
            'address_link',
            'owner',
        ]
        read_only_fields = ['id', 'owner']
    
class RestaurantCreateSerializer(ModelSerializer):
    """
    Serializer for creating Restaurant instances.
    """

    class Meta:
        model = Restaurant
        fields = [
            'name',
            'description',
            'address',
            'address_link',
        ]

    def create(self, validated_data):
        """Create a Restaurant instance with the owner set from context."""
        
        return super().create(validated_data)

class CategorySerializer(ModelSerializer):
    """
    Serializer for the Category model.
    """

    class Meta:
        model = Restaurant
        fields = [
            'id',
            'name',
            'description',
            'icon_url',
        ]
        read_only_fields = ['id']