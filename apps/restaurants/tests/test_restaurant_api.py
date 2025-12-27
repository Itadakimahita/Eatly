import pytest
from rest_framework.test import APIClient
from apps.users.models import CustomUser
from apps.restaurants.models import Restaurant, Category
from apps.users.entities.role_entity import UserRoleEntity
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def owner(db):
    """Create and return a restaurant owner user."""
    return CustomUser.objects.create_user(
        email="owner@example.com",
        password="password123",
        role=UserRoleEntity.OWNER, 
        name = "Owner Name",
    )

@pytest.fixture
def auth_headers(owner):
    """Return authentication headers for the owner user."""
    refresh = RefreshToken.for_user(owner)
    return {"HTTP_AUTHORIZATION": f"JWT {str(refresh.access_token)}"}

@pytest.fixture
def another_user(db):
    """Create and return a regular customer user."""
    return CustomUser.objects.create_user(
        email="user@test.com",
        password="password123",
        role=UserRoleEntity.CUSTOMER,
        name = "User Name",
    )

@pytest.fixture
def auth_headers_other(another_user):
    refresh = RefreshToken.for_user(another_user)
    return {"HTTP_AUTHORIZATION": f"JWT {str(refresh.access_token)}"}

@pytest.fixture
def restaurant(owner):
    return Restaurant.objects.create(
        name="Testaurant",
        owner=owner,
        address="123 Test St",    
    )




"""
Tests for POST /restaurants/add/
"""
#positive
@pytest.mark.django_db
def test_create_restaurant_success(api_client, auth_headers):
    url = "/api/restaurant/v1/restaurants/add/"
    data = {
        "name" : "New Restaurant",
        "address" : "456 New St",
        "description" : "A brand new restaurant",
        "address_link" : "http://maps.test",
    }
    response = api_client.post(url, data, **auth_headers)
    assert response.status_code == HTTP_201_CREATED
    assert Restaurant.objects.filter(name="New Restaurant").exists()

#negative1
@pytest.mark.django_db
def test_create_restaurant_unauthorized(api_client):
    response = api_client.post("/api/restaurant/v1/restaurants/add/", {})
    assert response.status_code == HTTP_401_UNAUTHORIZED

#negative2
@pytest.mark.django_db
def test_create_restaurant_missing_name(api_client, auth_headers):
    response = api_client.post(
        "/api/restaurant/v1/restaurants/add/",
        {
            "address": "456 New St",
        },
            **auth_headers
    )
    assert response.status_code == HTTP_400_BAD_REQUEST

#negative3
@pytest.mark.django_db
def test_create_restaurant_invalid_link(api_client, auth_headers):
    response = api_client.post(
        "/api/restaurant/v1/restaurants/add/",
        {
            "name": "Invalid Link Restaurant",
            "address": "789 Invalid St",
            "address_link": "not-a-valid-url",
        },
        **auth_headers
    )
    assert response.status_code == HTTP_400_BAD_REQUEST




"""
Tests for Get /restaurants/{id}/
"""

#positive
@pytest.mark.django_db
def test_get_restaurant_success(api_client, restaurant, auth_headers):
    url = f"/api/restaurant/v1/restaurants/{restaurant.id}/"
    response = api_client.get(url, **auth_headers)
    assert response.status_code == HTTP_200_OK
    assert response.data["name"] == restaurant.name

#negative1
@pytest.mark.django_db
def test_get_restaurant_not_found(api_client, auth_headers):
    url = "/api/restaurant/v1/restaurants/9999/"
    response = api_client.get(url, **auth_headers)
    assert response.status_code == HTTP_404_NOT_FOUND

#negative2
@pytest.mark.django_db
def test_get_restaurant_not_owner(api_client, restaurant, auth_headers_other):
    url = f"/api/restaurant/v1/restaurants/{restaurant.id}/"
    response = api_client.get(url, **auth_headers_other)
    assert response.status_code == HTTP_403_FORBIDDEN

#negative3
@pytest.mark.django_db
def test_get_restaurant_unauthenticated(api_client, restaurant):
    url = f"/api/restaurant/v1/restaurants/{restaurant.id}/"
    response = api_client.get(url)
    assert response.status_code == HTTP_401_UNAUTHORIZED




"""
Tests for Patch /restaurants/{id}
"""
#positive
@pytest.mark.django_db
def test_update_restaurant_success(api_client, restaurant, auth_headers):
    url = f"/api/restaurant/v1/restaurants/{restaurant.id}/"
    response = api_client.patch(url, {"name": "updated"}, **auth_headers)
    assert response.status_code == HTTP_200_OK
    restaurant.refresh_from_db()
    assert restaurant.name == "Updated Restaurant Name"

#negative1
@pytest.mark.django_db
def test_update_restaurant_not_owner(api_client, restaurant, auth_headers_other):
    url = f"/api/restaurant/v1/restaurants/{restaurant.id}/"
    response = api_client.patch(url, {"name": "Hacked Name"}, **auth_headers_other)
    assert response.status_code == HTTP_403_FORBIDDEN

#negative2
@pytest.mark.django_db
def test_update_restaurant_invalid_data(api_client, restaurant, auth_headers):
    url = f"/api/restaurant/v1/restaurants/{restaurant.id}/"
    response = api_client.patch(url, {"address_link": "invalid-url"}, **auth_headers)
    assert response.status_code == HTTP_400_BAD_REQUEST

#negative3
@pytest.mark.django_db
def test_update_restaurant_not_found(api_client, auth_headers):
    url = "/api/restaurant/v1/restaurants/9999/"
    response = api_client.patch(url, {"name": "Nonexistent"}, **auth_headers)
    assert response.status_code == HTTP_404_NOT_FOUND


"""
Tests for Delete /restaurants/{id}
"""
#positive
@pytest.mark.django_db
def test_delete_restaurant_success(api_client, restaurant, auth_headers):
    url = f"/api/restaurant/v1/restaurants/{restaurant.id}/"
    response = api_client.delete(url, **auth_headers)
    assert response.status_code == HTTP_204_NO_CONTENT
    assert not Restaurant.objects.filter(id=restaurant.id).exists()

#negative1
@pytest.mark.django_db
def test_delete_restaurant_not_owner(api_client, restaurant, auth_headers_other):
    url = f"/api/restaurant/v1/restaurants/{restaurant.id}/"
    response = api_client.delete(url, **auth_headers_other)
    assert response.status_code == HTTP_403_FORBIDDEN

#negative2
@pytest.mark.django_db
def test_delete_restaurant_not_found(api_client, auth_headers):
    url = "/api/restaurant/v1/restaurants/9999/"
    response = api_client.delete(url, **auth_headers)
    assert response.status_code == HTTP_404_NOT_FOUND

#negative3
@pytest.mark.django_db
def test_delete_restaurant_unauthenticated(api_client, restaurant):
    url = f"/api/restaurant/v1/restaurants/{restaurant.id}/"
    response = api_client.delete(url)
    assert response.status_code == HTTP_401_UNAUTHORIZED


"""
Tests for GET /restaurants/list/
"""
#positive
@pytest.mark.django_db
def test_list_restaurants_list_success(api_client, auth_headers, restaurant):
    url = "/api/restaurant/v1/restaurants/list/"
    response = api_client.get(url, **auth_headers)
    assert response.status_code == HTTP_200_OK
    assert isinstance(response.data, list)

#negative1
@pytest.mark.django_db
def test_list_restaurants_unauthenticated(api_client):
    url = "/api/restaurant/v1/restaurants/list/"
    response = api_client.get(url)
    assert response.status_code == HTTP_401_UNAUTHORIZED

#negative2
@pytest.mark.django_db
def test_list_restaurants_empty_list(api_client, auth_headers):
    Restaurant.objects.all().delete()
    url = "/api/restaurant/v1/restaurants/list/"
    response = api_client.get(url, **auth_headers)
    assert response.status_code == HTTP_200_OK
    assert response.data == []

#negative3
@pytest.mark.django_db
def test_list_restaurants_invalid_method(api_client, auth_headers):
    url = "/api/restaurant/v1/restaurants/list/"
    response = api_client.post(url, {}, **auth_headers)
    assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED

"""
Tests for GET /restaurants/assign-categories/
"""
@pytest.fixture
def categories(db):
    cat1 = Category.objects.create(name="Pizza")
    cat2 = Category.objects.create(name="Burger")
    return [cat1, cat2]

#positive
def test_assign_categories_success(api_client, restaurant, categories, auth_headers):
    url = "/api/restaurant/v1/restaurants/assign-categories/"
    category_ids = [c.id for c in categories]

    response = api_client.get(
        url,
        data = {
            "restaurant_ids": restaurant.ids,},
            **auth_headers
    )
    assert response.status_code == HTTP_200_OK
    assert restaurant.categories.count() == 2

#negative1
@pytest.mark.django_db
def test_assign_categories_no_ids(api_client, auth_headers):
    response = api_client.get(
        "/api/restaurant/v1/restaurants/assign-categories/",
        **auth_headers
    )
    assert response.status_code == HTTP_400_BAD_REQUEST

#negative2
@pytest.mark.django_db
def test_assign_categories_no_restaurant(api_client, owner, auth_headers):
    Restaurant.objects.filter(owner=owner).delete()
    response = api_client.get(
        "/api/restaurant/v1/restaurants/assign-categories/",
        data={"restaurant_ids": [1,2]},
        **auth_headers
    )
    assert response.status_code == HTTP_404_NOT_FOUND

#negative3
@pytest.mark.django_db
def test_assign_categories_unauthenticated(api_client):
    response = api_client.get(
        "/api/restaurant/v1/restaurants/assign-categories/",
        data={"restaurant_ids": [1,2]},
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED



"""
Tests for POST /restaurants/unassign-categories/
"""
#positive
@pytest.mark.django_db
def test_unassign_categories_success(api_client, restaurant, categories, auth_headers):
    restaurant.categories.set(categories)
    category_ids = [c.id for c in categories]

    response = api_client.post(
        "/api/restaurant/v1/restaurants/unassign-categories/",
        data={
            "restaurant_ids": [restaurant.id],
            "category_ids": category_ids,
        },
        **auth_headers
    )
    assert response.status_code == HTTP_200_OK
    assert restaurant.categories.count() == 1

#negative1
@pytest.mark.django_db
def test_unassign_categories_no_ids(api_client, auth_headers):
    response = api_client.post(
        "/api/restaurant/v1/restaurants/unassign-categories/",
        **auth_headers,
        data = {}
    )
    assert response.status_code == HTTP_400_BAD_REQUEST

#negative2
@pytest.mark.django_db
def test_unassign_categories_not_owner(api_client, restaurant, categories, auth_headers_other):
    restaurant.categories.set(categories)
    category_ids = [c.id for c in categories]

    response = api_client.post(
        "/api/restaurant/v1/restaurants/unassign-categories/",
        data={
            "restaurant_ids": [restaurant.id],
            "category_ids": category_ids,
        },
        **auth_headers_other
    )
    assert response.status_code == HTTP_403_FORBIDDEN

#negative3
@pytest.mark.django_db
def test_unassign_categories_unauthenticated(api_client):
    response = api.client.post(
        "/api/restaurant/v1/restaurants/unassign-categories/",
        data={
            "category_ids": [1],
        },
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED


"""
TEST FOR POST /restaurants/add-delivery
"""
from apps.restaurants.models import DeliveryLink
@pytest.fixture
def delivery_link(db, restaurant):
    return [
        DeliveryLink.objects.create(
            restaurant=restaurant,
            platform_name="Glovo",
            platform_url="http://delivery.test/link1"
        ),
        DeliveryLink.objects.create(
            restaurant=restaurant,
            platform_name="Wolt",
            platform_url="http://delivery.test/link2"
        ),
    ]

#positive
@pytest.mark.django_db
def test_add_delivery_success(api_client, auth_headers, restaurant, delivery_link):
    url = "/api/restaurant/v1/restaurants/add-delivery/"
    delivery_ids = [d.id for d in delivery_link]

    response = api_client.post(
        url,
        data={"delivery_ids": delivery_ids},
        **auth_headers
    )

    assert response.status_code == HTTP_200_OK

#negative1
@pytest.mark.django_db
def test_add_delivery_no_ids(api_client, auth_headers):
    response = api_client.post(
        "/api/restaurant/v1/restaurants/add-delivery/",
        data={},
        **auth_headers
    )
    assert response.status_code == HTTP_400_BAD_REQUEST

#negative2
@pytest.mark.django_db
def test_add_delivery_no_restaurant(api_client, auth_headers, owner):
    Restaurant.objects.filter(owner=owner).delete()

    response = api_client.post(
        "/api/restaurant/v1/restaurants/add-delivery/",
        data={"delivery_ids": [1]},
        **auth_headers
    )
    assert response.status_code == HTTP_404_NOT_FOUND

#negative3
@pytest.mark.django_db
def test_add_delivery_unauthenticated(api_client):
    response = api_client.post(
        "/api/restaurant/v1/restaurants/add-delivery/",
        data={"delivery_ids": [1]}
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED



"""
Tests for POST /restaurants/remove-delivery/
"""
#positive
@pytest.mark.django_db
def test_remove_delivery_success(api_client, auth_headers, restaurant, delivery_link):
    restaurant.delivery_methods.set(delivery_link)

    response = api_client.post(
        "/api/restaurant/v1/restaurants/remove-delivery/",
        data={"delivery_ids": [delivery_link[0].id]},
        **auth_headers
    )

    assert response.status_code == HTTP_200_OK

#negative1
@pytest.mark.django_db
def test_remove_delivery_no_ids(api_client, auth_headers):
    response = api_client.post(
        "/api/restaurant/v1/restaurants/remove-delivery/",
        data={},
        **auth_headers
    )
    assert response.status_code == HTTP_400_BAD_REQUEST

#negative2
@pytest.mark.django_db
def test_remove_delivery_not_owner(api_client, auth_headers_other, restaurant, delivery_link):
    restaurant.delivery_methods.set(delivery_link)

    response = api_client.post(
        "/api/restaurant/v1/restaurants/remove-delivery/",
        data={"delivery_ids": [delivery_link[0].id]},
        **auth_headers_other
    )
    assert response.status_code == HTTP_403_FORBIDDEN

#negative3
@pytest.mark.django_db
def test_remove_delivery_unauthenticated(api_client):
    response = api_client.post(
        "/api/restaurant/v1/restaurants/remove-delivery/",
        data={"delivery_ids": [1]}
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED

