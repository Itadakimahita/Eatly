# Django REST Framework modules
from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    IntegerField,
    Field,
    URLField,
    ListField,
    Serializer,
    BooleanField,
)

# Project modules
from apps.restaurants.models import Restaurant


class CurrentPKURLDefault:
    """Default value for the primary key URL field in """

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
        """
        Meta class for RestaurantBaseSerializer.
        has the model and fields attributes.
        fields include all fields from the Restaurant model.
        """
        model = Restaurant
        fields = '__all__'

class RestaurantListSerializer(ModelSerializer):
    """
    Serializer for listing Restaurant instances.
    """

    class Meta:
        """
        Meta class for RestaurantListSerializer.
        has the model and fields attributes.
        fields include id, name, description, image_url, address, address_link, and owner.
        """
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
        """
        Meta class for RestaurantCreateSerializer.
        has the model and fields attributes.
        fields include name, description, address, and address_link.
        """
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
    
class RestaurantDeleteSerializer(ModelSerializer):
    """
    Serializer for deleting Restaurant instances.
    """

    class Meta:
        """
        Meta class for RestaurantDeleteSerializer.
        has the model and fields attributes.
        fields include id.
        """
        model = Restaurant
        fields = [
            'id',
        ]
        read_only_fields = ['id']

    def delete(self, validated_data):
        """Delete a Restaurant instance."""

        return super().delete(validated_data)  
      
class RestaurantGetByIdSerializer(ModelSerializer):
    """
    Serializer for getting Restaurant instances by ID.
    """
    id = IntegerField()

    class Meta:
        """
        Meta class for RestaurantGetByIdSerializer.
        has the model and fields attributes.
        fields include id.
        """
        model = Restaurant
        fields = [
            'id',
        ]
        read_only_fields = ['id']

class CategorySerializer(ModelSerializer):
    """
    Serializer for the Category model.
    """

    class Meta:
        """
        Meta class for CategorySerializer.
        has the model and fields attributes.
        fields include id, name, description, and icon_url.
        """
        model = Restaurant
        fields = [
            'id',
            'name',
            'description',
            'icon_url',
        ]
        read_only_fields = ['id']

class ImageURLSerializer(Serializer):
    """
    Serializer for handling image URL input, on restaurant image updates.
    """
    image_url = URLField()


class CategoryAssignSerializer(Serializer):
    """
    Serializer for assigning categories to a restaurant.
    """
    category_ids = ListField(
        child=IntegerField(),
        min_length=1,
    )


class DeliveryAssignSerializer(Serializer):
    """
    Serializer for assigning deliveries to a restaurant.
    """
    delivery_ids = ListField(
        child=IntegerField(),
        min_length=1,
    )

class OwnerQuerySerializer(Serializer):
    """
    Serializer for querying restaurants by owner ID.
    """
    owner_id = IntegerField(min_value=1)

class RestaurantListQuerySerializer(Serializer):
    """
    Serializer for querying restaurants with optional filters.
    """
    has_delivery = BooleanField(required=False)
    has_image = BooleanField(required=False)