# views.py
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import UserInfo

@api_view(['POST'])
def register(request):
    email = request.data.get('email')
    password = request.data.get('password')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    phone_number = request.data.get('phone_number')
    address = request.data.get('address')

    # Validate fields
    if not all([email, password, first_name, last_name, phone_number, address]):
        return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if email exists
    if User.objects.filter(username=email).exists():
        return Response({"error": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)

    # Create User
    user = User.objects.create_user(
        username=email,  # email used as username
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )

    # Create UserInfo
    UserInfo.objects.create(
        user=user,
        phone_number=phone_number,
        address=address
    )

    # Create token
    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        "message": "User registered successfully.",
        "token": token.key,
        "user": {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": phone_number,
            "address": address
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    # Authenticate
    user = authenticate(username=email, password=password)
    if user is None:
        return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)

    # Get or create token
    token, _ = Token.objects.get_or_create(user=user)

    # Get user info
    user_info = UserInfo.objects.filter(user=user).first()

    return Response({
        "message": "Login successful.",
        "token": token.key,
        "user": {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user_info.phone_number if user_info else "",
            "address": user_info.address if user_info else ""
        }
    }, status=status.HTTP_200_OK)
