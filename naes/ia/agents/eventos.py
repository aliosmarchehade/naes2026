
from django.db.models import Q
from django.utils import timezone

from ufc.models import Evento, Luta


def buscar_eventos(nome=None, pais=None, limite=10):
    """Busca eventos por nome ou país."""

    queryset = Evento.objects.select_related(
        "pais", "usuario"
    )

    if nome:
        queryset = queryset.filter(nome__icontains=nome)

    if pais:
        queryset = queryset.filter(pais__nome__icontains=pais)

    limite = max(1, min(int(limite), 20))

    eventos = queryset.order_by("-data")[:limite]

    return [
        {
            "id": evento.id,
            "nome": evento.nome,
            "local": evento.local,
            "pais": evento.pais.nome if evento.pais else "Não informado",
            "data": evento.data.isoformat(),
            "descricao": evento.descricao,
        }
        for evento in eventos
    ]


def proximos_eventos(limite=5):
    """Retorna os eventos a partir da data atual."""

    hoje = timezone.localdate()

    eventos = Evento.objects.filter(
        data__gte=hoje
    ).select_related(
        "pais"
    ).order_by("data")[:max(1, min(int(limite), 20))]

    return [
        {
            "nome": evento.nome,
            "local": evento.local,
            "pais": evento.pais.nome if evento.pais else "Não informado",
            "data": evento.data.isoformat(),
        }
        for evento in eventos
    ]


def buscar_lutas(nome_evento=None, nome_lutador=None, limite=15):
    """Busca lutas por evento ou participante."""

    queryset = Luta.objects.select_related(
        "lutador_1",
        "lutador_2",
        "evento",
        "categoria",
        "vencedor",
    )

    if nome_evento:
        queryset = queryset.filter(
            evento__nome__icontains=nome_evento
        )

    if nome_lutador:
        queryset = queryset.filter(
            Q(lutador_1__nome__icontains=nome_lutador) |
            Q(lutador_2__nome__icontains=nome_lutador) |
            Q(lutador_1__apelido__icontains=nome_lutador) |
            Q(lutador_2__apelido__icontains=nome_lutador)
        )

    limite = max(1, min(int(limite), 30))

    lutas = queryset.order_by("-data_hora", "-id")[:limite]

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
        for luta in lutas
    ]


def detalhes_evento(evento_id):
    """Retorna os dados de um evento e suas lutas."""

    try:
        evento = Evento.objects.select_related(
            "pais"
        ).get(id=evento_id)
    except Evento.DoesNotExist:
        return None

    lutas = buscar_lutas(nome_evento=evento.nome, limite=30)

    return {
        "evento": {
            "id": evento.id,
            "nome": evento.nome,
            "local": evento.local,
            "pais": evento.pais.nome if evento.pais else "Não informado",
            "data": evento.data.isoformat(),
            "descricao": evento.descricao,
        },
        "lutas": lutas,
    }
