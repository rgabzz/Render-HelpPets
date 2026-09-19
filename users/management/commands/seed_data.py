from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta

from users.models import User, Ong
from denuncias.models import Denuncias
from adocoes.models import Animal, Adocao


class Command(BaseCommand):
    help = "Popula o banco com dados de teste (usuários, ONGs, animais, denúncias e adoções). Seguro rodar várias vezes: não duplica dados."

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
        # Usuários comuns (todos em Caraúbas/RN, pra facilitar teste de filtro por cidade)
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
                "cidade": "Caraúbas",
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
                "cidade": "Caraúbas",
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
                "cidade": "Caraúbas",
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
        # ONGs (usuário tipo 'ong' + perfil Ong) — também em Caraúbas/RN
        # ------------------------------------------------------------------
        ongs_info = [
            {
                "username": "ong.patinhas",
                "email": "contato@patinhasdorn.org",
                "first_name": "Patinhas do RN",
                "last_name": "",
                "telefone": "84933334444",
                "cidade": "Caraúbas",
                "endereco": "Rua das Flores, 123 - Caraúbas/RN",
                "pix": "contato@patinhasdorn.org",
                "instagram": "@patinhasdorn",
                "descricao": "ONG dedicada ao resgate e adoção de cães e gatos abandonados em Caraúbas e região.",
            },
            {
                "username": "ong.focinhosdoseraom",
                "email": "contato@focinhosdosertao.org",
                "first_name": "Focinhos do Sertão",
                "last_name": "",
                "telefone": "84922223333",
                "cidade": "Caraúbas",
                "endereco": "Av. Principal, 456 - Caraúbas/RN",
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
        animais_info = [
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
                "descricao": "Filhote resgatada na zona rural de Caraúbas, cheia de energia.",
                "status_adocao": "em_processo",
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

        animais_criados = {}
        for dados in animais_info:
            animal, created = Animal.objects.get_or_create(
                nome=dados["nome"],
                ong=dados["ong"],
                defaults=dados,
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  -> Animal criado: {dados['nome']}"))
            animais_criados[dados["nome"]] = animal

        # ------------------------------------------------------------------
        # Denúncias — também em Caraúbas/RN (coordenadas aproximadas da cidade)
        # ------------------------------------------------------------------
        agora = timezone.now()

        denuncias = [
            {
                "titulo_caixinha": "Cachorro ferido na estrada de Caraúbas",
                "midia_path": "seed/denuncia_1.jpg",
                "tipo_animal": "Cachorro",
                "quantidade": 1,
                "latitude": -5.742200,
                "longitude": -37.475000,
                "cidade": "Caraúbas",
                "condicao": ["Machucado", "Assustado"],
                "descricao": "Cachorro visto mancando na beira da estrada, parece ter sido atropelado.",
                "motivo": "Maus-tratos / acidente",
                "data_encontro": agora - timedelta(days=2),
                "status": "aberto",
                "ong": None,
                "usuario": usuarios_criados["beatriz.lima"],
            },
            {
                "titulo_caixinha": "Ninhada de gatos abandonada",
                "midia_path": "seed/denuncia_2.jpg",
                "tipo_animal": "Gato",
                "quantidade": 4,
                "latitude": -5.736500,
                "longitude": -37.466600,
                "cidade": "Caraúbas",
                "condicao": ["Muito magro", "Sujo"],
                "descricao": "Quatro filhotes de gato encontrados numa caixa perto de um terreno baldio.",
                "motivo": "Abandono",
                "data_encontro": agora - timedelta(days=5),
                "status": "atendimento",
                "ong": ongs_criadas["ong.patinhas"],
                "usuario": usuarios_criados["joana.silva"],
            },
            {
                "titulo_caixinha": "Cavalo solto em área de risco",
                "midia_path": "seed/denuncia_3.jpg",
                "tipo_animal": "Equino",
                "quantidade": 1,
                "latitude": -5.732000,
                "longitude": -37.475900,
                "cidade": "Caraúbas",
                "condicao": ["Perto de trânsito intenso", "Muito quieto / parado"],
                "descricao": "Cavalo perambulando próximo à rodovia, oferecendo risco a motoristas.",
                "motivo": "Risco à segurança / possível abandono",
                "data_encontro": agora - timedelta(days=10),
                "status": "finalizado",
                "ong": ongs_criadas["ong.focinhosdoseraom"],
                "usuario": usuarios_criados["carlos.souza"],
            },
        ]

        for dados in denuncias:
            _, created = Denuncias.objects.get_or_create(
                titulo_caixinha=dados["titulo_caixinha"],
                defaults=dados,
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  -> Denúncia criada: {dados['titulo_caixinha']}"))

        # ------------------------------------------------------------------
        # Adoções (liga um animal já adotado/em processo a um usuário e uma ONG)
        # ------------------------------------------------------------------
        adocoes = [
            {
                "animal": animais_criados["Thor"],
                "ong": ongs_criadas["ong.patinhas"],
                "usuario": usuarios_criados["carlos.souza"],
                "data_adocao": agora - timedelta(days=15),
            },
            {
                "animal": animais_criados["Nina"],
                "ong": ongs_criadas["ong.focinhosdoseraom"],
                "usuario": usuarios_criados["joana.silva"],
                "data_adocao": agora - timedelta(days=1),
            },
        ]

        for dados in adocoes:
            _, created = Adocao.objects.get_or_create(
                animal=dados["animal"],
                usuario=dados["usuario"],
                defaults=dados,
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"  -> Adoção registrada: {dados['animal'].nome} -> {dados['usuario'].email}")
                )

        self.stdout.write(self.style.SUCCESS("Seed concluído com sucesso."))
