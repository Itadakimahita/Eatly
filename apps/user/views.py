from typing import Any
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model
from django.contrib.auth import get_user_model

from rest_framework.viewsets import ViewSet
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_201_CREATED,
    HTTP_205_RESET_CONTENT,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from apps.restaurant.serializers import RestaurantCreateSerializer
from apps.user.models import CustomUser
from apps.user.serializers import (
    UserListSerializer,
    UserLoginSerializer,
    UserRegisterSerializer,
    UserLoginResponseSerializer,
    UserSerializer,
)


class UserViewSet(ViewSet):
    """ViewSet to manage user-related operations."""

    permission_classes = [AllowAny]

    # ----------------------- LOGIN -----------------------
    @extend_schema(
        tags=["User Authentication"],
        summary="Login user",
        description="Authenticate user and return JWT access & refresh tokens.",
        request=UserLoginSerializer,
        responses={HTTP_200_OK: UserLoginResponseSerializer},
        examples=[
            OpenApiExample(
                "Login example",
                value={"email": "user@example.com", "password": "123456"},
            )
        ],
    )
    @action(
        methods=["post"],
        detail=False,
        url_path="login",
        url_name="login",
        permission_classes=[AllowAny],
    )
    def login(self, request: DRFRequest, *args: Any, **kwargs: Any) -> DRFResponse:
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token

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
        return DRFResponse(response_serializer.data, HTTP_200_OK)

    # ----------------------- REGISTER -----------------------
    @extend_schema(
        tags=["User Authentication"],
        summary="Register new user",
        description="Create new user and return JWT tokens.",
        request=UserRegisterSerializer,
        responses={HTTP_201_CREATED: UserLoginResponseSerializer},
    )
    @action(
        methods=["post"],
        detail=False,
        url_path="register",
        url_name="register",
        permission_classes=[AllowAny],
    )
    def register(self, request: DRFRequest, *args, **kwargs) -> DRFResponse:
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token

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
        return DRFResponse(response_serializer.data, HTTP_201_CREATED)

    # ----------------------- LIST USERS -----------------------
    @extend_schema(
        tags=["User Management"],
        summary="Get users list",
        description="Returns a list of all registered users. Requires authentication.",
        responses={HTTP_200_OK: UserListSerializer},
    )
    @action(
        methods=["get"],
        detail=False,
        url_path="list",
        url_name="list",
        permission_classes=[IsAuthenticated],
    )
    def users(self, *args, **kwargs) -> DRFResponse:
        users = CustomUser.objects.all()
        serializer = UserListSerializer({"users": users})
        return DRFResponse(serializer.data, HTTP_200_OK)

    # ----------------------- LOGOUT -----------------------
    @extend_schema(
        tags=["User Authentication"],
        summary="Logout user",
        description="Blacklists the refresh token.",
        request={
            "type": "object",
            "properties": {"refresh": {"type": "string"}},
            "required": ["refresh"],
        },
        responses={
            HTTP_205_RESET_CONTENT: OpenApiExample(
                "Logout success", value={"detail": "Successfully logged out."}
            ),
            HTTP_400_BAD_REQUEST: OpenApiExample(
                "Invalid refresh", value={"detail": "Invalid or expired token."}
            ),
        },
    )
    @action(
        methods=["post"],
        detail=False,
        url_path="logout",
        url_name="logout",
        permission_classes=[IsAuthenticated],
    )
    def logout(self, request: DRFRequest, *args, **kwargs) -> DRFResponse:
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return DRFResponse(
                {"detail": "Refresh token is required."},
                HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return DRFResponse(
                {"detail": "Invalid or expired token."},
                HTTP_400_BAD_REQUEST,
            )

        return DRFResponse({"detail": "Successfully logged out."}, HTTP_205_RESET_CONTENT)

    # ----------------------- RETRIEVE -----------------------
    @extend_schema(
        tags=["User Management"],
        summary="Get single user",
        description="Retrieve user details by ID.",
        parameters=[
            OpenApiParameter("id", int, location="path", description="User ID"),
        ],
        responses={
            200: UserSerializer,
            400: OpenApiExample("User not found", value={"detail": "User not found."}),
        },
    )
    def retrieve(
        self, request: DRFRequest, pk: int = None, *args, **kwargs
    ) -> DRFResponse:
        user = CustomUser.objects.filter(id=pk).first()
        if user:
            serializer = UserSerializer(user)
            return DRFResponse(serializer.data, HTTP_200_OK)

        return DRFResponse({"detail": "User not found."}, HTTP_400_BAD_REQUEST)
