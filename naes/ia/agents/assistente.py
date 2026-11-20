
import json
from pathlib import Path

from django.conf import settings
from openai import OpenAI

from .lutadores import (
    buscar_lutadores,
    ranking_lutadores,
    comparar_lutadores,
    historico_lutas,
)

from .eventos import (
    buscar_eventos,
    proximos_eventos,
    buscar_lutas,
)


# Ferramentas disponíveis para a IA
FERRAMENTAS = [
    {
        "type": "function",
        "name": "buscar_lutadores",
        "description": "Busca lutadores cadastrados por nome, categoria ou país.",
        "parameters": {
            "type": "object",
            "properties": {
                "nome": {"type": ["string", "null"]},
                "categoria": {"type": ["string", "null"]},
                "pais": {"type": ["string", "null"]},
                "limite": {"type": "integer"},
            },
            "required": ["nome", "categoria", "pais", "limite"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "ranking_lutadores",
        "description": "Gera rankings por vitórias, derrotas, idade ou peso.",
        "parameters": {
            "type": "object",
            "properties": {
                "criterio": {
                    "type": "string",
                    "enum": ["vitorias", "derrotas", "idade", "peso"],
                },
                "limite": {"type": "integer"},
            },
            "required": ["criterio", "limite"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "comparar_lutadores",
        "description": "Compara dois lutadores cadastrados.",
        "parameters": {
            "type": "object",
            "properties": {
                "nome_1": {"type": "string"},
                "nome_2": {"type": "string"},
            },
            "required": ["nome_1", "nome_2"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "historico_lutas",
        "description": "Consulta o histórico de lutas de um lutador.",
        "parameters": {
            "type": "object",
            "properties": {
                "nome_lutador": {"type": "string"},
                "limite": {"type": "integer"},
            },
            "required": ["nome_lutador", "limite"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "buscar_eventos",
        "description": "Busca eventos cadastrados por nome ou país.",
        "parameters": {
            "type": "object",
            "properties": {
                "nome": {"type": ["string", "null"]},
                "pais": {"type": ["string", "null"]},
                "limite": {"type": "integer"},
            },
            "required": ["nome", "pais", "limite"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "proximos_eventos",
        "description": "Consulta os próximos eventos cadastrados a partir da data atual.",
        "parameters": {
            "type": "object",
            "properties": {
                "limite": {"type": "integer"},
            },
            "required": ["limite"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "buscar_lutas",
        "description": "Busca lutas por evento ou nome de participante.",
        "parameters": {
            "type": "object",
            "properties": {
                "nome_evento": {"type": ["string", "null"]},
                "nome_lutador": {"type": ["string", "null"]},
                "limite": {"type": "integer"},
            },
            "required": ["nome_evento", "nome_lutador", "limite"],
            "additionalProperties": False,
        },
    },
]


# Associação entre as ferramentas e as funções Python
FUNCOES = {
    "buscar_lutadores": buscar_lutadores,
    "ranking_lutadores": ranking_lutadores,
    "comparar_lutadores": comparar_lutadores,
    "historico_lutas": historico_lutas,
    "buscar_eventos": buscar_eventos,
    "proximos_eventos": proximos_eventos,
    "buscar_lutas": buscar_lutas,
}


def carregar_contexto():
    """Carrega as instruções do assistente a partir do arquivo Markdown."""

    caminho = Path(__file__).with_name("contexto_projeto.md")

    try:
        return caminho.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Arquivo de contexto não encontrado: {caminho}"
        )


def responder(pergunta, modelo=None):
    """Processa uma pergunta utilizando os agentes e a OpenAI."""

    if not settings.OPENAI_API_KEY:
        raise ValueError("A chave da API da OpenAI não foi configurada.")

    modelo = modelo or settings.OPENAI_MODEL

    cliente = OpenAI(api_key=settings.OPENAI_API_KEY)

    tokens_entrada = 0
    tokens_saida = 0
    identificador = ""

    # Carrega as instruções externas do projeto
    instrucoes = carregar_contexto()

    # Primeira chamada à OpenAI
    resposta = cliente.responses.create(
        model=modelo,
        instructions=instrucoes,
        input=pergunta,
        tools=FERRAMENTAS,
    )

    # Permite que a IA execute as ferramentas necessárias
    for tentativa in range(5):

        if resposta.usage:
            tokens_entrada += resposta.usage.input_tokens
            tokens_saida += resposta.usage.output_tokens

        identificador = resposta.id

        chamadas = [
            item for item in resposta.output
            if item.type == "function_call"
        ]

        # Se não houver ferramentas, retorna a resposta final
        if not chamadas:
            return {
                "resposta": resposta.output_text or (
                    "Não foi possível gerar uma resposta."
                ),
                "tokens_entrada": tokens_entrada,
                "tokens_saida": tokens_saida,
                "total_tokens": tokens_entrada + tokens_saida,
                "identificador": identificador,
            }

        resultados = []

        for chamada in chamadas:
            funcao = FUNCOES.get(chamada.name)

            if not funcao:
                resultado = {
                    "erro": "Ferramenta não disponível."
                }
            else:
                try:
                    argumentos = json.loads(chamada.arguments)
                    resultado = funcao(**argumentos)

                except (TypeError, ValueError, json.JSONDecodeError):
                    resultado = {
                        "erro": "Não foi possível processar os argumentos."
                    }

                except Exception:
                    resultado = {
                        "erro": "Ocorreu um erro ao consultar os dados."
                    }

            resultados.append({
                "type": "function_call_output",
                "call_id": chamada.call_id,
                "output": json.dumps(
                    resultado,
                    ensure_ascii=False,
                    default=str,
                ),
            })

        # Envia os resultados das ferramentas para a OpenAI
        resposta = cliente.responses.create(
            model=modelo,
            instructions=instrucoes,
            previous_response_id=resposta.id,
            input=resultados,
            tools=FERRAMENTAS,
        )

    # Caso o limite de ciclos seja atingido
    return {
        "resposta": (
            "Não consegui concluir a consulta. "
            "Tente reformular sua pergunta."
        ),
        "tokens_entrada": tokens_entrada,
        "tokens_saida": tokens_saida,
        "total_tokens": tokens_entrada + tokens_saida,
        "identificador": identificador,
    }
