from denuncias.models import Denuncias

from rest_framework import serializers

class DenunciasSerializer(serializers.ModelSerializer):
    condicao = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[choice[0] for choice in Denuncias.CONDICAO_CHOICES]
        )
    )

    foto = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Denuncias
        fields = '__all__'
        read_only_fields = ['usuario','midia_path']

    def validate(self, attrs):
        if self.instance is None and 'foto' not in attrs:
            raise serializers.ValidationError({'foto': 'Envie a foto do animal.'})
        return attrs
