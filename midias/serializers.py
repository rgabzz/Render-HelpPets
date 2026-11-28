from rest_framework import serializers

from midias.storage import MAX_FOTOS


class FotoSerializer(serializers.Serializer):
    """Como a foto aparece nas respostas: {id, url, ordem}."""
    id = serializers.IntegerField(read_only=True)
    url = serializers.CharField(source='midia_path', read_only=True)
    ordem = serializers.IntegerField(read_only=True)


def campo_fotos():
    """Campo de ENTRADA: várias imagens (multipart, campo 'fotos' repetido)."""
    return serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        allow_empty=False,
        max_length=MAX_FOTOS,
    )