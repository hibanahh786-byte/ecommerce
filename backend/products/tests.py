from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from categories.models import Category
from products.models import Product

class ProductApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.list_url = reverse('product_list_create')
        self.category = Category.objects.create(name='Smartphones')
        self.admin = User.objects.create_user(
            username='admin_prod',
            email='admin_prod@test.com',
            password='Password123',
            role=User.Role.ADMIN,
            is_staff=True
        )
        self.user = User.objects.create_user(
            username='user_prod',
            email='user_prod@test.com',
            password='Password123',
            role=User.Role.USER
        )

    def test_anonymous_can_view_products(self):
        Product.objects.create(name='Phone 1', price=1000, stock=5, category=self.category)
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_filter_and_search_products(self):
        cat2 = Category.objects.create(name='Laptops')
        Product.objects.create(name='Gaming Laptop', price=50000, stock=2, category=cat2)
        Product.objects.create(name='Smartphone X', price=20000, stock=4, category=self.category)

        # Filter by category
        res = self.client.get(f"{self.list_url}?category={cat2.id}")
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], 'Gaming Laptop')

        # Search by query
        res2 = self.client.get(f"{self.list_url}?search=Laptop")
        self.assertEqual(len(res2.data), 1)

    def test_regular_user_cannot_create_product(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "name": "Hacked Product",
            "price": 10.0,
            "stock": 100,
            "category_id": self.category.id
        }
        res = self.client.post(self.list_url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_and_update_product(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            "name": "Admin Product",
            "price": 1299.99,
            "stock": 50,
            "category_id": self.category.id
        }
        res = self.client.post(self.list_url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        product_id = res.data['id']

        # Update stock
        detail_url = reverse('product_detail', kwargs={'pk': product_id})
        update_res = self.client.put(detail_url, {
            "name": "Admin Product",
            "price": 1299.99,
            "stock": 75,
            "category_id": self.category.id
        })
        self.assertEqual(update_res.status_code, status.HTTP_200_OK)
        prod = Product.objects.get(id=product_id)
        self.assertEqual(prod.stock, 75)
