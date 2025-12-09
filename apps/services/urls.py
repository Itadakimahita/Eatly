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