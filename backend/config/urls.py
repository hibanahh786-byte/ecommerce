from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.shortcuts import redirect
from accounts.urls import auth_urlpatterns, user_urlpatterns
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR.parent / 'frontend'

def root_redirect(request):
    return redirect('/index.html')

def admin_root_redirect(request):
    return redirect('/admin/dashboard.html')

urlpatterns = [
    # Built-in Django Admin Site
    path('django-admin/', admin.site.urls),

    # Redirects for convenient root navigation
    path('', root_redirect),
    path('admin/', admin_root_redirect),

    # REST APIs
    path('api/auth/', include((auth_urlpatterns, 'auth'))),
    path('api/users/', include((user_urlpatterns, 'users'))),
    path('api/categories/', include('categories.urls')),
    path('api/products/', include('products.urls')),
    path('api/orders/', include('orders.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve all custom frontend static assets & admin HTML pages
urlpatterns += [
    re_path(r'^(?!api/|django-admin/|media/)(?P<path>.*)$', serve, {
        'document_root': str(FRONTEND_DIR),
        'show_indexes': True
    }),
]
