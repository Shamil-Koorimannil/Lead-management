from rest_framework import status, viewsets, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .models import User, UserRole, Brand
from .serializers import (
    UserSerializer, UserCreateSerializer, LoginSerializer, BrandSerializer, BrandSettingsSerializer
)
from .permissions import IsBrandOwner, CanManageUsers

from rest_framework.throttling import AnonRateThrottle

class LoginRateThrottle(AnonRateThrottle):
    scope = 'login'

class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user, context={'request': request}).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'detail': 'Logout completed.'}, status=status.HTTP_200_OK)

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserManagementViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [CanManageUsers]

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.all()
        if user.brand and not user.is_superuser:
            queryset = queryset.filter(brand=user.brand)
        elif not user.is_superuser:
            return User.objects.none()
        return queryset.order_by('-date_joined')

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_superuser:
            brand = serializer.validated_data.get('brand') or user.brand
        else:
            brand = user.brand
        serializer.save(brand=brand)

    def perform_update(self, serializer):
        user = self.request.user
        if not user.is_superuser:
            serializer.save(brand=user.brand)
        else:
            serializer.save()

class SettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.brand and not user.is_superuser:
            return Response({'detail': 'User not associated with a Brand.'}, status=status.HTTP_400_BAD_REQUEST)

        brand = user.brand
        if user.is_superuser and not brand:
            brand = Brand.objects.first()

        if not brand:
            return Response({'detail': 'No active brand found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = BrandSettingsSerializer(brand)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        user = request.user
        if not (user.role == UserRole.BRAND_OWNER or user.is_superuser):
            return Response({'detail': 'Only Brand Owners can modify brand settings.'}, status=status.HTTP_403_FORBIDDEN)

        if not user.brand and not user.is_superuser:
            return Response({'detail': 'User not associated with a Brand.'}, status=status.HTTP_400_BAD_REQUEST)

        brand = user.brand
        if user.is_superuser and not brand:
            brand = Brand.objects.first()

        if not brand:
            return Response({'detail': 'No active brand found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = BrandSettingsSerializer(brand, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        brand = serializer.save()
        return Response(BrandSettingsSerializer(brand).data, status=status.HTTP_200_OK)
