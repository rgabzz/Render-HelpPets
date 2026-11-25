from denuncias.models import Denuncias
from denuncias.serializers import DenunciasSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets,generics
from rest_framework import permissions
from .filters import DenunciasFilter
from .permissions import DenunciasPermission
from midias.storage import enviar_foto
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

class DenunciasViewset(viewsets.ModelViewSet):
    serializer_class = DenunciasSerializer
    queryset = Denuncias.objects.all()

    # multipart para enviar a foto; JSON continua valendo (ex.: PATCH sem foto)
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    filter_backends = [DjangoFilterBackend]

    filterset_class = DenunciasFilter

    def perform_create(self, serializer):
        # bloqueia o usuario de poder colocar a denuncia ja com uma ong pre pronta, alem de proibir alguem de colocar outro id de usuario apra aquela denuncia
        foto = serializer.validated_data.pop('foto')
        url = enviar_foto(foto, self.request.user.id)
        serializer.save(usuario=self.request.user, ong=None, status='aberto', midia_path=url)

    def perform_update(self, serializer):
        foto = serializer.validated_data.pop('foto', None)
        if foto is not None:
            serializer.save(midia_path=enviar_foto(foto, self.request.user.id))
        else:
            serializer.save()

    permission_classes = [permissions.IsAuthenticated, DenunciasPermission]
