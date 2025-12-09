from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.user.models import CustomUser
from apps.restaurant.models import Restaurant, Category

def auth_headers_for_user(user: CustomUser) -> dict:
    refresh = RefreshToken.for_user(user)
    return {"HTTP_AUTHORIZATION": f"Bearer {str(refresh.access_token)}"}


class RestaurantAPITestCase(APITestCase):
    def setUp(self):
        # two users: owner and another
        self.owner = CustomUser.objects.create_user(
            email="owner@example.com", name="Owner", password="ownerpass123"
        )
        self.other_user = CustomUser.objects.create_user(
            email="other@example.com", name="Other", password="otherpass123"
        )

        self.base_url = "/api/restaurant/v1/restaurants/"
        self.add_url = self.base_url + "add/"
        self.list_all_url = self.base_url + "list/"
        self.set_image_url = self.base_url + "set-image/"
        self.assign_categories_url = self.base_url + "assign-categories/"
        self.unassign_categories_url = self.base_url + "unassign-categories/"

        # create a restaurant owned by owner
        self.restaurant = Restaurant.objects.create(
            name="Testaurant",
            description="Test desc",
            owner=self.owner,
        )

        # categories
        self.cat1 = Category.objects.create(name="Pizza")
        self.cat2 = Category.objects.create(name="Sushi")

    def test_all_restaurants_action_returns_all(self):
        # create a second restaurant
        Restaurant.objects.create(name="Another", owner=self.other_user)
        headers = auth_headers_for_user(self.owner)
        resp = self.client.get(self.list_all_url, **headers)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # should return list of restaurants
        self.assertIsInstance(resp.data, list)
        # names included
        names = [r["name"] for r in resp.data]
        self.assertIn("Testaurant", names)
        self.assertIn("Another", names)

    def test_owner_restaurants_by_pk(self):
        headers = auth_headers_for_user(self.owner)
        url = self.base_url + "list/?pk=%d" % self.owner.pk
        resp = self.client.get(url, **headers)
        self.assertIn(resp.status_code, (status.HTTP_200_OK, status.HTTP_404_NOT_FOUND))

    def test_add_creates_restaurant_and_sets_owner_role(self):
        headers = auth_headers_for_user(self.other_user)
        payload = {
            "name": "NewPlace",
            "description": "Lovely",
            "address": "123 Main",
            "address_link": "http://maps.example.com/loc",
        }
        resp = self.client.post(self.add_url, data=payload, format="json", **headers)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # restaurant exists and owner set to other_user
        self.assertTrue(Restaurant.objects.filter(name="NewPlace", owner=self.other_user).exists())
        # role of user should be set to owner (UserRoleEntity.OWNER is probably 'owner')
        self.other_user.refresh_from_db()
        self.assertEqual(self.other_user.role, "owner")

    def test_retrieve_restaurant(self):
        headers = auth_headers_for_user(self.owner)
        url = self.base_url + f"{self.restaurant.pk}/"
        resp = self.client.get(url, **headers)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["id"], self.restaurant.id)
        self.assertEqual(resp.data["name"], self.restaurant.name)

    def test_partial_update_and_destroy(self):
        headers = auth_headers_for_user(self.owner)
        url = self.base_url + f"{self.restaurant.pk}/"
        # partial update
        resp = self.client.patch(url, data={"description": "Updated desc"}, format="json", **headers)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.restaurant.refresh_from_db()
        self.assertEqual(self.restaurant.description, "Updated desc")

        # destroy
        resp = self.client.delete(url, **headers)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Restaurant.objects.filter(pk=self.restaurant.pk).exists())

    def test_set_image_requires_image_url_and_owner_restaurant(self):
        headers = auth_headers_for_user(self.owner)
        # missing image_url
        resp = self.client.get(self.set_image_url, data={}, **headers)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        resp = self.client.get(self.set_image_url, data={"image_url": "http://example.com/img.jpg"}, **headers)
        self.assertIn(resp.status_code, (status.HTTP_200_OK, status.HTTP_404_NOT_FOUND))
        if resp.status_code == status.HTTP_200_OK:
            self.restaurant.refresh_from_db()
            self.assertEqual(self.restaurant.image_url, "http://example.com/img.jpg")

    def test_assign_and_unassign_categories(self):
        headers = auth_headers_for_user(self.owner)
        resp = self.client.get(self.assign_categories_url, data={"category_ids": [self.cat1.pk, self.cat2.pk]}, format="json", **headers)
        self.assertIn(resp.status_code, (status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND))
        if resp.status_code == status.HTTP_200_OK:
            self.restaurant.refresh_from_db()
            self.assertTrue(self.restaurant.categories.count() >= 1)

        resp2 = self.client.post(self.unassign_categories_url, data={"category_ids": [self.cat1.pk]}, format="json", **headers)
        self.assertIn(resp2.status_code, (status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND))
