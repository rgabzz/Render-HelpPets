from denuncias.models import Denuncias

from rest_framework import serializers

from midias.serializers import FotoSerializer, campo_fotos

class DenunciasSerializer(serializers.ModelSerializer):
    condicao = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[choice[0] for choice in Denuncias.CONDICAO_CHOICES]
        )
    )

    # ENTRADA: arquivos de imagem (multipart). SAIDA: lista [{id, url, ordem}].
    fotos = campo_fotos()

    class Meta:
        model = Denuncias
        fields = '__all__'
        read_only_fields = ['usuario']

    def validate(self, attrs):
        # Na criação é obrigatório mandar pelo menos 1 foto.
        if self.instance is None and not attrs.get('fotos'):
            raise serializers.ValidationError({'fotos': 'Envie pelo menos uma foto do animal.'})
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['fotos'] = FotoSerializer(instance.fotos.all(), many=True).data
        return data