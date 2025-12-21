#Py
from typing import Any

#Django
from django.db.models import QuerySet, Count
from django.shortcuts import render, get_object_or_404

#DRF
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
)
from rest_framework.decorators import action

#Project
from apps.services.models import Post, Comment, UserLike, UserSubscription
from apps.services.serializers import (
    PostLikeSerializer,
    PostListSerializer,
    PostDetailSerializer,
    PostCreateUpdateSerializer,
    CommentSerializer,
    UserLikeSerializer,
    UserSubscriptionSerializer,
)
from apps.services.permissions import IsOwnerOrReadOnly, IsSubscriptionOwner
from apps.user.models import CustomUser

class PostViewSet(ViewSet):
    """
    CRUD для Post + дополнительные экшены:
      - /posts/{pk}/like/  (POST -> like, DELETE -> unlike)
      - /posts/{pk}/comments/ (GET, POST)
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        if self.action=="create":
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    def get_queryset(self) -> QuerySet[Post]:
        qs=Post.objects.all().select_related("restaurant").annotate(
            likes_count = Count("liked_by", distinct=True),
            comments_count = Count("comments", distinct=True),).order_by("-created_at")

        restaurant_id = self.request.query_params.get("restaurant")
        if restaurant_id:
            qs = qs.filter(restaurant_id=restaurant_id)
        return qs
    
    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        if self.action in ("create", "update", "partial_update"):
            return PostCreateUpdateSerializer
        return PostListSerializer
    
    def list(self, request):
        qs = self.get_queryset()
        serializer = self.get_serializer_class()(qs, many=True)
        return DRFResponse(serializer.data, status=HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        post = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer_class()(post)
        return DRFResponse(serializer.data, status=HTTP_200_OK)
    
    def create(self, request):
        serializer = self.get_serializer_class()(data=request.data, context={"request": request})
        serializer.save()
        serializer.is_valid(raise_exception=True)
        return DRFResponse(serializer.data, status=HTTP_201_CREATED)
    
    def update(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, post)
        serializer = self.get_serializer_class()(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    def partial_update(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, post)
        serializer = self.get_serializer_class()(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(serializer.data, status=HTTP_200_OK)
    
    def destroy(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, post)
        post.delete()
        return DRFResponse(status=HTTP_204_NO_CONTENT)
    
    @action(
        methods=["post", "delete"],
        detail=True,
        url_path="like",
        url_name="like",
        permission_classes=[IsAuthenticated],
    )
    def like(self, request, pk=None, *args, **kwargs):
        user = request.user
        post = get_object_or_404(Post, pk=pk)

        if request.method == "POST":
            like, created = UserLike.objects.get_or_create(
                user=user, discount_post=post
            )
            if created:
                return DRFResponse(
                    UserLikeSerializer(like).data,
                    status=HTTP_201_CREATED,
                )
            return DRFResponse(
                {"detail": "Already liked."},
                status=HTTP_400_BAD_REQUEST,
            )

        deleted, _ = UserLike.objects.filter(
            user=user, discount_post=post
        ).delete()

        if deleted:
            return DRFResponse(status=HTTP_204_NO_CONTENT)
        return DRFResponse(
            {"detail": "Like not found."},
            status=HTTP_404_NOT_FOUND,
        )

    @action(
        methods=["get", "post"],
        detail=True,
        url_path="comments",
        url_name="comments",
        permission_classes=[AllowAny],
    )
    def comments(self, request, pk=None, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)

        if request.method == "GET":
            qs = post.comments.select_related("user").order_by("created_at")
            serializer = CommentSerializer(qs, many=True)
            return DRFResponse(serializer.data, status=HTTP_200_OK)

        if not request.user or not request.user.is_authenticated:
            return DRFResponse(
                {"detail": "Authentication required."},
                status=HTTP_401_UNAUTHORIZED,
            )

        data = request.data.copy()
        data["post"] = pk
        serializer = CommentSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        return DRFResponse(
            CommentSerializer(comment).data,
            status=HTTP_201_CREATED,
        )

class CommentViewSet(ViewSet):
    """
    CRUD для Comment (редактировать/удалить может только автор)
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    def get_queryset(self):
        return Comment.objects.all().select_related("user", "post")
    
    def list(self, request):
        qs = self.get_queryset()
        serializer = CommentSerializer(qs, many=True)
        return DRFResponse(serializer.data, status=HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        comment = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = CommentSerializer(comment)
        return DRFResponse(serializer.data, status=HTTP_200_OK)
    
    def create(self, request):
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return DRFResponse(serializer.data, status=HTTP_201_CREATED)
    
    def update(self, request, pk=None):
        comment = get_object_or_404(Comment, pk=pk)
        self.check_object_permissions(request, comment)
        serializer = CommentSerializer(comment, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(serializer.data, status=HTTP_200_OK)
    
    def destroy(self, request, pk=None):
        comment = get_object_or_404(Comment, pk=pk)
        self.check_object_permissions(request, comment)
        comment.delete()
        return DRFResponse(status=HTTP_204_NO_CONTENT)
        

class UserLikeViewSet(ViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = UserLike.objects.all().select_related("user", "discount_post")
        user_id = self.request.query_params.get("user")
        if user_id:
            return qs.filter(user_id=user_id)
        return qs.filter(user=self.request.user)

    def list(self, request):
        serializer = UserLikeSerializer(self.get_queryset(), many=True)
        return DRFResponse(serializer.data)

    def create(self, request):
        serializer = UserLikeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return DRFResponse(serializer.data, status=HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        like = get_object_or_404(UserLike, pk=pk, user=request.user)
        like.delete()
        return DRFResponse(status=HTTP_204_NO_CONTENT)


class UserSubscriptionViewSet(ViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.action in ("destroy",):
            return [IsAuthenticated(), IsSubscriptionOwner()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = UserSubscription.objects.all().select_related("user", "restaurant")
        user_id = self.request.query_params.get("user")
        if user_id:
            return qs.filter(user_id=user_id)
        return qs.filter(user=self.request.user)

    def list(self, request):
        serializer = UserSubscriptionSerializer(self.get_queryset(), many=True)
        return DRFResponse(serializer.data)

    def retrieve(self, request, pk=None):
        sub = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = UserSubscriptionSerializer(sub)
        return DRFResponse(serializer.data)

    def create(self, request):
        serializer = UserSubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return DRFResponse(serializer.data, status=HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        sub = get_object_or_404(UserSubscription, pk=pk)
        self.check_object_permissions(request, sub)
        sub.delete()
        return DRFResponse(status=HTTP_204_NO_CONTENT)