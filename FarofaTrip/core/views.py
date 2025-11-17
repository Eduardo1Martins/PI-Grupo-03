from rest_framework import viewsets, status, permissions, filters
from django.utils.timezone import localdate
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Perfil, Evento
from .serializers import PerfilSerializer, EventoSerializer, RegisterSerializer, EmailOrUsernameTokenObtainPairSerializer

# LOGIN
class LoginView(TokenObtainPairView):
    serializer_class = EmailOrUsernameTokenObtainPairSerializer
    permission_classes = [AllowAny]

# REFRESH padrão
class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

# LOGOUT com blacklist
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh = request.data.get("refresh")
            if not refresh:
                return Response({"detail": "refresh token é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

# REGISTER
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        s = RegisterSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.save()
        return Response({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        }, status=status.HTTP_201_CREATED)

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Perfil.objects.select_related("user").all()
    serializer_class = PerfilSerializer
    permission_classes = [permissions.AllowAny]
    

class EventoViewSet(viewsets.ModelViewSet):
    serializer_class = EventoSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'cidade', 'local', 'descricao']
    ordering_fields = ['data', 'nome', 'cidade']
    ordering = ['data']

    def get_queryset(self):
        qs = Evento.objects.all().order_by('data')
        scope = (self.request.query_params.get('scope') or 'future').lower()
        if scope == 'future':
            qs = qs.filter(data__gte=localdate())
        elif scope == 'past':
            qs = qs.filter(data__lt=localdate())
        # scope=all -> sem filtro de data
        return qs