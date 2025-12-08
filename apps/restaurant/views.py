# Python modules
from typing import Any

# Django modules
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.db.models import QuerySet, Count

# Django REST Framework
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from rest_framework.decorators import action

# Restaurant modules
from apps.restaurant.models import DeliveryLink, Restaurant
from apps.user.entities.role_entity import UserRoleEntity
from apps.user.models import CustomUser
from apps.restaurant.permissions import IsRestaurantOwner
from apps.restaurant.serializers import (
    RestaurantBaseSerializer,
    RestaurantListSerializer,
    RestaurantCreateSerializer,
)


class RestaurantViewSet(ViewSet):
    """
    ViewSet for handling Restaurant-related endpoints.
    """

    queryset: QuerySet[Restaurant] = Restaurant.objects.all()
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, IsRestaurantOwner,)
    serializer_class = RestaurantBaseSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list':
            permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated, AllowAny]  # Allow any authenticated user to create a restaurant
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsRestaurantOwner] # Assuming IsOwnerOrAdmin is a custom permission
        else:
            permission_classes = [AllowAny] # Default for other actions or custom actions
            
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a 'username' query parameter in the URL.
        """
        user = self.request.user
        if user.is_authenticated:
            return Restaurant.objects.filter(owner=user)
        return Restaurant.objects.none() # Or handle unauthenticated access as needed

    def perform_create(self, serializer):
        """
        Assigns the current user as the owner of the new object.
        """
        serializer.save(owner=self.request.user)

    @action(
        methods=['get'],
        detail=False,
        url_name='list',
        url_path='list',
        permission_classes=[IsAuthenticated, AllowAny],
    )
    def all_restaurants(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any]
    ) -> DRFResponse:
        """
        Handle GET requests to list Restaurants.

        Parameters:
            request: DRFRequest
                The request object.
            *args: list
                Additional positional arguments.
                Additional positional arguments.
            **kwargs: dict
                Additional keyword arguments.
        
        Returns:
            DRFResponse
                A response containing list of Restaurants.
        """

        restaurants: QuerySet[Restaurant] = Restaurant.objects.all()
        serializer: RestaurantListSerializer = RestaurantListSerializer(
            restaurants, many=True
        )
        return DRFResponse(serializer.data, status=HTTP_200_OK)
    
    @action(
        methods=['get'],
        detail=False,
        url_name='list',
        url_path='list',
        permission_classes=[IsAuthenticated, AllowAny],
    )
    def owner_restaurants(
        self, 
        request: DRFRequest, 
        pk: int = None,
        *args: tuple[Any, ...], 
        **kwargs: dict[str, Any]
        ) -> DRFResponse:
        """
        Handle GET requests to list Restaurants of a specific owner.

        Parameters:
            request: DRFRequest
                The request object.
            *args: list
                Additional positional arguments.
                Additional positional arguments.
            **kwargs: dict
                Additional keyword arguments.
        
        Returns:
            DRFResponse
                A response containing list of Restaurants.
        """
        owner = CustomUser.objects.get(pk=pk)
        if owner is None:
            return DRFResponse(detail="Owner not found.", status=HTTP_404_NOT_FOUND)
        restaurants: QuerySet[Restaurant] = Restaurant.objects.filter(owner=owner)
        serializer: RestaurantListSerializer = RestaurantListSerializer(
            restaurants, many=True
        )
        return DRFResponse(serializer.data, status=HTTP_200_OK)
        
    
    @action(
        methods=['post'],
        detail=False,
        url_path='add',
        url_name='add',
        permission_classes=[IsAuthenticated, AllowAny],
    )
    def add(self, request, *args, **kwargs):
        serializer = RestaurantCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        if user.role != UserRoleEntity.OWNER:
            user.role = UserRoleEntity.OWNER
            user.save(update_fields=["role"])

        restaurant = serializer.save(owner=user)

        return DRFResponse(RestaurantBaseSerializer(restaurant).data, status=HTTP_201_CREATED)
    
    def retrieve(self, request: DRFRequest, pk: int=None, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> DRFResponse:
        """
        Handle GET requests to list Restaurants of a specific owner.

        Parameters:
            request: DRFRequest
                The request object.
            pk: int
                The id of Restaurant
            *args: list
                Additional positional arguments.
                Additional positional arguments.
            **kwargs: dict
                Additional keyword arguments.
        
        Returns:
            DRFResponse
                A response containing list of Restaurants.
        """
        try:
            restaurant = Restaurant.objects.get(pk=pk)
        except Restaurant.DoesNotExist:
            return DRFResponse(
                {"detail": "Restaurant not found."},
                status=HTTP_404_NOT_FOUND,
            )

        serializer = RestaurantBaseSerializer(restaurant)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            restaurant = Restaurant.objects.get(pk=pk)
        except Restaurant.DoesNotExist:
            return DRFResponse(
                {"detail": "Restaurant not found."},
                status=HTTP_404_NOT_FOUND,
            )

        restaurant.delete()
        return DRFResponse(status=HTTP_204_NO_CONTENT)
    
    def partial_update(self, request, pk=None, *args, **kwargs):
        try:
            restaurant = Restaurant.objects.get(pk=pk)
        except Restaurant.DoesNotExist:
            return DRFResponse(
                {"detail": "Restaurant not found."},
                status=HTTP_404_NOT_FOUND,
            )

        serializer = RestaurantBaseSerializer(
            restaurant, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return DRFResponse(RestaurantBaseSerializer(restaurant).data, status=HTTP_200_OK)
    
    @action(
        methods=['get'],
        detail=False,
        url_path='set-image',
        url_name='set-image',
        permission_classes=[IsAuthenticated, IsRestaurantOwner],
    )
    def set_image(
        self,
        request: DRFRequest,
        *args: Any,
        **kwargs: Any
    ) -> DRFResponse:
        """
        Set the image URL for the restaurant owned by the authenticated user.

        Parameters:
            request: DRFRequest
                The request object containing 'image_url' in data.
            *args: list
                Additional positional arguments.
            **kwargs: dict
                Additional keyword arguments.

        Returns:
            DRFResponse
                A response indicating success or failure.
        """

        user: CustomUser = request.user
        image_url: str = request.data.get('image_url', '')

        if not image_url:
            return DRFResponse(
                {"detail": "Image URL is required."},
                status=HTTP_400_BAD_REQUEST,
            )

        try:
            restaurant: Restaurant = Restaurant.objects.get(owner=user)
        except Restaurant.DoesNotExist:
            return DRFResponse(
                {"detail": "Restaurant not found for the user."},
                status=HTTP_404_NOT_FOUND,
            )

        restaurant.image_url = image_url
        restaurant.save(update_fields=['image_url'])

        return DRFResponse(
            {"detail": "Image URL updated successfully."},
            status=HTTP_200_OK,
        )

    @action(
        methods=['get'],
        detail=False,
        url_path='assign-categories',
        url_name='assign-categories',
        permission_classes=[IsAuthenticated, IsRestaurantOwner],
    )
    def assign_categories(
        self,
        request: DRFRequest,
        *args: Any,
        **kwargs: Any
    ) -> DRFResponse:
        """
        Assign categories to the restaurant owned by the authenticated user.

        Parameters:
            request: DRFRequest
                The request object containing 'category_ids' in data.
            *args: list
                Additional positional arguments.
            **kwargs: dict
                Additional keyword arguments.

        Returns:
            DRFResponse
                A response indicating success or failure.
        """

        user: CustomUser = request.user
        category_ids: list[int] = request.data.get('category_ids', [])

        if not category_ids:
            return DRFResponse(
                {"detail": "Category IDs are required."},
                status=HTTP_400_BAD_REQUEST,
            )

        try:
            restaurant: Restaurant = Restaurant.objects.get(owner=user)
        except Restaurant.DoesNotExist:
            return DRFResponse(
                {"detail": "Restaurant not found for the user."},
                status=HTTP_404_NOT_FOUND,
            )

        restaurant.categories.set(category_ids)
        restaurant.save()

        return DRFResponse(
            {"detail": "Categories assigned successfully."},
            status=HTTP_200_OK,
        )
    
    @action(
        methods=['post'],
        detail=False,
        url_path='unassign-categories',
        url_name='unassign-categories',
        permission_classes=[IsAuthenticated, IsRestaurantOwner],
    )
    def unassign_categories(
        self,
        request: DRFRequest,
        *args: Any,
        **kwargs: Any
    ) -> DRFResponse:
        """
        Unassign categories from the restaurant owned by the authenticated user.

        Parameters:
            request: DRFRequest
                The request object containing 'category_ids' in data.
            *args: list
                Additional positional arguments.
            **kwargs: dict
                Additional keyword arguments.

        Returns:
            DRFResponse
                A response indicating success or failure.
        """

        user: CustomUser = request.user
        category_ids: list[int] = request.data.get('category_ids', [])

        if not category_ids:
            return DRFResponse(
                {"detail": "Category IDs are required."},
                status=HTTP_400_BAD_REQUEST,
            )

        try:
            restaurant: Restaurant = Restaurant.objects.get(owner=user)
        except Restaurant.DoesNotExist:
            return DRFResponse(
                {"detail": "Restaurant not found for the user."},
                status=HTTP_404_NOT_FOUND,
            )

        restaurant.categories.remove(*category_ids)
        restaurant.save(update_fields=['categories'])

        return DRFResponse(
            {"detail": "Categories unassigned successfully."},
            status=HTTP_200_OK,
        )
    
    @action(
        methods=['post'],
        url_name='add-delivery',
        url_path='add-delivery',
        permission_classes=[IsAuthenticated, IsRestaurantOwner],
    )
    def add_delivery_method(
        self,
        request: DRFRequest,
        pk: int = None,
        *args: Any,
        **kwargs: Any
    ) -> DRFResponse:
        """
        Add a delivery method to the restaurant owned by the authenticated user.

        Parameters:
            request: DRFRequest
                The request object containing 'delivery_ids' in data.
            pk: int
                The id of the restaurant.
            *args: list
                Additional positional arguments.
            **kwargs: dict
                Additional keyword arguments.

        Returns:
            DRFResponse
                A response indicating success or failure.
        """
        restaurant = self.get_object()
    
        user: CustomUser = request.user
        delivery_ids: list[int] = request.data.get('delivery_ids', [])

        if not delivery_ids:
            return DRFResponse(
                {"detail": "Delivery IDs are required."},
                status=HTTP_400_BAD_REQUEST,
            )

        try:
            restaurant: Restaurant = Restaurant.objects.get(owner=user)
        except Restaurant.DoesNotExist:
            return DRFResponse(
                {"detail": "Restaurant not found for the user."},
                status=HTTP_404_NOT_FOUND,
            )

        restaurant.delivery_methods.set(delivery_ids)
        restaurant.save()

        return DRFResponse(
            {"detail": "Delivery methods assigned successfully."},
            status=HTTP_200_OK,
        )
    
    @action(
        methods=['post'],
        url_name='remove-delivery',
        url_path='remove-delivery',
        permission_classes=[IsAuthenticated, IsRestaurantOwner],
    )
    def remove_delivery_methods(
        self,
        request: DRFRequest,
        *args: Any,
        **kwargs: Any
    ) -> DRFResponse:
        """
        Unassign delivery methods from the restaurant owned by the authenticated user.

        Parameters:
            request: DRFRequest
                The request object containing 'delivery_ids' in data.
            *args: list
                Additional positional arguments.
            **kwargs: dict
                Additional keyword arguments.

        Returns:
            DRFResponse
                A response indicating success or failure.
        """

        user: CustomUser = request.user
        delivery_ids: list[int] = request.data.get('delivery_ids', [])

        if not delivery_ids:
            return DRFResponse(
                {"detail": "Delivery IDs are required."},
                status=HTTP_400_BAD_REQUEST,
            )

        try:
            restaurant: Restaurant = Restaurant.objects.get(owner=user)
        except Restaurant.DoesNotExist:
            return DRFResponse(
                {"detail": "Restaurant not found for the user."},
                status=HTTP_404_NOT_FOUND,
            )

        restaurant.delivery_methods.remove(*delivery_ids)
        restaurant.save(update_fields=['delivery_methods'])

        return DRFResponse(
            {"detail": "Delivery methods unassigned successfully."},
            status=HTTP_200_OK,
        )

