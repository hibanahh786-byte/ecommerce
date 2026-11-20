from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Q
from .models import Order
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderStatusUpdateSerializer
)
from accounts.models import User
from accounts.permissions import IsAdminRole, IsOwnerOrAdmin
from products.models import Product
from categories.models import Category

class OrderListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN' or user.is_staff or user.is_superuser:
            queryset = Order.objects.select_related('user').prefetch_related('items__product').all()
        else:
            queryset = Order.objects.filter(user=user).select_related('user').prefetch_related('items__product')

        status_param = self.request.query_params.get('status')
        if status_param in ['Placed', 'Completed']:
            queryset = queryset.filter(status=status_param)

        search = self.request.query_params.get('search', '').strip()
        if search:
            if search.isdigit():
                queryset = queryset.filter(
                    Q(id=int(search)) |
                    Q(user__username__icontains=search) |
                    Q(user__email__icontains=search) |
                    Q(items__product__name__icontains=search)
                ).distinct()
            else:
                queryset = queryset.filter(
                    Q(user__username__icontains=search) |
                    Q(user__email__icontains=search) |
                    Q(items__product__name__icontains=search)
                ).distinct()

        return queryset.order_by('-created_at')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        output_serializer = OrderSerializer(order, context={'request': request})
        return Response({
            "message": "Order placed successfully!",
            "order": output_serializer.data
        }, status=status.HTTP_201_CREATED)

class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.select_related('user').prefetch_related('items__product').all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

class OrderStatusUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [IsAdminRole]
    http_method_names = ['patch']

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        full_order = OrderSerializer(order, context={'request': request})
        return Response({
            "message": f"Order #{order.id} status updated to '{order.status}'.",
            "order": full_order.data
        }, status=status.HTTP_200_OK)

class DashboardStatsView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        total_products = Product.objects.count()
        total_categories = Category.objects.count()
        total_orders = Order.objects.count()
        total_users = User.objects.filter(role=User.Role.USER).count()
        
        # Total revenue from Completed orders
        revenue_agg = Order.objects.filter(status='Completed').aggregate(total=Sum('total_amount'))
        total_revenue = float(revenue_agg['total'] or 0.0)

        # Pending orders
        placed_orders = Order.objects.filter(status='Placed').count()

        return Response({
            "total_products": total_products,
            "total_categories": total_categories,
            "total_orders": total_orders,
            "total_users": total_users,
            "total_revenue": total_revenue,
            "placed_orders": placed_orders,
        }, status=status.HTTP_200_OK)
