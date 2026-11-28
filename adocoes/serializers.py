from adocoes.models import Animal,Adocao

from rest_framework import serializers

from midias.serializers import FotoSerializer, campo_fotos

class AnimalSerializer(serializers.ModelSerializer):
    # ENTRADA: arquivos de imagem (multipart). SAIDA: lista [{id, url, ordem}].
    fotos = campo_fotos()

    class Meta:
        model = Animal
        fields = '__all__'
        read_only_fields = ['ong']

    def validate(self, attrs):
        # No cadastro do animal é obrigatório mandar pelo menos 1 foto.
        if self.instance is None and not attrs.get('fotos'):
            raise serializers.ValidationError({'fotos': 'Envie pelo menos uma foto do animal.'})
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['fotos'] = FotoSerializer(instance.fotos.all(), many=True).data
        return data
    
class AdocaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adocao
        fields = '__all__'
        read_only_fields = ['ong']