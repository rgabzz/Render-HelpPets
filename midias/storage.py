import io
import uuid

import requests
from django.conf import settings
from django.db.models import Max
from PIL import Image, ImageOps, UnidentifiedImageError
from rest_framework import serializers

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB por foto recebida
MAX_DIMENSAO = 1600                  # lado maior, em pixels
QUALIDADE_WEBP = 82
MAX_FOTOS = 4                        # fotos por denúncia / por animal
Image.MAX_IMAGE_PIXELS = 50_000_000


def enviar_foto(arquivo, pasta):
    """Otimiza UMA foto, envia ao Supabase Storage e devolve a URL pública.

    pasta: prefixo dentro do bucket, ex.: 'denuncias/7' ou 'animais/3'.
    """
    if arquivo.size > MAX_UPLOAD_BYTES:
        raise serializers.ValidationError({'fotos': 'Cada foto deve ter no máximo 10 MB.'})
    if not (settings.SUPABASE_URL and settings.SUPABASE_SECRET_KEY):
        raise serializers.ValidationError({'fotos': 'Storage de imagens não configurado no servidor.'})

    try:
        arquivo.seek(0)
        img = Image.open(arquivo)
        img = ImageOps.exif_transpose(img)
        img = img.convert('RGB')
    except (UnidentifiedImageError, OSError):
        raise serializers.ValidationError({'fotos': 'Um dos arquivos não é uma imagem válida.'})

    img.thumbnail((MAX_DIMENSAO, MAX_DIMENSAO))
    buf = io.BytesIO()
    img.save(buf, format='WEBP', quality=QUALIDADE_WEBP, method=6)  # descarta EXIF/GPS

    caminho = f'{pasta}/{uuid.uuid4().hex}.webp'
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
        raise serializers.ValidationError({'fotos': 'Não foi possível enviar as fotos agora. Tente de novo.'})

    if resp.status_code not in (200, 201):
        raise serializers.ValidationError({'fotos': 'Falha ao salvar uma das fotos no storage.'})

    return f'{settings.SUPABASE_URL}/storage/v1/object/public/{settings.SUPABASE_BUCKET}/{caminho}'


def enviar_fotos(arquivos, pasta):
    """Envia várias fotos e devolve a lista de URLs, na mesma ordem."""
    return [enviar_foto(a, pasta) for a in arquivos]


def checar_limite(ja_existentes, novas):
    if ja_existentes + novas > MAX_FOTOS:
        raise serializers.ValidationError(
            {'fotos': f'Máximo de {MAX_FOTOS} fotos (já existem {ja_existentes}, você enviou {novas}).'}
        )


def criar_fotos(modelo_foto, campo, objeto, urls):
    """Cria as linhas de foto (a ordem continua de onde parou) para o objeto."""
    filtro = {campo: objeto}
    ultima = modelo_foto.objects.filter(**filtro).aggregate(m=Max('ordem'))['m'] or 0
    modelo_foto.objects.bulk_create([
        modelo_foto(**filtro, midia_path=url, ordem=ultima + i)
        for i, url in enumerate(urls, start=1)
    ])