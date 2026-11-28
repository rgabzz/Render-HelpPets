from django.db import transaction
from denuncias.models import Denuncias, DenunciaFoto
from denuncias.serializers import DenunciasSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets,generics
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .filters import DenunciasFilter
from .permissions import DenunciasPermission
from midias.storage import enviar_fotos, checar_limite, criar_fotos

class DenunciasViewset(viewsets.ModelViewSet):
    serializer_class = DenunciasSerializer
    queryset = Denuncias.objects.all().prefetch_related('fotos')

    # multipart para enviar as fotos; JSON continua valendo (ex.: PATCH sem foto)
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    filter_backends = [DjangoFilterBackend]

    filterset_class = DenunciasFilter

    def perform_create(self, serializer):
        # bloqueia o usuario de poder colocar a denuncia ja com uma ong pre pronta, alem de proibir alguem de colocar outro id de usuario apra aquela denuncia
        arquivos = serializer.validated_data.pop('fotos')
        urls = enviar_fotos(arquivos, f'denuncias/{self.request.user.id}')
        with transaction.atomic():
            denuncia = serializer.save(usuario=self.request.user, ong=None, status='aberto')
            criar_fotos(DenunciaFoto, 'denuncia', denuncia, urls)

    def perform_update(self, serializer):
        # fotos enviadas no PUT/PATCH sao ADICIONADAS as que ja existem (limite total de 5)
        arquivos = serializer.validated_data.pop('fotos', [])
        denuncia = serializer.instance
        checar_limite(denuncia.fotos.count(), len(arquivos))
        urls = enviar_fotos(arquivos, f'denuncias/{denuncia.usuario_id or self.request.user.id}')
        with transaction.atomic():
            serializer.save()
            criar_fotos(DenunciaFoto, 'denuncia', denuncia, urls)

    permission_classes = [permissions.IsAuthenticated, DenunciasPermission]