
from django.db.models import Q
from ufc.models import Lutador, Luta


def _dados_lutador(lutador):
    """Organiza os dados de um lutador para a IA."""

    return {
        "id": lutador.id,
        "nome": lutador.nome,
        "apelido": lutador.apelido,
        "idade": lutador.idade,
        "peso": str(lutador.peso),
        "categoria": lutador.categoria.nome,
        "pais": lutador.pais.nome if lutador.pais else "Não informado",
        "vitorias": lutador.vitorias,
        "derrotas": lutador.derrotas,
    }


def buscar_lutadores(nome=None, categoria=None, pais=None, limite=10):
    """Busca lutadores por nome, categoria ou país."""

    queryset = Lutador.objects.select_related(
        "categoria", "pais"
    )

    if nome:
        queryset = queryset.filter(
            Q(nome__icontains=nome) |
            Q(apelido__icontains=nome)
        )

    if categoria:
        queryset = queryset.filter(
            categoria__nome__icontains=categoria
        )

    if pais:
        queryset = queryset.filter(
            pais__nome__icontains=pais
        )

    limite = max(1, min(int(limite), 20))

    return [
        _dados_lutador(lutador)
        for lutador in queryset.order_by("nome")[:limite]
    ]


def ranking_lutadores(criterio="vitorias", limite=5):
    """Retorna o ranking de lutadores."""

    criterios_validos = {
        "vitorias",
        "derrotas",
        "idade",
        "peso",
    }

    if criterio not in criterios_validos:
        criterio = "vitorias"

    limite = max(1, min(int(limite), 20))

    queryset = Lutador.objects.select_related(
        "categoria", "pais"
    ).order_by(f"-{criterio}", "nome")

    return [
        _dados_lutador(lutador)
        for lutador in queryset[:limite]
    ]


def comparar_lutadores(nome_1, nome_2):
    """Compara dois lutadores cadastrados."""

    def localizar(nome):
        return Lutador.objects.select_related(
            "categoria", "pais"
        ).filter(
            Q(nome__icontains=nome) |
            Q(apelido__icontains=nome)
        ).first()

    lutador_1 = localizar(nome_1)
    lutador_2 = localizar(nome_2)

    return {
        "lutador_1": (
            _dados_lutador(lutador_1) if lutador_1 else None
        ),
        "lutador_2": (
            _dados_lutador(lutador_2) if lutador_2 else None
        ),
    }


def historico_lutas(nome_lutador, limite=10):
    """Consulta o histórico de lutas de um lutador."""

    lutas = Luta.objects.filter(
        Q(lutador_1__nome__icontains=nome_lutador) |
        Q(lutador_1__apelido__icontains=nome_lutador) |
        Q(lutador_2__nome__icontains=nome_lutador) |
        Q(lutador_2__apelido__icontains=nome_lutador)
    ).select_related(
        "lutador_1",
        "lutador_2",
        "evento",
        "categoria",
        "vencedor",
    ).order_by("-data_hora", "-id")

    limite = max(1, min(int(limite), 20))

    return [
        {
            "lutador_1": luta.lutador_1.nome,
            "lutador_2": luta.lutador_2.nome,
            "evento": luta.evento.nome,
            "data": (
                luta.data_hora.isoformat()
                if luta.data_hora else None
            ),
            "categoria": luta.categoria.nome,
            "resultado": luta.resultado or "Não informado",
            "vencedor": (
                luta.vencedor.nome if luta.vencedor else "Não definido"
            ),
        }
        for luta in lutas[:limite]
    ]
