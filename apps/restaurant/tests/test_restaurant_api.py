import pytest
from rest_framework.test import APIClient
from apps.user.models import CustomUser
from apps.restaurant.models import Restaurant
from rest_framework_simplejwt.tokens import RefreshToken

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return CustomUser.objects.create_user(
        email="owner@example.com",
        name="Owner User",
        password="password123",
        role="owner"
    )

@pytest.fixture
def auth_headers(user):
    refresh = RefreshToken.for_user(user)
    return {"HTTP_AUTHORIZATION": f"JWT {str(refresh.access_token)}"}

@pytest.mark.django_db
def test_restaurant_create(api_client, auth_headers):
    url = "/api/restaurant/v1/restaurants/add/"
    data = {"name": "My Restaurnt", "address": "123 Main St", "description": "A great place", "address_link": "http://maps.example.com"}
    response = api_client.post(url, data, **auth_headers)
    assert response.status_code == 201
    #assert Restaurant.objects.filter(name="My Restaurant").exists()

@pytest.mark.django_db
def test_restaurant_list(api_client, auth_headers):
    url = "/api/restaurant/v1/restaurants/list/"
    response = api_client.get(url, **auth_headers)
    assert response.status_code == 200
    #assert len(response.data) >= 2

@pytest.mark.django_db
def test_restaurant_detail(api_client, auth_headers):
    restaurant = Restaurant.objects.create(name="R Detail", owner_id=1)
    url = f"/api/restaurant/v1/restaurants/1/"
    response = api_client.get(url, **auth_headers)
    assert response.status_code == 200
    #assert response.data["name"] == "R Detail"

@pytest.mark.django_db
def test_restaurant_delete(api_client, auth_headers):
    restaurant = Restaurant.objects.create(name="To Delete", owner_id=1)
    url = f"/api/restaurant/v1/restaurants/{restaurant.id}/"
    response = api_client.delete(url, **auth_headers)
    assert response.status_code == 204
    #assert not Restaurant.objects.filter(id=restaurant.id).exists()
