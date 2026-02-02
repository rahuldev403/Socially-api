from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from core import urls as core_urls

def health_check(request):
    return JsonResponse({"status": "ok", "message": "Server is running"})

urlpatterns = [
    path("", health_check, name="health_check"),
    path("admin/", admin.site.urls),
    path("api/auth/", include(core_urls.auth_urlpatterns)),
    path("api/", include(core_urls.posts_urlpatterns)),
]
