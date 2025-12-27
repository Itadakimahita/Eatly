# Python modules
from typing import Any

# Django modules
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.db.models import QuerySet, Count

# Django REST Framework
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.abstract.serializers import ErrorDetailSerializer, MessageSerializer, ValidationErrorSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_401_UNAUTHORIZED,
)
from rest_framework.decorators import action
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    swagger_auto_schema,
)


# Restaurant modules
from apps.restaurants.models import DeliveryLink, Restaurant
from apps.users.entities.role_entity import UserRoleEntity
from apps.users.models import CustomUser
from apps.restaurants.permissions import IsRestaurantOwner
from apps.restaurants.serializers import (
    CategoryAssignSerializer,
    DeliveryAssignSerializer,
    ImageURLSerializer,
    OwnerQuerySerializer,
    RestaurantBaseSerializer,
    RestaurantDeleteSerializer,
    RestaurantGetByIdSerializer,
    RestaurantListQuerySerializer,
    RestaurantListSerializer,
    RestaurantCreateSerializer,
)


class RestaurantViewSet(ViewSet):
    """
    ViewSet for handling Restaurant-related endpoints.
    """

    queryset: QuerySet[Restaurant] = Restaurant.objects.all()
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

    @extend_schema(
        tags=["Restaurants"],
        summary="List all restaurants",
        parameters=[
            OpenApiParameter("has_delivery", bool, OpenApiParameter.QUERY),
            OpenApiParameter("has_image", bool, OpenApiParameter.QUERY),
        ],
        responses={
            HTTP_200_OK: RestaurantListSerializer(many=True),
            HTTP_400_BAD_REQUEST: ValidationErrorSerializer,
            HTTP_401_UNAUTHORIZED: ErrorDetailSerializer,
        },
    )
    @action(
        methods=["get"],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def all_restaurants(self, request: DRFRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> DRFResponse:
        """
        Handle GET requests to list all Restaurants.

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
        query_serializer = RestaurantListQuerySerializer(data=request.query_params)
        if not query_serializer.is_valid():
            return DRFResponse(
                {"detail": query_serializer.errors},
                HTTP_400_BAD_REQUEST,
            )

        qs = Restaurant.objects.all()
        data = query_serializer.validated_data

        if data.get("has_delivery"):
            qs = qs.filter(delivery_methods__isnull=False)

        if data.get("has_image"):
            qs = qs.exclude(image_url="")

        return DRFResponse(
            RestaurantListSerializer(qs, many=True).data,
            HTTP_200_OK,
        )

    @extend_schema(
        tags=["Restaurants"],
        summary="List restaurants by owner",
        parameters=[
            OpenApiParameter("owner_id", int, OpenApiParameter.QUERY), # Первый вариант для параметров
        ],
        responses={
            HTTP_200_OK: RestaurantListSerializer(many=True),
            HTTP_400_BAD_REQUEST: ValidationErrorSerializer,
            HTTP_404_NOT_FOUND: ErrorDetailSerializer,
        },
    )
    @action(methods=["get"], detail=False)
    def owner_restaurants(self, request: DRFRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> DRFResponse:
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
        serializer = OwnerQuerySerializer(data=request.query_params)

        if not serializer.is_valid():
            return DRFResponse(
                {"errors": serializer.errors},
                HTTP_400_BAD_REQUEST,
            )

        owner_id: int = serializer.validated_data["owner_id"]
        owner: CustomUser = CustomUser.objects.filter(pk=owner_id).first()

        if not owner:
            return DRFResponse(
                {"detail": "Owner not found."},
                HTTP_404_NOT_FOUND,
            )

        restaurants: QuerySet[Restaurant] = Restaurant.objects.filter(owner=owner)
        return DRFResponse(
            RestaurantListSerializer(restaurants, many=True).data,
            HTTP_200_OK,
        )

        
    @extend_schema(
        tags=["Restaurants"],
        summary="Create restaurant",
        request=RestaurantCreateSerializer, # Второй вариант - Serializer для входящих параметров
        responses={
            HTTP_201_CREATED: RestaurantBaseSerializer,
            HTTP_400_BAD_REQUEST: ValidationErrorSerializer,
            HTTP_401_UNAUTHORIZED: ErrorDetailSerializer,
        },
    )
    @action(
        methods=["post"], 
        detail=False, 
        permission_classes=[IsAuthenticated]
    )
    def add(self, request: DRFRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> DRFResponse:
        """
        Handle POST requests to create a new Restaurant.

        Parameters:
            request: DRFRequest
                The request object.
            *args: list
                Additional positional arguments.
            **kwargs: dict
                Additional keyword arguments.
        
        Returns:
            DRFResponse
                A response containing the created Restaurant.
        """
        serializer = RestaurantCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return DRFResponse(
                {"detail": serializer.errors},
                HTTP_400_BAD_REQUEST,
            )

        user: CustomUser = request.user
        if user.role != UserRoleEntity.OWNER:
            user.role = UserRoleEntity.OWNER
            user.save(update_fields=["role"])

        restaurant: QuerySet[Restaurant] = serializer.save(owner=user)
        return DRFResponse(
            RestaurantBaseSerializer(restaurant).data,
            HTTP_201_CREATED,
        )

    
    @extend_schema(
        tags=["Restaurants"],
        summary="Get restaurant by ID",
        request=RestaurantGetByIdSerializer,
        responses={
            HTTP_200_OK: RestaurantBaseSerializer,
            HTTP_400_BAD_REQUEST: ValidationErrorSerializer,
            HTTP_401_UNAUTHORIZED: ErrorDetailSerializer,
            HTTP_404_NOT_FOUND: ErrorDetailSerializer,
        },
    )
    def retrieve(self, request: DRFRequest, pk: int, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> DRFResponse:
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
        id = RestaurantGetByIdSerializer(data={'id': pk})
        if not id.is_valid():
            return DRFResponse(
                {"detail": id.errors},
                status=HTTP_400_BAD_REQUEST,
            )
        try:
            restaurant: QuerySet[Restaurant] = Restaurant.objects.get(pk=pk)
        except Restaurant.DoesNotExist:
            return DRFResponse(
                {"detail": "Restaurant not found."},
                status=HTTP_404_NOT_FOUND,
            )

        serializer = RestaurantBaseSerializer(restaurant)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(
        tags=["Restaurants"],
        summary="Delete restaurant by ID",
        request=RestaurantDeleteSerializer,
        responses={
            HTTP_204_NO_CONTENT: "Restaurant deleted",
            HTTP_404_NOT_FOUND: ErrorDetailSerializer,
            HTTP_401_UNAUTHORIZED: ErrorDetailSerializer,
            HTTP_400_BAD_REQUEST: ValidationErrorSerializer,
        },
    )
    def destroy(self, request: DRFRequest, pk: int, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> DRFResponse:
        """
        Handle DELETE requests to delete a Restaurant.

        Parameters:
            request: DRFRequest
                The request object.
            pk: int
                The id of Restaurant
            *args: list
                Additional positional arguments.
            **kwargs: dict
                Additional keyword arguments.
        
        Returns:
            DRFResponse
                A no content response on successful deletion.
        """
        id: RestaurantDeleteSerializer = RestaurantDeleteSerializer(data={'id': pk})
        if not id.is_valid():
            return DRFResponse(
                {"detail": id.errors},
                status=HTTP_400_BAD_REQUEST,
            )
        try:
            restaurant: QuerySet[Restaurant] = Restaurant.objects.get(pk=pk)
        except Restaurant.DoesNotExist:
            return DRFResponse(
                {"detail": "Restaurant not found."},
                status=HTTP_404_NOT_FOUND,
            )

        restaurant.delete()
        return DRFResponse(status=HTTP_204_NO_CONTENT)

    @extend_schema(
        tags=["Restaurants"],
        summary="Update restaurant by ID",
        request=RestaurantBaseSerializer,
        responses={
            HTTP_201_CREATED: RestaurantBaseSerializer,
            HTTP_400_BAD_REQUEST: ValidationErrorSerializer,
            HTTP_401_UNAUTHORIZED: ErrorDetailSerializer,
            HTTP_404_NOT_FOUND: ErrorDetailSerializer,
        },
    )   
    def partial_update(self, request: DRFRequest, pk: int, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> DRFResponse:
        """
        Handle PATCH requests to update a Restaurant.

        Parameters:
            request: DRFRequest
                The request object.
            pk: int
                The id of Restaurant
            *args: list
                Additional positional arguments.
            **kwargs: dict
                Additional keyword arguments.
        
        Returns:
            DRFResponse
                A response containing the updated Restaurant.
        """
        id: RestaurantGetByIdSerializer = RestaurantGetByIdSerializer(data={'id': pk})
        if not id.is_valid():
            return DRFResponse(
                {"detail": id.errors},
                status=HTTP_400_BAD_REQUEST,
            )
        try:
            restaurant: QuerySet[Restaurant] = Restaurant.objects.get(pk=pk)
        except Restaurant.DoesNotExist:
            return DRFResponse(
                {"detail": "Restaurant not found."},
                status=HTTP_404_NOT_FOUND,
            )

        serializer = RestaurantBaseSerializer(
            restaurant, data=request.data, partial=True
        )
        if not serializer.is_valid():
            return DRFResponse(
                {"detail": serializer.errors},
                status=HTTP_400_BAD_REQUEST,
            )
        serializer.save()

        return DRFResponse(RestaurantBaseSerializer(restaurant).data, status=HTTP_200_OK)
    
    @extend_schema(
        tags=["Restaurants"],
        summary="Set restaurant image",
        request=ImageURLSerializer,
        responses={
            HTTP_200_OK: MessageSerializer,
            HTTP_400_BAD_REQUEST: ValidationErrorSerializer,
            HTTP_401_UNAUTHORIZED: ErrorDetailSerializer,
            HTTP_404_NOT_FOUND: ErrorDetailSerializer,
        },
    )
    @action(
        methods=["post"], 
        detail=False, 
        permission_classes=[IsAuthenticated, IsRestaurantOwner]
        )
    def set_image(self, request: DRFRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> DRFResponse:
        """
        Handle POST requests to set the image URL for a Restaurant.

        Parameters:
            request: DRFRequest
                The request object.
            *args: list
                Additional positional arguments.
            **kwargs: dict
                Additional keyword arguments.
        
        Returns:
            DRFResponse
                A response indicating success or failure.
        """
        serializer = ImageURLSerializer(data=request.data)
        if not serializer.is_valid():
            return DRFResponse({"errors": serializer.errors}, HTTP_400_BAD_REQUEST)

        restaurant: QuerySet[Restaurant] = Restaurant.objects.filter(owner=request.user).first()
        if not restaurant:
            return DRFResponse({"detail": "Restaurant not found."}, HTTP_404_NOT_FOUND)

        restaurant.image_url = serializer.validated_data["image_url"]
        restaurant.save(update_fields=["image_url"])

        return DRFResponse({"detail": "Image updated."}, HTTP_200_OK)


    @extend_schema(
        tags=["Restaurants"],
        summary="Assign/Unassign categories",
        request=CategoryAssignSerializer,
        responses={
            HTTP_200_OK: MessageSerializer,
            HTTP_400_BAD_REQUEST: ValidationErrorSerializer,
            HTTP_401_UNAUTHORIZED: ErrorDetailSerializer,
            HTTP_404_NOT_FOUND: ErrorDetailSerializer,
        },
    )
    @action(
        methods=["post"], 
        detail=False, 
        permission_classes=[IsAuthenticated, IsRestaurantOwner]
        )
    def assign_categories(self, request: DRFRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> DRFResponse:
        """
        Handle POST requests to set the image URL for a Restaurant.

        Parameters:
            request: DRFRequest
                The request object.
            *args: list
                Additional positional arguments.
            **kwargs: dict
                Additional keyword arguments.
        
        Returns:
            DRFResponse
                A response indicating success or failure.
        """
        serializer = CategoryAssignSerializer(data=request.data)
        if not serializer.is_valid():
            return DRFResponse({"errors": serializer.errors}, HTTP_400_BAD_REQUEST)

        restaurant: QuerySet[Restaurant] = Restaurant.objects.filter(owner=request.user).first()
        if not restaurant:
            return DRFResponse({"detail": "Restaurant not found."}, HTTP_404_NOT_FOUND)

        # if assigned then unassign, else assign
        if restaurant.categories.filter(id__in=serializer.validated_data["category_ids"]).exists():
            restaurant.categories.remove(*serializer.validated_data["category_ids"])
            return DRFResponse({"detail": "Categories unassigned."}, HTTP_200_OK)
        restaurant.categories.set(serializer.validated_data["category_ids"])
        return DRFResponse({"detail": "Categories assigned."}, HTTP_200_OK)

    @extend_schema(
        tags=["Restaurants"],
        summary="Add/Remove delivery method to restaurant",
        request=DeliveryAssignSerializer,
        responses={
            HTTP_200_OK: MessageSerializer,
            HTTP_400_BAD_REQUEST: ValidationErrorSerializer,
            HTTP_401_UNAUTHORIZED: ErrorDetailSerializer,
            HTTP_404_NOT_FOUND: ErrorDetailSerializer,
        },
    )
    @action(
        methods=['post'],
        detail=False,
        url_name='delivery',
        url_path='delivery',
        permission_classes=[IsAuthenticated, IsRestaurantOwner],
    )
    def add_delivery_method(
        self,
        request: DRFRequest,
        *args: Any,
        **kwargs: Any
    ) -> DRFResponse:
        """
        Handle POST requests to add or delete delivery methods to a Restaurant.

        Parameters:
            request: DRFRequest
                The request object.
            *args: list
                Additional positional arguments.
            **kwargs: dict
                Additional keyword arguments.
        
        Returns:
            DRFResponse
                A response indicating success or failure.
        """
        serializer = DeliveryAssignSerializer(data=request.data)
        if not serializer.is_valid():
            return DRFResponse({"errors": serializer.errors}, HTTP_400_BAD_REQUEST)

        restaurant: QuerySet[Restaurant] = Restaurant.objects.filter(owner=request.user).first()
        if not restaurant:
            return DRFResponse({"detail": "Restaurant not found."}, HTTP_404_NOT_FOUND)

        # if assigned then unassign, else assign
        if restaurant.delivery_methods.filter(id__in=serializer.validated_data["delivery_ids"]).exists():
            restaurant.delivery_methods.remove(*serializer.validated_data["delivery_ids"])
            return DRFResponse({"detail": "Delivery methods unassigned."}, HTTP_200_OK)
        restaurant.delivery_methods.set(serializer.validated_data["delivery_ids"])
        return DRFResponse({"detail": "Delivery methods assigned."}, HTTP_200_OK)
    
    