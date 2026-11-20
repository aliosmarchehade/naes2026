
import time

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import (
    ConfiguracaoIA,
    CotaMensalIA,
    RegistroChamadaIA,
)

from .agents.assistente import responder


class CotaIAExcedida(Exception):
    """Indica que o usuário atingiu sua cota mensal de tokens."""


def chamar_ia(usuario, pergunta):
    """
    Executa uma chamada à IA, controla a cota mensal
    e registra a utilização no banco de dados.
    """

    if not usuario or not usuario.is_authenticated:
        raise PermissionError("É necessário estar autenticado.")

    hoje = timezone.localdate()
    inicio = time.monotonic()

    modelo = settings.OPENAI_MODEL

    tokens_entrada = 0
    tokens_saida = 0
    total_tokens = 0
    identificador = ""

    status = "erro"
    mensagem_erro = ""

    try:
        with transaction.atomic():

            # Recupera as configurações da IA
            configuracao = ConfiguracaoIA.objects.first()

            if configuracao:
                if not configuracao.ativa:
                    raise ValueError(
                        "A integração com IA está desativada."
                    )

                modelo = configuracao.modelo

            if not settings.OPENAI_API_KEY:
                raise ValueError(
                    "A chave da API não foi configurada."
                )

            # Cria ou recupera a cota mensal do usuário
            cota, _ = CotaMensalIA.objects.get_or_create(
                usuario=usuario,
                ano=hoje.year,
                mes=hoje.month,
            )

            # Bloqueia alterações concorrentes na mesma cota
            cota = CotaMensalIA.objects.select_for_update().get(
                pk=cota.pk
            )

            # Verifica se o usuário já atingiu o limite
            if cota.atingiu_limite:
                raise CotaIAExcedida(
                    "Você atingiu seu limite mensal de utilização da IA."
                )

            # Executa a chamada à inteligência artificial
            resultado = responder(
                pergunta,
                modelo=modelo,
            )

            tokens_entrada = resultado["tokens_entrada"]
            tokens_saida = resultado["tokens_saida"]
            total_tokens = resultado["total_tokens"]
            identificador = resultado["identificador"]

            # Contabiliza o consumo real, mesmo que ultrapasse
            # ligeiramente o limite restante.
            cota.tokens_utilizados += total_tokens

            cota.save(update_fields=[
                "tokens_utilizados",
                "atualizado_em",
            ])

            status = "sucesso"

            return resultado["resposta"]

    except Exception as erro:
        mensagem_erro = str(erro)
        raise

    finally:
        duracao = int(
            (time.monotonic() - inicio) * 1000
        )

        # Registra a chamada para auditoria
        RegistroChamadaIA.objects.create(
            usuario=usuario,
            provedor="openai",
            modelo=modelo,
            tokens_entrada=tokens_entrada,
            tokens_saida=tokens_saida,
            total_tokens=total_tokens,
            status=status,
            mensagem_erro=mensagem_erro[:5000],
            identificador_resposta=identificador,
            duracao_ms=duracao,
        )
