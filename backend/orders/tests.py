from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from categories.models import Category
from products.models import Product
from orders.models import Order

class OrderBusinessLogicTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Gadget',
            price=500.00,
            stock=10,
            category=self.category
        )

        self.user1 = User.objects.create_user(
            username='buyer1',
            email='buyer1@test.com',
            password='Password123',
            role=User.Role.USER
        )

        self.user2 = User.objects.create_user(
            username='buyer2',
            email='buyer2@test.com',
            password='Password123',
            role=User.Role.USER
        )

        self.admin = User.objects.create_user(
            username='storeadmin',
            email='admin@test.com',
            password='AdminPassword123',
            role=User.Role.ADMIN,
            is_staff=True
        )

        self.orders_url = reverse('order_list_create')

    def test_stock_validation_insufficient_stock_rejected(self):
        self.client.force_authenticate(user=self.user1)
        # Attempt to order 15 items when only 10 exist
        res = self.client.post(self.orders_url, {
            "product_id": self.product.id,
            "quantity": 15
        }, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Verify product stock remained 10
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)
        # Verify no order was created
        self.assertEqual(Order.objects.count(), 0)

    def test_order_creation_stock_reduction_and_server_price_calculation(self):
        self.client.force_authenticate(user=self.user1)
        # Order 3 items at ₹500 each => Total should be ₹1500
        # Notice: Even if a frontend tries sending total_amount: 1, backend MUST ignore it and calculate ₹1500!
        res = self.client.post(self.orders_url, {
            "product_id": self.product.id,
            "quantity": 3,
            "total_amount": 10.00 # Fake frontend amount that must be ignored
        }, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.product.refresh_from_db()
        # Stock must be decremented 10 - 3 = 7
        self.assertEqual(self.product.stock, 7)

        # Server-side total calculated
        order = Order.objects.get(id=res.data['order']['id'])
        self.assertEqual(float(order.total_amount), 1500.00)
        self.assertEqual(order.status, 'Placed')

    def test_user_orders_isolation(self):
        # user1 creates an order
        self.client.force_authenticate(user=self.user1)
        self.client.post(self.orders_url, {"product_id": self.product.id, "quantity": 1}, format='json')

        # user2 creates an order
        self.client.force_authenticate(user=self.user2)
        self.client.post(self.orders_url, {"product_id": self.product.id, "quantity": 2}, format='json')

        # user1 listing orders should ONLY see 1 order (theirs)
        self.client.force_authenticate(user=self.user1)
        res1 = self.client.get(self.orders_url)
        self.assertEqual(len(res1.data), 1)
        self.assertEqual(res1.data[0]['customer']['username'], 'buyer1')

        # Admin listing orders should see ALL orders (2)
        self.client.force_authenticate(user=self.admin)
        res_admin = self.client.get(self.orders_url)
        self.assertEqual(len(res_admin.data), 2)

    def test_admin_can_update_order_status_user_cannot(self):
        self.client.force_authenticate(user=self.user1)
        order_res = self.client.post(self.orders_url, {"product_id": self.product.id, "quantity": 1}, format='json')
        order_id = order_res.data['order']['id']
        status_url = reverse('order_status_update', kwargs={'pk': order_id})

        # Regular user tries to update status -> 403 Forbidden
        res_user_patch = self.client.patch(status_url, {"status": "Completed"})
        self.assertEqual(res_user_patch.status_code, status.HTTP_403_FORBIDDEN)

        # Admin updates status -> 200 OK
        self.client.force_authenticate(user=self.admin)
        res_admin_patch = self.client.patch(status_url, {"status": "Completed"})
        self.assertEqual(res_admin_patch.status_code, status.HTTP_200_OK)
        order = Order.objects.get(id=order_id)
        self.assertEqual(order.status, 'Completed')
