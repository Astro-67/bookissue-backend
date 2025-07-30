from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserListSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer
)
from .permissions import IsOwnerOrReadOnly, IsStaffOrICT, CanManageTickets


class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Register a new user",
        responses={
            201: openapi.Response(
                description="User registered successfully",
                examples={
                    "application/json": {
                        "user": {
                            "id": 1,
                            "email": "student@example.com",
                            "full_name": "John Doe",
                            "role": "student"
                        },
                        "tokens": {
                            "refresh": "refresh_token_here",
                            "access": "access_token_here"
                        },
                        "message": "User registered successfully"
                    }
                }
            ),
            400: "Bad Request - Validation errors"
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    """
    User login endpoint
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Login with email and password",
        request_body=UserLoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "user": {
                            "id": 1,
                            "email": "student@example.com",
                            "full_name": "John Doe",
                            "role": "student"
                        },
                        "tokens": {
                            "refresh": "refresh_token_here",
                            "access": "access_token_here"
                        },
                        "message": "Login successful"
                    }
                }
            ),
            400: "Bad Request - Invalid credentials"
        }
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    """
    User logout endpoint
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update user profile
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """
    Change user password
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    """
    List all users (for staff and ICT)
    """
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrICT]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email', 'student_id']
    ordering_fields = ['created_at', 'first_name', 'last_name']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = User.objects.all()
        role = self.request.query_params.get('role', None)
        department = self.request.query_params.get('department', None)
        is_active = self.request.query_params.get('is_active', None)

        if role is not None:
            queryset = queryset.filter(role=role)
        if department is not None:
            queryset = queryset.filter(department__icontains=department)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete user details (for staff, ICT, and super admins)
    """
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrICT]
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserProfileSerializer

    def perform_destroy(self, instance):
        # Prevent super admins from deleting themselves
        if instance == self.request.user:
            raise ValidationError("You cannot delete your own account.")
        instance.delete()


class UserCreateView(generics.CreateAPIView):
    """
    Create a new user (for super admins)
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrICT]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_current_user(request):
    """
    Get current authenticated user
    """
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, CanManageTickets])
def get_user_stats(request):
    """
    Get user statistics (for staff and ICT)
    """
    total_users = User.objects.count()
    students = User.objects.filter(role='student').count()
    staff = User.objects.filter(role='staff').count()
    ict = User.objects.filter(role='ict').count()
    active_users = User.objects.filter(is_active=True).count()
    
    return Response({
        'total_users': total_users,
        'students': students,
        'staff': staff,
        'ict': ict,
        'active_users': active_users,
        'inactive_users': total_users - active_users
    }, status=status.HTTP_200_OK)
