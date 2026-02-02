from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from core.authentication import CsrfExemptSessionAuthentication

# signup api
@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def signup_view(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Username and password are required"}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=400)

    user = User.objects.create_user(username=username, password=password)
    login(request, user)
    return Response({"message": "Account created successfully"})

# login api
@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)

    if user is None:
        return Response({"error": "Invalid credentials"}, status=400)

    login(request, user)
    return Response({"message": "Logged in"})

# logout api
@api_view(["POST"])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([AllowAny])
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return Response({"message": "Logged out"})

# who am i api
@api_view(["GET"])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([AllowAny])
def me_view(request):
    if not request.user.is_authenticated:
        return Response({"error": "Not authenticated"}, status=401)
    
    return Response({
        "id": request.user.id,
        "username": request.user.username,
    })
