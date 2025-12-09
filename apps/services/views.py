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

class PostViewSet(ModelViewSet):
    """
    CRUD для Post + дополнительные экшены:
      - /posts/{pk}/like/  (POST -> like, DELETE -> unlike)
      - /posts/{pk}/comments/ (GET, POST)
    """
    queryset: QuerySet[Post] = Post.objects.all()
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)  # методы чтения могут менять в get_permissions
    serializer_class = PostListSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        if self.action in ("create",):
            return [IsAuthenticated()]
        # update/destroy/partial_update -> check owner or restaurant owner
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    def get_queryset(self):
        qs = Post.objects.all().select_related("restaurant").annotate(
            likes_count=Count("liked_by", distinct=True),
            comments_count=Count("comments", distinct=True),
        ).order_by("-created_at")
        # можно фильтровать по ресторану: ?restaurant=1
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

    def perform_create(self, serializer):
        # сохраняем пост как есть; при необходимости можно проверять, что пользователь — owner ресторана
        serializer.save()

    @action(
        methods=["post", "delete"],
        detail=True,
        url_path="like",
        url_name="like",
        permission_classes=[IsAuthenticated],
    )
    def like(self, request: DRFRequest, pk: int = None, *args: Any, **kwargs: Any) -> DRFResponse:
        """
        POST -> поставить лайк (id поста в pk)
        DELETE -> убрать лайк текущего пользователя
        """
        user: CustomUser = request.user
        post = get_object_or_404(Post, pk=pk)

        if request.method == "POST":
            # создать лайк если не существует
            like, created = UserLike.objects.get_or_create(user=user, discount_post=post)
            if created:
                serializer = UserLikeSerializer(like)
                return DRFResponse(serializer.data, status=HTTP_201_CREATED)
            return DRFResponse({"detail": "Already liked."}, status=HTTP_400_BAD_REQUEST)

        # DELETE
        deleted, _ = UserLike.objects.filter(user=user, discount_post=post).delete()
        if deleted:
            return DRFResponse(status=HTTP_204_NO_CONTENT)
        return DRFResponse({"detail": "Like not found."}, status=HTTP_404_NOT_FOUND)

    @action(
        methods=["get", "post"],
        detail=True,
        url_path="comments",
        url_name="comments",
        permission_classes=[AllowAny],  # GET доступен всем, POST требует авторизации (см внутри)
    )
    def comments(self, request: DRFRequest, pk: int = None, *args: Any, **kwargs: Any) -> DRFResponse:
        """
        GET -> список комментариев к посту
        POST -> добавить комментарий (auth required)
        """
        post = get_object_or_404(Post, pk=pk)

        if request.method == "GET":
            qs = post.comments.select_related("user").order_by("created_at")
            serializer = CommentSerializer(qs, many=True)
            return DRFResponse(serializer.data, status=HTTP_200_OK)

        # POST
        if not request.user or not request.user.is_authenticated:
            return DRFResponse({"detail": "Authentication required."}, status=HTTP_401_UNAUTHORIZED)

        data = request.data.copy()
        data["post"] = pk
        serializer = CommentSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        return DRFResponse(CommentSerializer(comment).data, status=HTTP_201_CREATED)

class CommentViewSet(ModelViewSet):
    """
    CRUD для Comment (редактировать/удалить может только автор)
    """
    queryset = Comment.objects.all().select_related("user", "post")
    serializer_class = CommentSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserLikeViewSet(ModelViewSet):
    """
    Работалайками (обычно для админки/отладки): list user's likes, create, destroy.
    """
    queryset = UserLike.objects.all().select_related("user", "discount_post")
    serializer_class = UserLikeSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # если передан ?user= -> фильтр, иначе только свои
        user_id = self.request.query_params.get("user")
        if user_id:
            return self.queryset.filter(user_id=user_id)
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserSubscriptionViewSet(ModelViewSet):
    """
    Подписки пользователя на рестораны.
    - POST /subscriptions/  body: {"restaurant": id} -> подписаться
    - DELETE /subscriptions/{pk}/ -> отписаться (только владелец подписки)
    - GET list -> свои подписки
    """
    queryset = UserSubscription.objects.all().select_related("user", "restaurant")
    serializer_class = UserSubscriptionSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # по умолчанию показываем подписки текущего юзера
        qs = self.queryset
        user_id = self.request.query_params.get("user")
        if user_id:
            return qs.filter(user_id=user_id)
        return qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        # уникальность enforced в модели через unique_together
        serializer.save(user=self.request.user)

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated()]
        if self.action in ("destroy",):
            return [IsAuthenticated(), IsSubscriptionOwner()]
        return [IsAuthenticated()]