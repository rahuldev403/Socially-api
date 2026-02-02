from django.contrib import admin
from django.urls import path, include
from core import urls as core_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include(core_urls.auth_urlpatterns)),
    path("api/", include(core_urls.posts_urlpatterns)),
]
