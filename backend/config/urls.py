from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from accounts.urls import auth_urlpatterns, user_urlpatterns
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR.parent / 'frontend'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include((auth_urlpatterns, 'auth'))),
    path('api/users/', include((user_urlpatterns, 'users'))),
    path('api/categories/', include('categories.urls')),
    path('api/products/', include('products.urls')),
    path('api/orders/', include('orders.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Also optionally serve frontend static assets for single-command launch convenience
urlpatterns += [
    re_path(r'^(?!api/|admin/|media/)(?P<path>.*)$', serve, {
        'document_root': str(FRONTEND_DIR),
        'show_indexes': True
    }),
]
