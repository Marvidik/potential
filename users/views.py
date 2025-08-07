# views.py
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view,permission_classes,parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import UserInfo,Consultation,Notification
from .serializers import ConsultationSerializer,NotificationSerializer,UserUpdateSerializer,UserDashboardSerializer
from rest_framework.parsers import MultiPartParser, FormParser

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


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])  # Support image upload
def update_user_account(request):
    user = request.user
    serializer = UserUpdateSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Account updated successfully", "user": serializer.data}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_consultation(request):
    data = request.data.copy()
    data['user'] = request.user.id  # Attach logged-in user

    serializer = ConsultationSerializer(data=data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response({"message": "Consultation created successfully", "consultation": serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_consultations(request):
    consultations = Consultation.objects.filter(user=request.user)
    serializer = ConsultationSerializer(consultations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_notifications(request):
    notifications = Notification.objects.all().order_by('-date')
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_dashboard(request):
    serializer = UserDashboardSerializer(request.user, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)





@api_view(['DELETE'])
def delete_notification(request, id):
    try:
        notification = Notification.objects.get(id=id)
        notification.delete()
        return Response({"message": "Notification deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except Notification.DoesNotExist:
        return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def delete_consultation(request, id):
    try:
        consultation = Consultation.objects.get(id=id)
        consultation.delete()
        return Response({"message": "Consultation deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except Consultation.DoesNotExist:
        return Response({"error": "Consultation not found"}, status=status.HTTP_404_NOT_FOUND)