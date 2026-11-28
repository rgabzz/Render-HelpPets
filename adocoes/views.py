from adocoes.serializers import AnimalSerializer,AdocaoSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets,generics
from rest_framework import permissions
from .filters import AnimalFilters
from .permissions import AdocoesPermissions, AnimalPermissions
from django.db import transaction
from adocoes.models import Animal,Adocao,AnimalFoto
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from midias.storage import enviar_fotos, checar_limite, criar_fotos

class AnimalViewset(viewsets.ModelViewSet):
    serializer_class = AnimalSerializer
    queryset = Animal.objects.all().prefetch_related('fotos')

    # multipart para enviar as fotos; JSON continua valendo (ex.: PATCH sem foto)
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        ong = getattr(self.request.user, 'perfil_ONG', None) 
        arquivos = serializer.validated_data.pop('fotos')
        urls = enviar_fotos(arquivos, f'animais/{ong.id if ong else "admin"}')
        with transaction.atomic():
            animal = serializer.save(ong=ong)
            criar_fotos(AnimalFoto, 'animal', animal, urls)

    def perform_update(self, serializer):
        # fotos enviadas no PUT/PATCH sao ADICIONADAS as que ja existem (limite total de 5)
        arquivos = serializer.validated_data.pop('fotos', [])
        animal = serializer.instance
        checar_limite(animal.fotos.count(), len(arquivos))
        urls = enviar_fotos(arquivos, f'animais/{animal.ong_id}')
        with transaction.atomic():
            serializer.save()
            criar_fotos(AnimalFoto, 'animal', animal, urls)

    filter_backends = [DjangoFilterBackend]
    filterset_class = AnimalFilters

    permission_classes = [permissions.IsAuthenticated,AnimalPermissions]

class AdocaoViewset(viewsets.ModelViewSet):
    serializer_class = AdocaoSerializer
    queryset = Adocao.objects.all()

    def get_queryset(self):

            user = self.request.user
    
            ''' 
                Verificação criada para que nenhum usuário consiga acessar a lista com todos as adocoes
            - Sem essa verificação a rota /adocoes/ fica exposta e todos conseguem acessar as informações dos usuários
            - Com ela apenas admins conseguem ver isso, caso o usuário comum tente acessar, encontrará apenas suas adocões
    
            '''
    
            if user.is_superuser:
                return Adocao.objects.all().order_by('id')

            if user.tipo == 'ong':
                ong_perfil  = getattr(user, 'perfil_ONG', None)

                if ong_perfil  is None:
                    return Adocao.objects.none()

                return Adocao.objects.filter(ong=ong_perfil )
                 
            
            return Adocao.objects.filter(usuario=user)

    def perform_create(self, serializer):
            ong = getattr(self.request.user, 'perfil_ONG', None) 
            serializer.save(ong=ong)

    permission_classes = [permissions.IsAuthenticated,AdocoesPermissions]