from rest_framework import generics, permissions, filters
from django.db.models import Q
from .models import Product
from .serializers import ProductSerializer
from accounts.permissions import IsAdminRole

class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [IsAdminRole()]

    def get_queryset(self):
        queryset = Product.objects.select_related('category').all().order_by('-created_at')
        
        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # Search by product name
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(category__name__icontains=search))

        # In-stock filter
        in_stock = self.request.query_params.get('in_stock')
        if in_stock and in_stock.lower() in ('true', '1'):
            queryset = queryset.filter(stock__gt=0)

        return queryset

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [IsAdminRole()]
