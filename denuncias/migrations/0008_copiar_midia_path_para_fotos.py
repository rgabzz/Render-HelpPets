from django.db import migrations


def copiar_para_fotos(apps, schema_editor):
    """Cada midia_path que já existe vira a foto 1 da própria denúncia."""
    Denuncias = apps.get_model('denuncias', 'Denuncias')
    DenunciaFoto = apps.get_model('denuncias', 'DenunciaFoto')
    for d in Denuncias.objects.exclude(midia_path='').iterator():
        DenunciaFoto.objects.get_or_create(
            denuncia=d, midia_path=d.midia_path, defaults={'ordem': 1}
        )


def voltar_para_midia_path(apps, schema_editor):
    """Se a migração for desfeita, a primeira foto volta para midia_path."""
    Denuncias = apps.get_model('denuncias', 'Denuncias')
    for d in Denuncias.objects.iterator():
        primeira = d.fotos.order_by('ordem', 'id').first()
        if primeira:
            d.midia_path = primeira.midia_path
            d.save(update_fields=['midia_path'])


class Migration(migrations.Migration):

    dependencies = [
        ('denuncias', '0008_fotos'),
    ]

    operations = [
        migrations.RunPython(copiar_para_fotos, voltar_para_midia_path),
    ]