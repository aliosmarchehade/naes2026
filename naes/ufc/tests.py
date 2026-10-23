"""
Testes automatizados do Sistema UFC (NAES).

Cada teste corresponde a um caso de teste cadastrado no Testiny (CT01 ... CT51).
O número do caso aparece no nome do método e na docstring.

Como executar (na pasta onde está o manage.py):

    python manage.py test ufc --settings=naes.settings_test -v 2

Com medição de cobertura (teste caixa-branca):

    pip install coverage
    coverage run manage.py test ufc --settings=naes.settings_test
    coverage report -m --include="ufc/*,website/*"

IMPORTANTE: alguns testes FALHAM de propósito na versão atual do sistema.
Eles verificam o comportamento definido no plano de testes, e a falha indica
um defeito a ser registrado no Testiny e corrigido. NÃO altere o resultado
esperado para o teste passar.
"""
import io
import logging
from datetime import date

from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.db.models.deletion import ProtectedError
from django.test import Client, TestCase
from django.urls import NoReverseMatch, reverse

from .models import CategoriaPeso, Evento, Luta, Lutador, Pais

SENHA = "SenhaForte#2026"


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------
def imagem_png(nome="foto.png"):
    """Gera uma imagem PNG válida em memória para os testes de upload."""
    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (20, 20), color=(200, 0, 0)).save(buffer, format="PNG")
    return SimpleUploadedFile(nome, buffer.getvalue(), content_type="image/png")


class BaseUFCTestCase(TestCase):
    """Cria os dados de teste usados por quase todos os casos."""

    @classmethod
    def setUpTestData(cls):
        cls.usuario_a = User.objects.create_user("usuario_a", password=SENHA)
        cls.usuario_b = User.objects.create_user("usuario_b", password=SENHA)

        cls.brasil = Pais.objects.create(nome="Brasil", sigla="BR")
        cls.leve = CategoriaPeso.objects.create(nome="Peso Leve", peso_maximo="70.30")
        cls.medio = CategoriaPeso.objects.create(nome="Peso Médio", peso_maximo="83.90")

        cls.lutador_a = Lutador.objects.create(
            nome="Lutador do A", apelido="A", idade=30, peso="70.00",
            categoria=cls.leve, pais=cls.brasil, cadastrado_por=cls.usuario_a,
        )
        cls.lutador_b = Lutador.objects.create(
            nome="Lutador do B", apelido="B", idade=28, peso="69.50",
            categoria=cls.leve, pais=cls.brasil, cadastrado_por=cls.usuario_b,
        )
        cls.evento_a = Evento.objects.create(
            nome="UFC Teste", local="Curitiba", data=date(2026, 10, 10),
            pais=cls.brasil, usuario=cls.usuario_a,
        )

    def setUp(self):
        # Cliente que devolve o erro 500 como resposta, em vez de estourar a
        # exceção dentro do teste. Assim o teste consegue verificar o que o
        # usuário realmente veria no navegador.
        self.client = Client(raise_request_exception=False)
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def login_a(self):
        self.client.login(username="usuario_a", password=SENHA)

    def criar_luta(self, lutador_1=None, lutador_2=None, vencedor=None):
        return Luta.objects.create(
            lutador_1=lutador_1 or self.lutador_a,
            lutador_2=lutador_2 or self.lutador_b,
            evento=self.evento_a,
            categoria=self.leve,
            vencedor=vencedor,
            cadastrado_por=self.usuario_a,
        )

    def dados_lutador(self, **alteracoes):
        dados = {
            "nome": "Novo Lutador", "apelido": "Novo", "pais": self.brasil.pk,
            "idade": 25, "peso": "70.00", "categoria": self.leve.pk,
        }
        dados.update(alteracoes)
        return dados


# ---------------------------------------------------------------------------
# Instalação
# ---------------------------------------------------------------------------
class InstalacaoTests(TestCase):

    def test_CT01_projeto_configurado_e_migracoes_em_dia(self):
        """CT01 - O projeto passa na verificação do Django e não há migrações pendentes."""
        call_command("check", verbosity=0)
        try:
            call_command("makemigrations", "--check", "--dry-run", verbosity=0)
        except SystemExit:
            self.fail("Existem alterações nos models sem migração correspondente.")


# ---------------------------------------------------------------------------
# Funcional > Autenticação
# ---------------------------------------------------------------------------
class AutenticacaoTests(BaseUFCTestCase):

    def test_CT02_cadastrar_usuario_valido(self):
        """CT02 - Cadastro de usuário com dados válidos."""
        resposta = self.client.post(reverse("registrar"), {
            "username": "novo_usuario", "password1": SENHA, "password2": SENHA,
        })
        self.assertRedirects(resposta, reverse("login"))
        self.assertTrue(User.objects.filter(username="novo_usuario").exists())

    def test_CT03_cadastrar_usuario_invalido(self):
        """CT03 - Cadastro com campos vazios, senhas diferentes e usuário repetido é recusado."""
        casos = {
            "campos vazios": {"username": "", "password1": "", "password2": ""},
            "senhas diferentes": {"username": "outro", "password1": SENHA, "password2": SENHA + "x"},
            "usuário repetido": {"username": "usuario_a", "password1": SENHA, "password2": SENHA},
        }
        total_antes = User.objects.count()
        for descricao, dados in casos.items():
            with self.subTest(descricao):
                resposta = self.client.post(reverse("registrar"), dados)
                self.assertEqual(resposta.status_code, 200)
                self.assertTrue(resposta.context["form"].errors)
        self.assertEqual(User.objects.count(), total_antes)

    def test_CT04_login_valido(self):
        """CT04 - Login com credenciais válidas."""
        resposta = self.client.post(reverse("login"), {"username": "usuario_a", "password": SENHA})
        self.assertRedirects(resposta, "/", fetch_redirect_response=False)
        self.assertIn("_auth_user_id", self.client.session)

    def _assert_login_recusado(self, usuario, senha):
        resposta = self.client.post(reverse("login"), {"username": usuario, "password": senha})
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Usuário ou senha inválidos.")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_CT05_login_senha_incorreta(self):
        """CT05 - Login com senha incorreta é recusado com mensagem de erro."""
        self._assert_login_recusado("usuario_a", "senha_errada")

    def test_CT06_login_usuario_inexistente(self):
        """CT06 - Login com usuário inexistente é recusado com mensagem de erro."""
        self._assert_login_recusado("nao_existe", SENHA)

    def test_CT07_login_campos_em_branco(self):
        """CT07 - Login com campos em branco não autentica."""
        self._assert_login_recusado("", "")

    def test_CT08_logout(self):
        """CT08 - Logout encerra a sessão do usuário."""
        self.login_a()
        resposta = self.client.post(reverse("logout"))
        self.assertEqual(resposta.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)


# ---------------------------------------------------------------------------
# Funcional > Lutadores
# ---------------------------------------------------------------------------
class LutadorTests(BaseUFCTestCase):

    def test_CT09_cadastrar_lutador_valido(self):
        """CT09 - Cadastro de lutador com dados válidos, vinculado ao usuário logado."""
        self.login_a()
        resposta = self.client.post(reverse("lutador-create"), self.dados_lutador())
        self.assertRedirects(resposta, reverse("lutador-list"))
        novo = Lutador.objects.get(nome="Novo Lutador")
        self.assertEqual(novo.cadastrado_por, self.usuario_a)

    def test_CT10_cadastrar_lutador_campos_obrigatorios_vazios(self):
        """CT10 - Cadastro com campos obrigatórios vazios é recusado."""
        self.login_a()
        resposta = self.client.post(reverse("lutador-create"), {})
        self.assertEqual(resposta.status_code, 200)
        erros = resposta.context["form"].errors
        for campo in ("nome", "idade", "peso", "categoria"):
            self.assertIn(campo, erros)
        self.assertFalse(Lutador.objects.filter(nome="").exists())

    def test_CT10_idade_negativa_recusada(self):
        """CT10 (valor limite) - Idade -1 é recusada; idade 0 é o limite aceito pelo campo."""
        self.login_a()
        resposta = self.client.post(reverse("lutador-create"), self.dados_lutador(idade=-1))
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("idade", resposta.context["form"].errors)

    def test_CT11_somente_categorias_existentes(self):
        """CT11 - O campo categoria só aceita categorias cadastradas."""
        self.login_a()
        resposta = self.client.get(reverse("lutador-create"))
        opcoes = set(resposta.context["form"].fields["categoria"].queryset)
        self.assertEqual(opcoes, set(CategoriaPeso.objects.all()))

        resposta = self.client.post(reverse("lutador-create"), self.dados_lutador(categoria=99999))
        self.assertIn("categoria", resposta.context["form"].errors)
        self.assertFalse(Lutador.objects.filter(nome="Novo Lutador").exists())

    def test_CT12_alterar_lutador_proprio(self):
        """CT12 - Usuário altera o próprio lutador."""
        self.login_a()
        dados = self.dados_lutador(nome="Nome Alterado", vitorias=5, derrotas=1)
        resposta = self.client.post(reverse("lutador-update", args=[self.lutador_a.pk]), dados)
        self.assertRedirects(resposta, reverse("lutador-list"))
        self.lutador_a.refresh_from_db()
        self.assertEqual(self.lutador_a.nome, "Nome Alterado")
        self.assertEqual(self.lutador_a.vitorias, 5)

    def test_CT13_excluir_lutador_proprio_sem_lutas(self):
        """CT13 - Usuário comum exclui o próprio lutador (sem lutas)."""
        self.login_a()
        resposta = self.client.post(reverse("lutador-delete", args=[self.lutador_a.pk]))
        self.assertNotEqual(
            resposta.status_code, 403,
            "DEFEITO: LutadorDelete usa GroupRequiredMixin e só permite exclusão a quem é "
            "do grupo 'Administradores'. O dono do lutador recebe 403 (acesso negado).",
        )
        self.assertRedirects(resposta, reverse("lutador-list"))
        self.assertFalse(Lutador.objects.filter(pk=self.lutador_a.pk).exists())

    def test_CT14_excluir_lutador_vinculado_a_lutas(self):
        """CT14 - Excluir lutador com lutas: não exclui e mostra mensagem (sem erro 500).

        Caixa-branca: o usuário é colocado no grupo 'Administradores' para
        passar pelo GroupRequiredMixin e chegar ao caminho do ProtectedError.
        """
        Group.objects.get_or_create(name="Administradores")[0].user_set.add(self.usuario_a)
        self.criar_luta()
        self.login_a()
        resposta = self.client.post(reverse("lutador-delete", args=[self.lutador_a.pk]))
        self.assertTrue(Lutador.objects.filter(pk=self.lutador_a.pk).exists())
        self.assertNotEqual(
            resposta.status_code, 500,
            "DEFEITO: a exclusão levanta ProtectedError sem tratamento e o usuário vê erro 500.",
        )

    def test_CT15_upload_da_foto(self):
        """CT15 - A foto enviada no cadastro é salva."""
        self.login_a()
        resposta = self.client.post(
            reverse("lutador-create"), self.dados_lutador(foto=imagem_png()),
        )
        self.assertRedirects(resposta, reverse("lutador-list"))
        novo = Lutador.objects.get(nome="Novo Lutador")
        self.assertTrue(novo.foto.name.startswith("lutadores/"))

    def test_CT15_foto_exibida_no_detalhe(self):
        """CT15 - A foto enviada é exibida na página de detalhe do lutador."""
        self.lutador_a.foto = imagem_png("detalhe.png")
        self.lutador_a.save()
        resposta = self.client.get(reverse("lutador-detail", args=[self.lutador_a.pk]))
        self.assertContains(
            resposta, self.lutador_a.foto.url,
            msg_prefix="DEFEITO: o template lutador_detail.html não exibe a foto do lutador.",
        )

    def test_CT16_upload_de_arquivo_que_nao_e_imagem(self):
        """CT16 - Arquivo que não é imagem é recusado no campo foto."""
        self.login_a()
        arquivo = SimpleUploadedFile("texto.txt", b"isto nao e imagem", content_type="text/plain")
        resposta = self.client.post(reverse("lutador-create"), self.dados_lutador(foto=arquivo))
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("foto", resposta.context["form"].errors)
        self.assertFalse(Lutador.objects.filter(nome="Novo Lutador").exists())


# ---------------------------------------------------------------------------
# Funcional > Categorias de peso
# ---------------------------------------------------------------------------
class CategoriaPesoTests(BaseUFCTestCase):

    def test_CT17_cadastrar_categoria(self):
        """CT17 - Cadastro de categoria de peso."""
        self.login_a()
        resposta = self.client.post(reverse("categoria-create"), {"nome": "Peso Pena", "peso_maximo": "65.80"})
        self.assertRedirects(resposta, reverse("categoria-list"))
        self.assertTrue(CategoriaPeso.objects.filter(nome="Peso Pena").exists())

    def test_CT18_cadastrar_categoria_invalida(self):
        """CT18 - Cadastro de categoria com campos vazios é recusado."""
        self.login_a()
        total = CategoriaPeso.objects.count()
        resposta = self.client.post(reverse("categoria-create"), {"nome": "", "peso_maximo": ""})
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("nome", resposta.context["form"].errors)
        self.assertIn("peso_maximo", resposta.context["form"].errors)
        self.assertEqual(CategoriaPeso.objects.count(), total)

    def test_CT19_alterar_categoria(self):
        """CT19 - Alteração de categoria de peso."""
        self.login_a()
        resposta = self.client.post(
            reverse("categoria-update", args=[self.medio.pk]), {"nome": "Peso Médio", "peso_maximo": "84.00"},
        )
        self.assertRedirects(resposta, reverse("categoria-list"))
        self.medio.refresh_from_db()
        self.assertEqual(str(self.medio.peso_maximo), "84.00")

    def test_CT20_excluir_categoria_sem_lutadores(self):
        """CT20 - Exclusão de categoria sem lutadores vinculados."""
        self.login_a()
        resposta = self.client.post(reverse("categoria-delete", args=[self.medio.pk]))
        self.assertRedirects(resposta, reverse("categoria-list"))
        self.assertFalse(CategoriaPeso.objects.filter(pk=self.medio.pk).exists())


# ---------------------------------------------------------------------------
# Funcional > Países
# ---------------------------------------------------------------------------
class PaisTests(BaseUFCTestCase):

    def test_CT21_cadastrar_pais(self):
        """CT21 - Cadastro de país."""
        self.login_a()
        resposta = self.client.post(reverse("pais-create"), {"nome": "Estados Unidos", "sigla": "US"})
        self.assertRedirects(resposta, reverse("pais-list"))
        self.assertTrue(Pais.objects.filter(sigla="US").exists())

    def test_CT22_cadastrar_pais_invalido(self):
        """CT22 - País com campos vazios ou sigla com 3 letras (acima do limite de 2) é recusado."""
        self.login_a()
        total = Pais.objects.count()
        for dados in ({"nome": "", "sigla": ""}, {"nome": "Brasil", "sigla": "BRA"}):
            with self.subTest(dados=dados):
                resposta = self.client.post(reverse("pais-create"), dados)
                self.assertEqual(resposta.status_code, 200)
                self.assertTrue(resposta.context["form"].errors)
        self.assertEqual(Pais.objects.count(), total)

    def test_CT23_consultar_paises(self):
        """CT23 - Listagem exibe os países cadastrados."""
        Pais.objects.create(nome="Japão", sigla="JP")
        resposta = self.client.get(reverse("pais-list"))
        self.assertContains(resposta, "Brasil")
        self.assertContains(resposta, "Japão")


# ---------------------------------------------------------------------------
# Funcional > Eventos
# ---------------------------------------------------------------------------
class EventoTests(BaseUFCTestCase):

    def dados_evento(self, **alteracoes):
        dados = {"nome": "UFC 400", "pais": self.brasil.pk, "local": "São Paulo",
                 "data": "2026-12-12", "descricao": "Evento de teste"}
        dados.update(alteracoes)
        return dados

    def test_CT24_cadastrar_evento(self):
        """CT24 - Cadastro de evento com dados válidos."""
        self.login_a()
        resposta = self.client.post(reverse("evento-create"), self.dados_evento())
        self.assertRedirects(resposta, reverse("evento-list"))
        self.assertEqual(Evento.objects.get(nome="UFC 400").usuario, self.usuario_a)

    def test_CT25_cadastrar_evento_invalido(self):
        """CT25 - Evento com campos vazios ou data inválida é recusado."""
        self.login_a()
        for dados in (self.dados_evento(nome="", local=""), self.dados_evento(data="2026-13-45")):
            with self.subTest(dados=dados):
                resposta = self.client.post(reverse("evento-create"), dados)
                self.assertEqual(resposta.status_code, 200)
                self.assertTrue(resposta.context["form"].errors)
        self.assertFalse(Evento.objects.filter(nome="UFC 400").exists())

    def test_CT26_alterar_evento(self):
        """CT26 - Alteração de evento pelo usuário que o cadastrou."""
        self.login_a()
        resposta = self.client.post(
            reverse("evento-update", args=[self.evento_a.pk]), self.dados_evento(nome="UFC Alterado"),
        )
        self.assertRedirects(resposta, reverse("evento-list"))
        self.evento_a.refresh_from_db()
        self.assertEqual(self.evento_a.nome, "UFC Alterado")

    def test_CT27_excluir_evento(self):
        """CT27 - Exclusão de evento pelo usuário que o cadastrou."""
        self.login_a()
        resposta = self.client.post(reverse("evento-delete", args=[self.evento_a.pk]))
        self.assertRedirects(resposta, reverse("evento-list"))
        self.assertFalse(Evento.objects.filter(pk=self.evento_a.pk).exists())


# ---------------------------------------------------------------------------
# Funcional > Lutas
# ---------------------------------------------------------------------------
class LutaTests(BaseUFCTestCase):
    """As rotas de luta seguem o padrão de nomes das demais (luta-create etc.)."""

    def _assert_rota_existe(self, nome, *args):
        try:
            reverse(nome, args=args)
        except NoReverseMatch:
            self.fail(f"DEFEITO: não existe a rota '{nome}'. A aplicação não possui CRUD de lutas.")

    def test_CT28_cadastrar_luta(self):
        """CT28 - Existe funcionalidade para cadastrar lutas."""
        self._assert_rota_existe("luta-create")

    def test_CT29_luta_com_mesmo_lutador_nos_dois_lados(self):
        """CT29 - Uma luta não pode ter o mesmo lutador nos dois lados."""
        luta = Luta(lutador_1=self.lutador_a, lutador_2=self.lutador_a, evento=self.evento_a,
                    categoria=self.leve, cadastrado_por=self.usuario_a)
        with self.assertRaises(ValidationError, msg="DEFEITO: o model Luta aceita o mesmo lutador nos dois lados."):
            luta.full_clean()

    def test_CT30_vencedor_que_nao_participa_da_luta(self):
        """CT30 - O vencedor precisa ser um dos dois lutadores da luta."""
        terceiro = Lutador.objects.create(nome="Terceiro", idade=30, peso="70.00",
                                          categoria=self.leve, cadastrado_por=self.usuario_a)
        luta = Luta(lutador_1=self.lutador_a, lutador_2=self.lutador_b, vencedor=terceiro,
                    evento=self.evento_a, categoria=self.leve, cadastrado_por=self.usuario_a)
        with self.assertRaises(ValidationError, msg="DEFEITO: o model Luta aceita um vencedor que não luta."):
            luta.full_clean()

    def test_CT31_alterar_luta(self):
        """CT31 - Existe funcionalidade para alterar lutas."""
        self._assert_rota_existe("luta-update", 1)

    def test_CT32_excluir_luta(self):
        """CT32 - Existe funcionalidade para excluir lutas."""
        self._assert_rota_existe("luta-delete", 1)


# ---------------------------------------------------------------------------
# Funcional > Ranking e paginação
# ---------------------------------------------------------------------------
class RankingPaginacaoTests(BaseUFCTestCase):

    def _ranking_da_categoria(self, categoria):
        resposta = self.client.get(reverse("ranking"))
        self.assertEqual(resposta.status_code, 200)
        for grupo in resposta.context["ranking"]:
            if grupo["categoria"] == categoria:
                return [lutador.nome for lutador in grupo["lutadores"]]
        self.fail(f"Categoria {categoria} não aparece no ranking.")

    def test_CT33_ranking_por_categoria(self):
        """CT33 - Ranking mostra só a categoria, ordenado por vitórias (desc) e derrotas (asc)."""
        Lutador.objects.filter(pk=self.lutador_a.pk).update(vitorias=10, derrotas=2)
        Lutador.objects.filter(pk=self.lutador_b.pk).update(vitorias=10, derrotas=1)
        Lutador.objects.create(nome="Campeão", idade=31, peso="70.00", categoria=self.leve,
                               vitorias=15, derrotas=0, cadastrado_por=self.usuario_a)
        Lutador.objects.create(nome="De outra categoria", idade=31, peso="83.00", categoria=self.medio,
                               vitorias=99, cadastrado_por=self.usuario_a)

        self.assertEqual(
            self._ranking_da_categoria(self.leve),
            ["Campeão", "Lutador do B", "Lutador do A"],
        )

    def test_CT34_ranking_de_categoria_sem_lutadores(self):
        """CT34 - Categoria sem lutadores aparece vazia, sem erro."""
        self.assertEqual(self._ranking_da_categoria(self.medio), [])

    def _criar_lutadores(self, quantidade_total):
        faltam = quantidade_total - Lutador.objects.count()
        Lutador.objects.bulk_create([
            Lutador(nome=f"Extra {i}", idade=20, peso="70.00", categoria=self.leve)
            for i in range(faltam)
        ])

    def test_CT35_paginacao_no_limite(self):
        """CT35 (valor limite) - Com exatamente 10 lutadores existe uma única página."""
        self._criar_lutadores(10)
        resposta = self.client.get(reverse("lutador-list"))
        self.assertEqual(resposta.context["paginator"].num_pages, 1)
        self.assertEqual(len(resposta.context["lutadores"]), 10)
        self.assertEqual(self.client.get(reverse("lutador-list") + "?page=2").status_code, 404)

    def test_CT35_paginacao_acima_do_limite(self):
        """CT35 (valor limite) - Com 11 lutadores a 2ª página tem 1 registro, sem repetição."""
        self._criar_lutadores(11)
        pagina_1 = self.client.get(reverse("lutador-list")).context["lutadores"]
        pagina_2 = self.client.get(reverse("lutador-list") + "?page=2").context["lutadores"]
        self.assertEqual(len(pagina_1), 10)
        self.assertEqual(len(pagina_2), 1)
        self.assertFalse({l.pk for l in pagina_1} & {l.pk for l in pagina_2})


# ---------------------------------------------------------------------------
# Segurança e controle de acesso
# ---------------------------------------------------------------------------
class SegurancaTests(BaseUFCTestCase):

    def _assert_redireciona_para_login(self, url):
        resposta = self.client.get(url)
        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(
            resposta.url.startswith(reverse("login")),
            f"DEFEITO: redirecionou para '{resposta.url}', que não existe (404). "
            "Falta configurar LOGIN_URL = 'login' no settings.py.",
        )

    def test_CT36_acesso_sem_autenticacao(self):
        """CT36 - Usuário não autenticado é redirecionado para a página de login."""
        self._assert_redireciona_para_login(reverse("lutador-create"))

    def test_CT36_cadastro_sem_autenticacao_nao_grava(self):
        """CT36 - Um POST sem autenticação não cadastra o lutador."""
        self.client.post(reverse("lutador-create"), self.dados_lutador())
        self.assertFalse(Lutador.objects.filter(nome="Novo Lutador").exists())

    def test_CT37_alterar_lutador_de_outro_usuario(self):
        """CT37 - Acesso direto à edição do lutador de outro usuário é negado."""
        self.login_a()
        url = reverse("lutador-update", args=[self.lutador_b.pk])
        self.assertEqual(self.client.get(url).status_code, 404)
        self.client.post(url, self.dados_lutador(nome="Invadido"))
        self.lutador_b.refresh_from_db()
        self.assertEqual(self.lutador_b.nome, "Lutador do B")

    def test_CT37_CT38_botoes_nao_aparecem_para_lutador_de_outro_usuario(self):
        """CT37/CT38 - A listagem não mostra Editar/Excluir nos lutadores de outro usuário."""
        self.login_a()
        resposta = self.client.get(reverse("lutador-list"))
        self.assertNotContains(
            resposta, reverse("lutador-update", args=[self.lutador_b.pk]),
            msg_prefix="DEFEITO: lutador_list.html mostra os botões para todos os lutadores.",
        )
        self.assertNotContains(resposta, reverse("lutador-delete", args=[self.lutador_b.pk]))

    def test_CT38_excluir_lutador_de_outro_usuario(self):
        """CT38 - Exclusão do lutador de outro usuário é negada."""
        self.login_a()
        resposta = self.client.post(reverse("lutador-delete", args=[self.lutador_b.pk]))
        self.assertIn(resposta.status_code, (403, 404))
        self.assertTrue(Lutador.objects.filter(pk=self.lutador_b.pk).exists())

    def test_CT39_acesso_apos_logout(self):
        """CT39 - Após o logout, a área protegida volta a exigir login."""
        self.login_a()
        self.client.post(reverse("logout"))
        self._assert_redireciona_para_login(reverse("lutador-create"))


# ---------------------------------------------------------------------------
# Interface do usuário
# ---------------------------------------------------------------------------
class InterfaceTests(BaseUFCTestCase):

    def test_CT40_navegacao_pelas_principais_telas(self):
        """CT40 - Todas as telas principais abrem sem erro."""
        self.login_a()
        paginas = [
            reverse("index"), reverse("sobre"), reverse("contato"),
            reverse("lutador-list"), reverse("lutador-create"),
            reverse("lutador-detail", args=[self.lutador_a.pk]),
            reverse("categoria-list"), reverse("categoria-create"),
            reverse("categoria-detail", args=[self.leve.pk]),
            reverse("evento-list"), reverse("evento-create"),
            reverse("evento-detail", args=[self.evento_a.pk]),
            reverse("pais-list"), reverse("pais-create"),
            reverse("pais-detail", args=[self.brasil.pk]),
            reverse("ranking"),
        ]
        com_erro = [(url, self.client.get(url).status_code) for url in paginas]
        com_erro = [(url, codigo) for url, codigo in com_erro if codigo != 200]
        self.assertEqual(com_erro, [], f"DEFEITO: telas que não abrem (url, status): {com_erro}")

    def test_CT40_telas_publicas_login_e_cadastro(self):
        """CT40 - Telas de login e de cadastro de usuário abrem sem erro."""
        for url in (reverse("login"), reverse("registrar")):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_CT41_formularios_exibem_campos_e_validacao(self):
        """CT41 - Os formulários mostram os campos esperados e erros ao enviar vazio."""
        self.login_a()
        formularios = {
            "lutador-create": ["nome", "apelido", "foto", "pais", "idade", "peso", "categoria"],
            "categoria-create": ["nome", "peso_maximo"],
            "evento-create": ["nome", "pais", "local", "data", "descricao"],
            "pais-create": ["nome", "sigla"],
        }
        for rota, campos in formularios.items():
            with self.subTest(rota=rota):
                form = self.client.get(reverse(rota)).context["form"]
                self.assertEqual(list(form.fields), campos)
                self.assertTrue(self.client.post(reverse(rota), {}).context["form"].errors)

    def test_CT42_exibicao_das_informacoes_do_lutador(self):
        """CT42 - O detalhe do lutador mostra nome, país, categoria e cartel."""
        resposta = self.client.get(reverse("lutador-detail", args=[self.lutador_a.pk]))
        for texto in ("Lutador do A", "Brasil", "Peso Leve", "30 anos"):
            self.assertContains(resposta, texto)

    def test_CT43_exibicao_do_evento_e_suas_lutas(self):
        """CT43 - O detalhe do evento mostra as lutas do evento."""
        self.criar_luta()
        resposta = self.client.get(reverse("evento-detail", args=[self.evento_a.pk]))
        self.assertContains(resposta, "UFC Teste")
        self.assertContains(
            resposta, "Lutador do B",
            msg_prefix="DEFEITO: evento_detail.html não exibe as lutas do evento.",
        )

    def test_CT44_erro_ao_excluir_lutador_vinculado_a_lutas(self):
        """CT44 - Excluir lutador com lutas mostra mensagem amigável, não erro 500."""
        Group.objects.get_or_create(name="Administradores")[0].user_set.add(self.usuario_a)
        self.criar_luta()
        self.login_a()
        resposta = self.client.post(reverse("lutador-delete", args=[self.lutador_a.pk]), follow=True)
        self.assertNotEqual(resposta.status_code, 500, "DEFEITO: o usuário vê uma página de erro 500.")

    def test_CT44_erro_ao_excluir_categoria_com_lutadores(self):
        """CT44 - Excluir categoria que tem lutadores mostra mensagem amigável, não erro 500."""
        self.login_a()
        resposta = self.client.post(reverse("categoria-delete", args=[self.leve.pk]), follow=True)
        self.assertTrue(CategoriaPeso.objects.filter(pk=self.leve.pk).exists())
        self.assertNotEqual(resposta.status_code, 500, "DEFEITO: o usuário vê uma página de erro 500.")


# ---------------------------------------------------------------------------
# Banco de dados
# ---------------------------------------------------------------------------
class BancoDeDadosTests(BaseUFCTestCase):

    def test_CT45_persistencia_de_usuarios(self):
        """CT45 - Usuário é gravado, alterado e removido corretamente."""
        usuario = User.objects.create_user("temporario", password=SENHA)
        self.assertTrue(User.objects.filter(username="temporario").exists())
        usuario.email = "temp@teste.com"
        usuario.save()
        self.assertEqual(User.objects.get(pk=usuario.pk).email, "temp@teste.com")
        usuario.delete()
        self.assertFalse(User.objects.filter(username="temporario").exists())

    def test_CT46_persistencia_de_lutadores(self):
        """CT46 - Lutador é gravado com o dono correto, alterado e removido."""
        lutador = Lutador.objects.create(nome="Persistido", idade=22, peso="66.00",
                                         categoria=self.leve, cadastrado_por=self.usuario_b)
        self.assertEqual(Lutador.objects.get(pk=lutador.pk).cadastrado_por, self.usuario_b)
        Lutador.objects.filter(pk=lutador.pk).update(peso="67.50")
        self.assertEqual(str(Lutador.objects.get(pk=lutador.pk).peso), "67.50")
        lutador.delete()
        self.assertFalse(Lutador.objects.filter(pk=lutador.pk).exists())

    def test_CT47_persistencia_de_eventos(self):
        """CT47 - Evento é gravado, alterado e removido."""
        evento = Evento.objects.create(nome="Fight Night", local="Rio", data=date(2027, 1, 1))
        Evento.objects.filter(pk=evento.pk).update(local="Manaus")
        self.assertEqual(Evento.objects.get(pk=evento.pk).local, "Manaus")
        evento.delete()
        self.assertFalse(Evento.objects.filter(pk=evento.pk).exists())

    def test_CT48_persistencia_de_categorias_e_paises(self):
        """CT48 - Categorias e países são gravados sem duplicação; excluir país não apaga lutador (SET_NULL)."""
        CategoriaPeso.objects.create(nome="Peso Pesado", peso_maximo="120.20")
        self.assertEqual(CategoriaPeso.objects.filter(nome="Peso Pesado").count(), 1)
        self.brasil.delete()
        self.lutador_a.refresh_from_db()
        self.assertIsNone(self.lutador_a.pais)

    def test_CT49_persistencia_de_lutas_e_vinculos(self):
        """CT49 - Luta é gravada com os vínculos corretos."""
        luta = self.criar_luta(vencedor=self.lutador_a)
        gravada = Luta.objects.get(pk=luta.pk)
        self.assertEqual(gravada.lutador_1, self.lutador_a)
        self.assertEqual(gravada.lutador_2, self.lutador_b)
        self.assertEqual(gravada.evento, self.evento_a)
        self.assertEqual(gravada.categoria, self.leve)
        self.assertEqual(gravada.vencedor, self.lutador_a)

    def test_CT50_protect_ao_excluir_lutador_com_luta(self):
        """CT50 - Banco bloqueia a exclusão de lutador vinculado a luta (PROTECT)."""
        self.criar_luta()
        with self.assertRaises(ProtectedError):
            self.lutador_a.delete()
        self.assertTrue(Lutador.objects.filter(pk=self.lutador_a.pk).exists())
        self.assertEqual(Luta.objects.count(), 1)

    def test_CT51_integridade_ao_excluir_evento_ou_categoria_com_lutas(self):
        """CT51 - Evento e categoria com lutas não podem ser excluídos (nenhuma luta fica órfã)."""
        self.criar_luta()
        with self.assertRaises(ProtectedError):
            self.evento_a.delete()
        with self.assertRaises(ProtectedError):
            self.leve.delete()
        self.assertEqual(Luta.objects.count(), 1)
