from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.user.models import CustomUser
from django.contrib.auth import get_user_model

def auth_headers_for_user(user: CustomUser) -> dict:
    refresh = RefreshToken.for_user(user)
    return {
        'HTTP_AUTHORIZATION': f'Bearer {str(refresh.access_token)}',
    }

class UserAPITests(APITestCase):
    def setUp(self):
        self.user_data = {
            "name": "Alice:",
            "email": "alice@gmail.com",
            "password": "StrongPassw0rd!",
        }
        #create existing user
        self.existing_user = CustomUser.objects.create_user(
            email="exist@gmail.com",
            name="existing user",
            password="Exist",
        )
        self.login_url = "api/user/v1/users/login/"
        self.register_url = "api/user/v1/users/register/"
        self.list_url = "api/user/v1/users/list"
        self.retrieve_url_template = "api/user/v1/users/{pk}/"
        self.logout_url = "api/user/v1/users/logout/"

    def test_register_create_user_and_returns_tokkens(self):
        resp= self.client.post(self.register_url, data=self.user_data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)
        self.assertTrue(CustomUser.objects.filter(email=self.user_data["email"]).exists())
    def test_login_with_valid_credentials_returns_tokens(self):
        # ensure user exists
        user = CustomUser.objects.create_user(
            email="loginuser@example.com", name="Login User", password="loginpass123"
        )
        resp = self.client.post(
            self.login_url,
            data={"email": "loginuser@example.com", "password": "loginpass123"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)
        self.assertEqual(resp.data["email"], "loginuser@example.com")

    def test_login_with_wrong_credentials_fails(self):
        resp = self.client.post(
            self.login_url,
            data={"email": "doesnotexist@example.com", "password": "nopass"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST) 

    def test_users_list_requires_authentication(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        headers = auth_headers_for_user(self.existing_user)
        resp = self.client.get(self.list_url, **headers)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("users", resp.data)
        self.assertTrue(len(resp.data["users"]) >= 1)

    def test_retrieve_user_by_pk(self):
        headers = auth_headers_for_user(self.existing_user)
        url = self.retrieve_url_template.format(pk=self.existing_user.pk)
        resp = self.client.get(url, **headers)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["id"], self.existing_user.id)
        self.assertEqual(resp.data["email"], self.existing_user.email)

    def test_logout_requires_refresh_and_blacklists(self):
        user = CustomUser.objects.create_user(
            email="logoutuser@example.com", name="Logout User", password="logoutpass123"
        )
        refresh = RefreshToken.for_user(user)
        headers = auth_headers_for_user(user)
        resp = self.client.post(self.logout_url, data={}, format="json", **headers)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        resp = self.client.post(self.logout_url, data={"refresh": "invalidtoken"}, format="json", **headers)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        resp = self.client.post(self.logout_url, data={"refresh": str(refresh)}, format="json", **headers)
        self.assertEqual(resp.status_code, status.HTTP_205_RESET_CONTENT)