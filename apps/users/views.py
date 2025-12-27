from typing import Any

from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_205_RESET_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
)

from rest_framework_simplejwt.tokens import RefreshToken

from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.users.models import CustomUser
from apps.users.serializers import (
    LogoutRequestSerializer,
    UserListResponseSerializer,
    UserLoginSerializer,
    UserLoginSuccessSerializer,
    UserRegisterSerializer,
    UserSerializer,
)
from apps.abstract.serializers import ErrorDetailSerializer, MessageSerializer, ValidationErrorSerializer


class UserViewSet(ViewSet):
    permission_classes = [AllowAny]

    # ---------------- LOGIN ----------------
    @extend_schema(
        tags=["User Authentication"],
        summary="Login user",
        request=UserLoginSerializer,
        responses={
            HTTP_200_OK: UserLoginSuccessSerializer,
            HTTP_400_BAD_REQUEST: ValidationErrorSerializer,
            HTTP_401_UNAUTHORIZED: ErrorDetailSerializer,
        },
    )
    @action(methods=["post"], detail=False, permission_classes=[AllowAny])
    def login(self, request: DRFRequest) -> DRFResponse:
        """Handle user login requests.
        Args:
            request (Request): The incoming request.
        Returns:
            Response: The response containing the JWT tokens and user info.
        """
        serializer = UserLoginSerializer(data=request.data)

        if not serializer.is_valid():
            return DRFResponse(
                {"errors": serializer.errors},
                HTTP_400_BAD_REQUEST,
            )

        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        response = UserLoginSuccessSerializer(
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        )
        return DRFResponse(response.data, HTTP_200_OK)

    # ---------------- REGISTER ----------------
    @extend_schema(
        tags=["User Authentication"],
        summary="Register user",
        request=UserRegisterSerializer,
        responses={
            HTTP_201_CREATED: UserLoginSuccessSerializer,
            HTTP_400_BAD_REQUEST: ValidationErrorSerializer,
        },
    )
    @action(methods=["post"], detail=False, permission_classes=[AllowAny])
    def register(self, request: DRFRequest) -> DRFResponse:
        """Handle user registration requests.
        Args:
            request (Request): The incoming request.
        Returns:
            Response: The response containing the JWT tokens and user info.
        """
        serializer = UserRegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return DRFResponse(
                {"errors": serializer.errors},
                HTTP_400_BAD_REQUEST,
            )

        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        response = UserLoginSuccessSerializer(
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        )
        return DRFResponse(response.data, HTTP_201_CREATED)

    # ---------------- LIST USERS ----------------
    @extend_schema(
        tags=["User Management"],
        summary="List users",
        responses={
            HTTP_200_OK: UserListResponseSerializer,
            HTTP_401_UNAUTHORIZED: ErrorDetailSerializer,
        },
    )
    @action(methods=["get"], detail=False, permission_classes=[IsAuthenticated])
    def users(self, request: DRFRequest) -> DRFResponse:
        """Handle Get request to list all users.
        Args:
            request (DRFRequest): The incoming request.
        Returns:
            DRFResponse: The response containing the list of users.
        """
        users = CustomUser.objects.all()
        serializer = UserListResponseSerializer({"users": users})
        return DRFResponse(serializer.data, HTTP_200_OK)

    # ---------------- LOGOUT ----------------
    @extend_schema(
        tags=["User Authentication"],
        summary="Logout user",
        request=LogoutRequestSerializer,
        responses={
            HTTP_205_RESET_CONTENT: MessageSerializer,
            HTTP_400_BAD_REQUEST: ErrorDetailSerializer,
            HTTP_401_UNAUTHORIZED: ErrorDetailSerializer,
        },
    )
    @action(methods=["post"], detail=False, permission_classes=[IsAuthenticated])
    def logout(self, request: DRFRequest) -> DRFResponse:
        """Handle user logout requests.
        Args:
            request (DRFRequest): The incoming request.
        Returns:
            DRFResponse: The response indicating logout success or failure.
        """
        serializer = LogoutRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return DRFResponse(
                {"detail": "Refresh token is required."},
                HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(serializer.validated_data["refresh"])
            token.blacklist()
        except Exception:
            return DRFResponse(
                {"detail": "Invalid or expired token."},
                HTTP_400_BAD_REQUEST,
            )

        return DRFResponse(
            {"detail": "Successfully logged out."},
            HTTP_205_RESET_CONTENT,
        )

    # ---------------- RETRIEVE ----------------
    @extend_schema(
        tags=["User Management"],
        summary="Retrieve user",
        parameters=[
            OpenApiParameter("id", int, OpenApiParameter.PATH),
        ],
        responses={
            HTTP_200_OK: UserSerializer,
            HTTP_400_BAD_REQUEST: ErrorDetailSerializer,
            HTTP_401_UNAUTHORIZED: ErrorDetailSerializer,
        },
    )
    def retrieve(self, request: DRFRequest, pk: int = None) -> DRFResponse:
        """Handle Get request to retrieve a user by ID.
        Args:
            request (DRFRequest): The incoming request.
            pk (int, optional): The ID of the user to retrieve. Defaults to None.
        Returns:
            DRFResponse: The response containing the user data or an error message.
        """
        user = CustomUser.objects.filter(pk=pk).first()

        if not user:
            return DRFResponse(
                {"detail": "User not found."},
                HTTP_400_BAD_REQUEST,
            )

        return DRFResponse(UserSerializer(user).data, HTTP_200_OK)
