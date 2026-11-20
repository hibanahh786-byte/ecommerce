from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    UserListView,
    UserProfileView
)

auth_urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', LoginView.as_view(), name='auth_login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
]

user_urlpatterns = [
    path('', UserListView.as_view(), name='user_list'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
]
