from rest_framework import status, viewsets, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .models import User, UserRole, Brand
from .serializers import UserSerializer, UserCreateSerializer, LoginSerializer, BrandSerializer
from .permissions import IsBrandOwner, CanManageUsers

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
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
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserManagementViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [CanManageUsers]

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.all()
        if user.brand and not user.is_superuser:
            queryset = queryset.filter(brand=user.brand)
        return queryset.order_by('-date_joined')

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def perform_create(self, serializer):
        # Automatically assign brand if not explicitly provided
        user = self.request.user
        brand = serializer.validated_data.get('brand') or user.brand
        serializer.save(brand=brand)
