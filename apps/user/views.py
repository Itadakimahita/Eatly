# Python modules
from typing import Any
from rest_framework_simplejwt.tokens import RefreshToken

# Django 
from django.contrib.auth import get_user_model

# Django REST Framework
from rest_framework.viewsets import ViewSet
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_405_METHOD_NOT_ALLOWED, HTTP_201_CREATED, HTTP_205_RESET_CONTENT
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action

from apps.restaurant.serializers import RestaurantCreateSerializer
from apps.user.models import CustomUser
from apps.user.serializers import UserListSerializer, UserLoginSerializer, UserRegisterSerializer, UserLoginResponseSerializer, UserSerializer

class UserViewSet(ViewSet):
    """ViewSet to manage user-related operations."""

    permission_classes = [AllowAny, IsAuthenticated,]

    @action(
        methods=['post'],
        detail=False,
        url_path='login',
        url_name='login',
        permission_classes=[AllowAny,],
    )
    def login(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
        """
        Handle user login.

        Parameters:
            request: 
                DRFRequest: 
                    email: The user's email.
                    password: The user's password.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            DRFResponse: A response containing user data and JWT tokens upon successful login.
        """

        serializer: UserLoginSerializer = UserLoginSerializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        user: CustomUser = serializer.validated_data['user']

        refresh_token: RefreshToken = RefreshToken.for_user(user)
        access_token: str = refresh_token.access_token

        response_serializer = UserLoginResponseSerializer(
            data={
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "refresh": str(refresh_token),
                "access": str(access_token),
            }
        )
        response_serializer.is_valid(raise_exception=True)

        return DRFResponse(
            data=response_serializer.data,
            status=HTTP_200_OK,
        )
    
    @action(
        methods=['post'],
        detail=False,
        url_path='register',
        url_name='register',
        permission_classes=[AllowAny,],
    )
    def register(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
        """
        Handle user registration.
        
        Parameters:
            request: 
                DRFRequest: 
                    name: Full name of the user.
                    email: Email address of the user.
                    password: Password for the user account.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        Returns:
            DRFResponse: A response containing user data and JWT tokens upon successful registration.
        """
        serializer: UserRegisterSerializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        # JWT Token generation
        refresh_token: RefreshToken = RefreshToken.for_user(user)
        access_token: str = refresh_token.access_token

        response_serializer = UserLoginResponseSerializer(
            data={
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "refresh": str(refresh_token),
                "access": str(access_token),
            }
        )
        response_serializer.is_valid(raise_exception=True)

        return DRFResponse(
            data=response_serializer.data,
            status=HTTP_201_CREATED,
        )
    
    @action(
        methods=['get'],
        detail=False,
        url_path='list',
        url_name='list',
        permission_classes=[IsAuthenticated,],
    )
    def users(self, *args: Any, **kwargs: Any) -> DRFResponse:
        """
        List all users.
        
        Parameters:
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        Returns:
            DRFResponse: A response containing the list of users.
        """ 
        
        users = CustomUser.objects.all()
        serializer = UserListSerializer({"users": users})
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    
    @action(
        methods=['post'],
        detail=False,
        url_path='logout',
        url_name='logout',
        permission_classes=[IsAuthenticated,],
    )
    def logout(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
        """
        Handle user logout by blacklisting the refresh token.

        Parameters:
            request: 
                DRFRequest: 
                    refresh: The refresh token to be blacklisted.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            DRFResponse: A response indicating successful logout.
        """

        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return DRFResponse(
                data={"detail": "Refresh token is required."},
                status=HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return DRFResponse(
                data={"detail": "Invalid or expired token."},
                status=HTTP_400_BAD_REQUEST,
            )

        return DRFResponse(
            data={"detail": "Successfully logged out."},
            status=HTTP_205_RESET_CONTENT,
        )
    
    def retrieve(self, request: DRFRequest, pk: int = None, *args: Any, **kwargs: Any) -> DRFResponse:
        """
        Retrieve user details by ID.

        Parameters:
            request: 
                DRFRequest: The incoming request.
            id: 
                int: The ID of the user to retrieve.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        Returns:
            DRFResponse: A response containing user details if found, else an error message.
        """

        user = CustomUser.objects.filter(id=pk).first()
        if user:
            serializer: UserSerializer = UserSerializer(user)
            return DRFResponse(
                data=serializer.data,
                status=HTTP_200_OK,
            )
        return DRFResponse(
            data={"detail": "User not found."},
            status=HTTP_400_BAD_REQUEST,
        )
    
    # Restaurant
    # @action(
    #     methods=['post'],
    #     detail=True,
    #     url_path='create-restaurant',
    #     url_name='create-restaurant',
    #     permission_classes=[IsAuthenticated,],
    # )
    # def create_restaurant(self, request: DRFRequest, pk: int = None, *args: Any, **kwargs: Any) -> DRFResponse:
    #     """
    #     Create a restaurant for the user.

    #     Parameters:
    #         request: 
    #             DRFRequest: 
    #                 name: Name of the restaurant.
    #                 description: Description of the restaurant.
    #                 address: Address of the restaurant.
    #                 address_link: Link to the restaurant's address.
    #         pk: 
    #             int: The ID of the user creating the restaurant.
    #         *args: Additional positional arguments.
    #         **kwargs: Additional keyword arguments.
    #     Returns:
    #         DRFResponse: A response indicating the result of the restaurant creation.
    #     """
    #     user = CustomUser.objects.filter(id=pk).first()
    #     if not user:
    #         return DRFResponse(
    #             data={"detail": "User not found."},
    #             status=HTTP_400_BAD_REQUEST,
    #         )
        
    #     serializer: UserSerializer = UserSerializer(user)
    #     restaurant_serializer: RestaurantCreateSerializer = RestaurantCreateSerializer(data=request.data)
    #     if not restaurant_serializer.is_valid():
    #         return DRFResponse(
    #             data=restaurant_serializer.errors,
    #             status=HTTP_400_BAD_REQUEST,
    #         )
    #     return DRFResponse(
    #         data=serializer.data,
    #         status=HTTP_201_CREATED,
    #     )