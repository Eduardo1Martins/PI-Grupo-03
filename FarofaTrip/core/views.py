from rest_framework import viewsets, status, permissions, filters
from django.utils.timezone import localdate
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action

from .models import Perfil, Evento, Pedido
from .serializers import (
    PerfilSerializer,
    EventoSerializer,
    RegisterSerializer,
    EmailOrUsernameTokenObtainPairSerializer,
    PedidoSerializer,
    ChangePasswordSerializer
)


# LOGIN
class LoginView(TokenObtainPairView):
    """
    Endpoint de login JWT, usando o serializer customizado
    que aceita username ou e-mail.
    """
    serializer_class = EmailOrUsernameTokenObtainPairSerializer
    permission_classes = [AllowAny]


# REFRESH padrão
class RefreshView(TokenRefreshView):
    """
    Endpoint padrão do SimpleJWT para renovar o access token
    a partir de um refresh token válido.
    """
    permission_classes = [AllowAny]


# LOGOUT com blacklist
class LogoutView(APIView):
    """
    Endpoint de logout: recebe o refresh token e o coloca na blacklist.
    Isso invalida o token para usos futuros.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh = request.data.get("refresh")
            if not refresh:
                return Response(
                    {"detail": "refresh token é obrigatório."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken(refresh)
            token.blacklist()
            # 205 Reset Content indica que o cliente deve "resetar" o estado
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            # Em caso de erro (token inválido, etc.)
            return Response(status=status.HTTP_400_BAD_REQUEST)


# REGISTER
class RegisterView(APIView):
    """
    Endpoint de registro de novos usuários.
    Usa o RegisterSerializer para criar User + Perfil.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        s = RegisterSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.save()
        # Retorna um payload enxuto, sem expor senha nem dados sensíveis
        return Response(
            {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
            },
            status=status.HTTP_201_CREATED,
        )
    

class ChangePasswordView(APIView):
    """
    Endpoint para troca de senha do usuário autenticado.

    Método:
    - POST /auth/change-password/
      Body JSON:
      {
        "old_password": "senha_atual",
        "new_password": "nova_senha",
        "new_password_confirm": "nova_senha"
      }
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Opcional: frontend pode, depois disso,
        # apagar o token do localStorage e forçar novo login.
        return Response(
            {"detail": "Senha alterada com sucesso."},
            status=status.HTTP_200_OK,
        )



class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet CRUD para Perfil de usuário.

    - Usa PerfilSerializer, que embute dados do User.
    - Permission AllowAny pode ser ajustada futuramente para regras de acesso.
    """
    queryset = Perfil.objects.select_related("user").all()
    serializer_class = PerfilSerializer
    permission_classes = [permissions.AllowAny]

    @action(
        detail=False,
        methods=["get", "patch"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="me",
    )
    def me(self, request):
        """
        Retorna ou atualiza o perfil do usuário autenticado.

        - GET /usuarios/me/  -> dados do perfil do usuário logado
        - PATCH /usuarios/me/ -> atualiza somente os campos enviados
          (ex.: first_name, last_name, email, telefone, endereco, etc.)
        """
        try:
            perfil = Perfil.objects.select_related("user").get(user=request.user)
        except Perfil.DoesNotExist:
            return Response(
                {"detail": "Perfil não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.method.lower() == "patch":
            serializer = self.get_serializer(
                perfil, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        # GET
        serializer = self.get_serializer(perfil)
        return Response(serializer.data)



class EventoViewSet(viewsets.ModelViewSet):
    """
    ViewSet CRUD para Evento.

    Inclui:
    - filtros de busca (nome, cidade, local, descrição)
    - ordenação por data, nome ou cidade
    - filtro 'scope' (future/past) por query param
    """
    serializer_class = EventoSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'cidade', 'local', 'descricao']
    ordering_fields = ['data', 'nome', 'cidade']
    ordering = ['data']

    def get_queryset(self):
        """
        Retorna eventos filtrados por escopo temporal:

        - scope=future (padrão): eventos com data >= hoje.
        - scope=past: eventos com data < hoje.
        """
        qs = Evento.objects.all().order_by('data')
        scope = (self.request.query_params.get('scope') or 'future').lower()
        if scope == 'future':
            qs = qs.filter(data__gte=localdate())
        elif scope == 'past':
            qs = qs.filter(data__lt=localdate())
        return qs


class PedidoViewSet(viewsets.ModelViewSet):
    """
    ViewSet CRUD para Pedido.

    - Permite leitura para todos.
    - Criação/edição requer autenticação (IsAuthenticatedOrReadOnly).
    - get_queryset() restringe a listagem aos pedidos do usuário logado.
    """
    serializer_class = PedidoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Retorna pedidos do usuário autenticado, incluindo:

        - select_related('usuario') para otimizar acesso ao usuário.
        - prefetch_related('itens__evento') para otimizar itens e eventos.
        """
        qs = Pedido.objects.all().select_related("usuario").prefetch_related(
            "itens__evento"
        )

        user = self.request.user
        if user.is_authenticated:
            return qs.filter(usuario=user)

        # Usuário anônimo não deve ver pedidos
        return qs.none()
