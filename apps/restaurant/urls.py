# Django modules
from django.urls import include, path

# Django Rest Framework modules
from rest_framework.routers import DefaultRouter

# Project modules
from apps.restaurant.views import RestaurantViewSet


router: DefaultRouter = DefaultRouter(
    trailing_slash=True
)

router.register(
    prefix="restaurants",
    viewset=RestaurantViewSet,
    basename="restaurants",
)

urlpatterns = [
    path("v1/", include(router.urls)),
]