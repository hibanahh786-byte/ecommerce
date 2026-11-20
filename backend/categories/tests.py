from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from categories.models import Category

class CategoryApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.list_url = reverse('category_list_create')
        self.admin = User.objects.create_user(
            username='admin_cat',
            email='admin_cat@test.com',
            password='Password123',
            role=User.Role.ADMIN,
            is_staff=True
        )
        self.user = User.objects.create_user(
            username='user_cat',
            email='user_cat@test.com',
            password='Password123',
            role=User.Role.USER
        )

    def test_anonymous_can_list_categories(self):
        Category.objects.create(name='Test Category')
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_regular_user_cannot_create_category(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(self.list_url, {"name": "New Category"})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_and_delete_category(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.post(self.list_url, {"name": "New Category"})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        cat_id = res.data['id']

        detail_url = reverse('category_detail', kwargs={'pk': cat_id})
        del_res = self.client.delete(detail_url)
        self.assertEqual(del_res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=cat_id).exists())
