import pytest
from rest_framework.test import APIClient
from apps.users.models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_405_METHOD_NOT_ALLOWED,
)

@pytest.fixture
def api_client():
    """Fixture to provide an API client for testing."""
    return APIClient()

@pytest.fixture
def user(db):
    """Fixture to create a test user."""
    return CustomUser.objects.create_user(
        email="testuser@example.com",
        name="Test User",
        password="Password123"
    )

@pytest.fixture
def auth_headers(user):
    """Fixture to provide authentication headers for a test user."""
    refresh = RefreshToken.for_user(user)
    return {"HTTP_AUTHORIZATION": f"JWT {str(refresh.access_token)}"}

@pytest.fixture
def another_user(db):
    """Fixture to create another test user."""
    return CustomUser.objects.create_user(
        email = "other@example.com",
        name = "Other User",
        password = "Password456",
    )


"""
TESTS FOR POST /users/login
"""

#positive
@pytest.mark.django_db
def test_login_user_success(api_client, user):
    response = api_client.post(
        "/api/user/v1/users/login",
        data={
            "email": user.email,
            "password": "Password123",
        }
    )
    assert response.status.code == HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data

#negative
@pytest.mark.django_db
def test_user_login_wrong_password(api_client, user):
    response = api_client.post(
        "/api/user/v1/users/login",
        data={
            "email": user.email,
            "password": "WrongPassword",
        }
    )
    assert response.status_code == HTTP_400_BAD_REQUEST

#negative2
@pytest.mark.django_db
def test_user_login_wrong_email(api_client):
    response = api_client.post(
        "/api/user/v1/users/login",
        data={
            "email": "wrong@example.com",
            "password": "Password123",
        }
    )
    assert response.status_code == HTTP_400_BAD_REQUEST

#negative3
@pytest.mark.django_db
def test_user_login_missing_fields(api_client):
    response = api_client.post(
        "/api/user/v1/users/login",
        data={})
    assert response.status_code == HTTP_400_BAD_REQUEST



"""
TESTS FOR POST /users/register
"""

#positive
@pytest.mark.django_db
def test_register_user_success(api_client):
    response = api_client.post(
        "/api/user/v1/users/register",
        data={
            "email": "newuser@example.com",
            "name": "New User",
            "password": "NewPassword123",
        }
    )
    assert response.status_code == HTTP_201_CREATED
    assert CustomUser.objects.filter(email="newuser@example.com").exists()

#negative1
@pytest.mark.django_db
def test_register_user_existing_email(api_client, user):
    response = api_client.post(
        "/api/user/v1/users/register",
        data={
            "email": user.email,
            "name": "Duplicate User",
            "password": "DuplicatePassword123",
        }
    )
    assert response.status_code == HTTP_400_BAD_REQUEST

#negative2
@pytest.mark.django_db
def test_user_register_short_password(api_client):
    response = api_client.post(
        "/api/user/v1/users/register",
        data={
            "email": "short@example.com",
            "name": "Short",
            "password": "123",
        }
    )
    assert response.status_code == HTTP_400_BAD_REQUEST

#negative3
@pytest.mark.django_db
def test_user_register_missing_fields(api_client):
    response = api_client.post(
        "/api/user/v1/users/register",
        data={})
    assert response.status_code == HTTP_400_BAD_REQUEST
            

"""
Tests for GET users/list
"""
#positive
@pytest.mark.django_db
def test_user_list_success(api_client, auth_headers):
    response = api_client.get(
        "/api/user/v1/users/list",
        **auth_headers
    )
    assert response.status_code == HTTP_200_OK
    assert "users" in response.data

#negative1
@pytest.mark.django_db
def test_user_list_unauthenticated(api_client):
    response = api_client.get(
        "/api/user/v1/users/list"
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED

#negative2
@pytest.mark.django_db
def test_user_list_wrong_method(api_client, auth_headers):
    response = api_client.post(
        "/api/user/v1/users/list",
        **auth_headers
    )
    assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED

#negative3
@pytest.mark.django_db
def test_user_list_empty(api_client, auth_headers):
    CustomUser.objects.all().delete()
    response = api_client.get(
        "/api/user/v1/users/list",
        **auth_headers
    )
    assert response.status_code == HTTP_200_OK
    assert response.data["users"] == []



"""
Tests for POST users/logout
"""
#positive
@pytest.mark.django_db
def test_user_logout_success(api_client, auth_headers, user):
    refresh = RefreshToken.for_user(user)
    response = api_client.post(
        "/api/user/v1/users/logout",
        data = {"refresh": str(refresh)},
        **auth_headers
    )
    assert response.status_code == HTTP_200_OK

#negative1
@pytest.mark.django_db
def test_user_logout_no_token(api_client, auth_headers):
    response = api_client.post(
        "/api/user/v1/users/logout",
        data = {},
        **auth_headers
    )
    assert response.status_code == HTTP_400_BAD_REQUEST

#negative2
@pytest.mark.django_db
def test_user_logout_invalid_token(api_client, auth_headers):
    response = api_client.post(
        "/api/user/v1/users/logout",
        data = {"refresh": "invalidtoken"},
        **auth_headers
    )
    assert response.status_code == HTTP_400_BAD_REQUEST

#negative3
@pytest.mark.django_db
def test_user_logout_unauthenticated(api_client):
    response = api_client.post(
        "/api/user/v1/users/logout",
        data = {"refresh": "sometoken"},
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED



"""
TESTS FOR GET users/id
"""
#positive
@pytest.mark.django_db
def test_user_retrieve_success(api_client, user):
    response = api_client.get(
        f"/api/user/v1/users/{user.id}"
    )
    assert response.status_code == HTTP_200_OK
    assert response.data["email"] == user.email

#negative1
@pytest.mark.django_db
def test_user_retrieve_not_found(api_client):
    response = api_client.get(
        "/api/user/v1/users/9999"
    )
    assert response.status_code == HTTP_400_BAD_REQUEST

#negative2
@pytest.mark.django_db
def test_user_retrieve_invalid_id(api_client):
    response = api_client.get(
        "/api/user/v1/users/invalid"
    )
    assert response.status_code in (HTTP_400_BAD_REQUEST, 404)

#negative3
@pytest.mark.django_db
def test_user_retrieve_wrong_method(api_client, user):
    response = api_client.post(
        f"/api/user/v1/users/{user.id}"
    )
    assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED