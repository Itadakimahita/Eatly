from django.urls import include, path

from rest_framework.routers import DefaultRouter

from apps.services.views import (
    PostViewSet,
    CommentViewSet,
    UserLikeViewSet,
    UserSubscriptionViewSet,
)

router = DefaultRouter(trailing_slash=True)
router.register(prefix="posts", viewset = PostViewSet, basename="posts")
router.register(prefix = "comments", viewset=CommentViewSet, basename="comments")
router.register(prefix = "likes", viewset=UserLikeViewSet, basename="likes")
router.register(prefix="subscriptions", viewset=UserSubscriptionViewSet, basename="subscriptions")

urlpatterns = [
    path("v1/", include(router.urls)),
]


'''
POSTS

GET    /api/services/v1/posts/          — получить все посты
POST   /api/services/v1/posts/          — создать пост
GET    /api/services/v1/posts/{id}/     — получить 1 пост
PUT    /api/services/v1/posts/{id}/     — обновить
PATCH  /api/services/v1/posts/{id}/     — частично обновить
DELETE /api/services/v1/posts/{id}/     — удалить

'''

'''
COMMMENTS
GET    /api/services/v1/comments/
POST   /api/services/v1/comments/
GET    /api/services/v1/comments/{id}/
PUT    /api/services/v1/comments/{id}/
DELETE /api/services/v1/comments/{id}/

'''

''''
LIKES
GET /api/services/v1/likes/      — список всех лайков
POST /api/services/v1/likes/     — поставить лайк (если не используешь постовый)
'''


'''
SUBSCRIPTIONS
GET /api/services/v1/subscriptions/
POST /api/services/v1/subscriptions/
DELETE /api/services/v1/subscriptions/{id}/
'''