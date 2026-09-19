from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta

from users.models import User, Ong
from denuncias.models import Denuncias
from adocoes.models import Animal


class Command(BaseCommand):
    help = "Popula o banco com dados de teste (usuários, ONGs, animais e denúncias). Seguro rodar várias vezes: não duplica dados."

    def handle(self, *args, **options):
        self.stdout.write("Iniciando seed de dados do HelpPets...")

        # ------------------------------------------------------------------
        # Superusuário (acesso ao /admin/)
        # ------------------------------------------------------------------
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@helppets.com",
                password="helppets123",
                genero="prefiro_nao_dizer",
                telefone="84999990000",
                estado="RN",
                cidade="Natal",
                tipo="usuario",
            )
            self.stdout.write(self.style.SUCCESS("  -> Superusuário criado (admin@helppets.com / helppets123)"))
        else:
            self.stdout.write("  -> Superusuário já existe, pulando.")

        # ------------------------------------------------------------------
        # Usuários comuns
        # ------------------------------------------------------------------
        usuarios_comuns = [
            {
                "username": "joana.silva",
                "email": "joana.silva@example.com",
                "first_name": "Joana",
                "last_name": "Silva",
                "genero": "feminino",
                "nascimento": date(1997, 4, 12),
                "telefone": "84988887777",
                "cpf": "11122233344",
                "estado": "RN",
                "cidade": "Natal",
            },
            {
                "username": "carlos.souza",
                "email": "carlos.souza@example.com",
                "first_name": "Carlos",
                "last_name": "Souza",
                "genero": "masculino",
                "nascimento": date(1990, 9, 3),
                "telefone": "84977776666",
                "cpf": "22233344455",
                "estado": "RN",
                "cidade": "Mossoró",
            },
            {
                "username": "beatriz.lima",
                "email": "beatriz.lima@example.com",
                "first_name": "Beatriz",
                "last_name": "Lima",
                "genero": "feminino",
                "nascimento": date(2001, 1, 20),
                "telefone": "84966665555",
                "cpf": "33344455566",
                "estado": "RN",
                "cidade": "Apodi",
            },
        ]

        usuarios_criados = {}
        for dados in usuarios_comuns:
            user, created = User.objects.get_or_create(
                email=dados["email"],
                defaults={**dados, "tipo": "usuario"},
            )
            if created:
                user.set_password("helppets123")
                user.save()
                self.stdout.write(self.style.SUCCESS(f"  -> Usuário criado: {user.email}"))
            usuarios_criados[dados["username"]] = user

        # ------------------------------------------------------------------
        # ONGs (usuário tipo 'ong' + perfil Ong)
        # ------------------------------------------------------------------
        ongs_info = [
            {
                "username": "ong.patinhas",
                "email": "contato@patinhasdorn.org",
                "first_name": "Patinhas do RN",
                "last_name": "",
                "telefone": "84933334444",
                "cidade": "Natal",
                "endereco": "Rua das Flores, 123 - Natal/RN",
                "pix": "contato@patinhasdorn.org",
                "instagram": "@patinhasdorn",
                "descricao": "ONG dedicada ao resgate e adoção de cães e gatos abandonados na Grande Natal.",
            },
            {
                "username": "ong.focinhosdoseraom",
                "email": "contato@focinhosdosertao.org",
                "first_name": "Focinhos do Sertão",
                "last_name": "",
                "telefone": "84922223333",
                "cidade": "Mossoró",
                "endereco": "Av. Principal, 456 - Mossoró/RN",
                "pix": "focinhosdosertao@pix.com",
                "instagram": "@focinhosdosertao",
                "descricao": "Resgate, castração e adoção responsável de animais em situação de rua no oeste potiguar.",
            },
        ]

        ongs_criadas = {}
        for dados in ongs_info:
            user, created = User.objects.get_or_create(
                email=dados["email"],
                defaults={
                    "username": dados["username"],
                    "first_name": dados["first_name"],
                    "last_name": dados["last_name"],
                    "genero": "nao_informado",
                    "telefone": dados["telefone"],
                    "estado": "RN",
                    "cidade": dados["cidade"],
                    "tipo": "ong",
                },
            )
            if created:
                user.set_password("helppets123")
                user.save()
                self.stdout.write(self.style.SUCCESS(f"  -> Usuário ONG criado: {user.email}"))

            ong, ong_created = Ong.objects.get_or_create(
                usuario=user,
                defaults={
                    "endereco": dados["endereco"],
                    "pix": dados["pix"],
                    "instagram": dados["instagram"],
                    "descricao": dados["descricao"],
                },
            )
            if ong_created:
                self.stdout.write(self.style.SUCCESS(f"  -> Perfil de ONG criado: {dados['first_name']}"))

            ongs_criadas[dados["username"]] = ong

        # ------------------------------------------------------------------
        # Animais para adoção
        # ------------------------------------------------------------------
        animais = [
            {
                "nome": "Bidu",
                "especie": "Cachorro",
                "raca": "SRD (Vira-lata)",
                "idade": "2 anos",
                "descricao": "Muito dócil, adora crianças e já está castrado e vacinado.",
                "status_adocao": "disponivel",
                "ong": ongs_criadas["ong.patinhas"],
            },
            {
                "nome": "Mimi",
                "especie": "Gato",
                "raca": "SRD",
                "idade": "1 ano",
                "descricao": "Gata calma, independente, ótima para apartamento.",
                "status_adocao": "disponivel",
                "ong": ongs_criadas["ong.patinhas"],
            },
            {
                "nome": "Thor",
                "especie": "Cachorro",
                "raca": "Labrador (mestiço)",
                "idade": "4 anos",
                "descricao": "Brincalhão e protetor, já convive bem com outros cães.",
                "status_adocao": "adotado",
                "ong": ongs_criadas["ong.patinhas"],
            },
            {
                "nome": "Nina",
                "especie": "Cachorro",
                "raca": "SRD (Vira-lata)",
                "idade": "6 meses",
                "descricao": "Filhote resgatada na zona rural de Mossoró, cheia de energia.",
                "status_adocao": "disponivel",
                "ong": ongs_criadas["ong.focinhosdoseraom"],
            },
            {
                "nome": "Simba",
                "especie": "Gato",
                "raca": "SRD",
                "idade": "3 anos",
                "descricao": "Gato tranquilo, gosta de dormir no sol e é muito carinhoso.",
                "status_adocao": "disponivel",
                "ong": ongs_criadas["ong.focinhosdoseraom"],
            },
        ]

        for dados in animais:
            _, created = Animal.objects.get_or_create(
                nome=dados["nome"],
                ong=dados["ong"],
                defaults=dados,
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  -> Animal criado: {dados['nome']}"))

        # ------------------------------------------------------------------
        # Denúncias
        # ------------------------------------------------------------------
        agora = timezone.now()

        denuncias = [
            {
                "titulo_caixinha": "Cachorro ferido na BR-405",
                "midia_path": "seed/denuncia_1.jpg",
                "tipo_animal": "Cachorro",
                "quantidade": 1,
                "latitude": -5.199200,
                "longitude": -37.799900,
                "cidade": "Apodi",
                "condicao": ["Machucado", "Assustado"],
                "descricao": "Cachorro visto mancando na beira da estrada, parece ter sido atropelado.",
                "motivo": "Maus-tratos / acidente",
                "data_encontro": agora - timedelta(days=2),
                "status": "aberto",
                "ong_id": None,
                "usuario_id": usuarios_criados["beatriz.lima"],
            },
            {
                "titulo_caixinha": "Ninhada de gatos abandonada",
                "midia_path": "seed/denuncia_2.jpg",
                "tipo_animal": "Gato",
                "quantidade": 4,
                "latitude": -5.795300,
                "longitude": -35.199500,
                "cidade": "Natal",
                "condicao": ["Muito magro", "Sujo"],
                "descricao": "Quatro filhotes de gato encontrados numa caixa perto de um terreno baldio.",
                "motivo": "Abandono",
                "data_encontro": agora - timedelta(days=5),
                "status": "atendimento",
                "ong_id": ongs_criadas["ong.patinhas"],
                "usuario_id": usuarios_criados["joana.silva"],
            },
            {
                "titulo_caixinha": "Cavalo solto em área de risco",
                "midia_path": "seed/denuncia_3.jpg",
                "tipo_animal": "Equino",
                "quantidade": 1,
                "latitude": -5.187500,
                "longitude": -37.343300,
                "cidade": "Mossoró",
                "condicao": ["Perto de trânsito intenso", "Muito quieto / parado"],
                "descricao": "Cavalo perambulando próximo à rodovia, oferecendo risco a motoristas.",
                "motivo": "Risco à segurança / possível abandono",
                "data_encontro": agora - timedelta(days=10),
                "status": "finalizado",
                "ong_id": ongs_criadas["ong.focinhosdoseraom"],
                "usuario_id": usuarios_criados["carlos.souza"],
            },
        ]

        for dados in denuncias:
            _, created = Denuncias.objects.get_or_create(
                titulo_caixinha=dados["titulo_caixinha"],
                defaults=dados,
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  -> Denúncia criada: {dados['titulo_caixinha']}"))

        self.stdout.write(self.style.SUCCESS("Seed concluído com sucesso."))
