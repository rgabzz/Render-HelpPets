import io
import uuid

import requests
from django.conf import settings
from PIL import Image, ImageOps, UnidentifiedImageError
from rest_framework import serializers

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_DIMENSAO = 1600                  # lado maior, em pixels
QUALIDADE_WEBP = 82
Image.MAX_IMAGE_PIXELS = 50_000_000


def enviar_foto(arquivo, user_id):
    """Otimiza a foto, envia ao Supabase Storage e devolve a URL pública."""
    if arquivo.size > MAX_UPLOAD_BYTES:
        raise serializers.ValidationError('Imagem maior que 10 MB.')
    if not (settings.SUPABASE_URL and settings.SUPABASE_SECRET_KEY):
        raise serializers.ValidationError('Storage de imagens não configurado no servidor.')

    try:
        arquivo.seek(0)
        img = Image.open(arquivo)
        img = ImageOps.exif_transpose(img)
        img = img.convert('RGB')
    except (UnidentifiedImageError, OSError):
        raise serializers.ValidationError('Arquivo não é uma imagem válida.')

    img.thumbnail((MAX_DIMENSAO, MAX_DIMENSAO))
    buf = io.BytesIO()
    img.save(buf, format='WEBP', quality=QUALIDADE_WEBP, method=6)  # descarta EXIF/GPS

    caminho = f'{user_id}/{uuid.uuid4().hex}.webp'
    try:
        resp = requests.post(
            f'{settings.SUPABASE_URL}/storage/v1/object/{settings.SUPABASE_BUCKET}/{caminho}',
            headers={
                'apikey': settings.SUPABASE_SECRET_KEY,
                'Content-Type': 'image/webp',
                'Cache-Control': 'max-age=31536000',
            },
            data=buf.getvalue(),
            timeout=20,
        )
    except requests.RequestException:
        raise serializers.ValidationError('Não foi possível enviar a foto agora. Tente de novo.')

    if resp.status_code not in (200, 201):
        raise serializers.ValidationError('Falha ao salvar a foto no storage.')

    return f'{settings.SUPABASE_URL}/storage/v1/object/public/{settings.SUPABASE_BUCKET}/{caminho}'