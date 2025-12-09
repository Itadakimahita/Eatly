import pytest
from rest_framework.test import APIClient
from apps.user.models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return CustomUser.objects.create_user(
        email="testuser@example.com",
        name="Test User",
        password="Password123"
    )

@pytest.fixture
def auth_headers(user):
    refresh = RefreshToken.for_user(user)
    return {"HTTP_AUTHORIZATION": f"JWT {str(refresh.access_token)}"}

@pytest.mark.django_db
def test_user_register(api_client):
    url = "/api/user/v1/users/register"
    data = {
        "email": "newuser@example.com",
        "name": "New User",
        "password": "Password123",
    }
    response = api_client.post(url, data)
    assert response.status_code == 201
    assert CustomUser.objects.filter(email="newuser@example.com").exists()

@pytest.mark.django_db
def test_user_login(api_client, user):
    url = "/api/user/v1/users/login"
    data = {
        "email": "testuser@example.com",
        "password": "Password123"
    }
    response = api_client.post(url, data)
    assert response.status_code == 200

@pytest.mark.django_db
def test_user_me(api_client, auth_headers):
    url = "/api/user/v1/users/1"
    response = api_client.get(url, **auth_headers)
    assert response.status_code == 200
