
import json

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


# Associação entre as ferramentas da IA e as funções Python
FUNCOES = {
    "buscar_lutadores": buscar_lutadores,
    "ranking_lutadores": ranking_lutadores,
    "comparar_lutadores": comparar_lutadores,
    "historico_lutas": historico_lutas,
    "buscar_eventos": buscar_eventos,
    "proximos_eventos": proximos_eventos,
    "buscar_lutas": buscar_lutas,
}


def responder(pergunta):
    """Processa uma pergunta utilizando os agentes e a OpenAI."""

    if not settings.OPENAI_API_KEY:
        raise ValueError("A chave da API da OpenAI não foi configurada.")

    cliente = OpenAI(api_key=settings.OPENAI_API_KEY)

    instrucoes = """
    Você é o assistente virtual oficial do NAES,
    um sistema de gerenciamento de eventos e lutadores de MMA.

    Você possui ferramentas para consultar os dados cadastrados no sistema.

    REGRAS:
    1. Utilize as ferramentas disponíveis para responder perguntas
       sobre lutadores, rankings, eventos e lutas.
    2. Não invente nomes, resultados, estatísticas ou datas.
    3. Não afirme que uma informação existe sem consultar o banco.
    4. Se não encontrar registros, informe isso claramente.
    5. Não invente informações que não estejam disponíveis nas consultas.
    6. Responda em português brasileiro.
    7. Organize as respostas de maneira clara e objetiva.
    8. Você não pode cadastrar, editar ou excluir dados.
    9. Quando comparar lutadores, utilize somente os dados retornados
       pelas ferramentas.
    10. Deixe claro quando uma informação não estiver cadastrada.
    """

    resposta = cliente.responses.create(
        model=settings.OPENAI_MODEL,
        instructions=instrucoes,
        input=pergunta,
        tools=FERRAMENTAS,
    )

    # Permite que a IA execute as ferramentas necessárias
    for tentativa in range(5):

        chamadas = [
            item for item in resposta.output
            if item.type == "function_call"
        ]

        if not chamadas:
            return resposta.output_text

        resultados = []

        for chamada in chamadas:
            funcao = FUNCOES.get(chamada.name)

            if not funcao:
                resultado = {"erro": "Ferramenta não disponível."}
            else:
                try:
                    argumentos = json.loads(chamada.arguments)
                    resultado = funcao(**argumentos)

                except (TypeError, ValueError, json.JSONDecodeError):
                    resultado = {
                        "erro": "Não foi possível processar os argumentos."
                    }

            resultados.append({
                "type": "function_call_output",
                "call_id": chamada.call_id,
                "output": json.dumps(
                    resultado,
                    ensure_ascii=False,
                    default=str
                ),
            })

        resposta = cliente.responses.create(
            model=settings.OPENAI_MODEL,
            instructions=instrucoes,
            previous_response_id=resposta.id,
            input=resultados,
            tools=FERRAMENTAS,
        )

    return "Não consegui concluir a consulta. Tente reformular sua pergunta."
