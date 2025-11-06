from rest_framework import viewsets
from .models import Usuario, Evento
from .serializers import UsuarioSerializer, EventoSerializer


# View USERS

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer