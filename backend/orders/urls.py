from django.urls import path
from .views import (
    OrderListCreateView,
    OrderDetailView,
    OrderStatusUpdateView,
    DashboardStatsView
)

urlpatterns = [
    path('', OrderListCreateView.as_view(), name='order_list_create'),
    path('dashboard-stats/', DashboardStatsView.as_view(), name='order_dashboard_stats'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('<int:pk>/status/', OrderStatusUpdateView.as_view(), name='order_status_update'),
]
