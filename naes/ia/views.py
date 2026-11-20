
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.utils import timezone
from django.db import transaction

from openai import (
    OpenAI,
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
    APIError,
)

from .forms import ConfiguracaoIAForm
from .models import (
    ConfiguracaoIA,
    CotaMensalIA,
    RegistroChamadaIA,
    ConversaIA,
    MensagemIA,
)
from .services import chamar_ia, CotaIAExcedida


def usuario_administrador(user):
    return user.is_authenticated and user.is_staff


@login_required
def assistente(request):
    # Recupera a conversa ativa da sessão.
    conversa_id = request.session.get("conversa_ia_id")

    conversa = None

    if conversa_id:
        conversa = ConversaIA.objects.filter(
            pk=conversa_id,
            usuario=request.user,
        ).first()

    # Se a sessão não tiver uma conversa válida,
    # recupera a conversa mais recente do usuário.
    if conversa is None:
        conversa = ConversaIA.objects.filter(
            usuario=request.user
        ).first()

        if conversa:
            request.session["conversa_ia_id"] = conversa.pk

    if request.method == "POST":
        pergunta = request.POST.get("pergunta", "").strip()

        if not pergunta:
            messages.warning(request, "Digite uma pergunta.")
            return redirect("ia:assistente")

        try:
            resposta = chamar_ia(
                usuario=request.user,
                pergunta=pergunta,
            )

            # Persiste a conversa e suas mensagens.
            with transaction.atomic():

                if conversa is None:
                    conversa = ConversaIA.objects.create(
                        usuario=request.user,
                        titulo=pergunta[:200],
                    )

                elif not conversa.mensagens.exists():
                    conversa.titulo = pergunta[:200]
                    conversa.save(update_fields=["titulo", "atualizada_em"])

                MensagemIA.objects.create(
                    conversa=conversa,
                    tipo="usuario",
                    conteudo=pergunta,
                )

                MensagemIA.objects.create(
                    conversa=conversa,
                    tipo="ia",
                    conteudo=resposta,
                )

            request.session["conversa_ia_id"] = conversa.pk

            messages.success(
                request,
                "Resposta recebida com sucesso."
            )

        except CotaIAExcedida as erro:
            messages.warning(request, str(erro))

        except AuthenticationError:
            messages.error(
                request,
                "Não foi possível autenticar com a OpenAI. Verifique sua chave."
            )

        except RateLimitError:
            messages.error(
                request,
                "A API da OpenAI está sem créditos disponíveis ou atingiu seu limite."
            )

        except APIConnectionError:
            messages.error(
                request,
                "Não foi possível conectar à API da OpenAI."
            )

        except APIError:
            messages.error(
                request,
                "Ocorreu um erro ao consultar a inteligência artificial."
            )

        except ValueError as erro:
            messages.error(request, str(erro))

        except Exception:
            messages.error(
                request,
                "Ocorreu um erro inesperado ao processar sua pergunta."
            )

        return redirect("ia:assistente")

    # Recupera o histórico diretamente do banco.
    historico = []

    if conversa:
        historico = [
            {
                "tipo": mensagem.tipo,
                "mensagem": mensagem.conteudo,
            }
            for mensagem in conversa.mensagens.all()
        ]

    return render(request, "ia/assistente.html", {
        "historico": historico,
        "conversa": conversa,
    })


@login_required
@user_passes_test(usuario_administrador)
def configuracao(request):
    configuracao_ia = ConfiguracaoIA.objects.first()

    if configuracao_ia is None:
        configuracao_ia = ConfiguracaoIA.objects.create()

    if request.method == "POST":
        form = ConfiguracaoIAForm(
            request.POST,
            instance=configuracao_ia,
        )

        if form.is_valid():
            configuracao_ia = form.save(commit=False)
            configuracao_ia.atualizado_por = request.user
            configuracao_ia.save()

            messages.success(
                request,
                "Configurações da IA atualizadas com sucesso."
            )

            return redirect("ia:configuracao")

    else:
        form = ConfiguracaoIAForm(instance=configuracao_ia)

    return render(
        request,
        "ia/configuracao.html",
        {
            "form": form,
            "configuracao": configuracao_ia,
        }
    )


@login_required
@user_passes_test(usuario_administrador)
@require_POST
def testar_conexao(request):
    configuracao_ia = ConfiguracaoIA.objects.first()

    if configuracao_ia is None:
        messages.error(
            request,
            "Salve as configurações antes de testar a conexão."
        )
        return redirect("ia:configuracao")

    if not settings.OPENAI_API_KEY:
        messages.error(
            request,
            "A chave da API não está configurada no ambiente."
        )
        return redirect("ia:configuracao")

    try:
        cliente = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=15.0,
            max_retries=0,
        )

        cliente.models.retrieve(configuracao_ia.modelo)

        messages.success(
            request,
            f"Conexão realizada com sucesso! "
            f"O modelo {configuracao_ia.modelo} está acessível."
        )

    except AuthenticationError:
        messages.error(
            request,
            "Falha de autenticação. Verifique a chave da OpenAI."
        )

    except RateLimitError:
        messages.error(
            request,
            "A OpenAI recusou a solicitação por limite de requisições ou créditos."
        )

    except APIConnectionError:
        messages.error(
            request,
            "Não foi possível estabelecer conexão com a OpenAI."
        )

    except APIError as erro:
        messages.error(
            request,
            f"Erro retornado pela OpenAI: {str(erro)[:300]}"
        )

    except Exception as erro:
        messages.error(
            request,
            f"Não foi possível testar a conexão: {str(erro)[:300]}"
        )

    return redirect("ia:configuracao")


# ==========================================================
# AUDITORIA DAS CHAMADAS DA IA
# ==========================================================

@login_required
@user_passes_test(usuario_administrador)
def auditoria(request):
    registros = RegistroChamadaIA.objects.select_related(
        "usuario"
    ).order_by("-criado_em")

    status = request.GET.get("status", "").strip()
    busca = request.GET.get("busca", "").strip()

    if status in ["sucesso", "erro"]:
        registros = registros.filter(status=status)

    if busca:
        registros = registros.filter(
            usuario__username__icontains=busca
        ) | registros.filter(
            modelo__icontains=busca
        )

    total_chamadas = registros.count()
    total_tokens = sum(
        registros.values_list("total_tokens", flat=True)
    )
    chamadas_com_erro = registros.filter(status="erro").count()

    paginator = Paginator(registros, 25)
    pagina = paginator.get_page(request.GET.get("pagina"))

    return render(
        request,
        "ia/auditoria.html",
        {
            "registros": pagina,
            "pagina": pagina,
            "total_chamadas": total_chamadas,
            "total_tokens": total_tokens,
            "chamadas_com_erro": chamadas_com_erro,
            "filtro_status": status,
            "busca": busca,
        }
    )


# ==========================================================
# GESTÃO DE USUÁRIOS E COTAS
# ==========================================================

@login_required
@user_passes_test(usuario_administrador)
def usuarios(request):
    Usuario = get_user_model()
    hoje = timezone.localdate()

    lista_usuarios = Usuario.objects.filter(
        is_active=True
    ).order_by("username")

    cotas = {
        cota.usuario_id: cota
        for cota in CotaMensalIA.objects.filter(
            ano=hoje.year,
            mes=hoje.month,
            usuario__in=lista_usuarios,
        )
    }

    dados_usuarios = []

    for usuario in lista_usuarios:
        cota = cotas.get(usuario.pk)

        if cota is None:
            limite = 100000
            utilizados = 0
            restante = limite
            percentual = 0
        else:
            limite = cota.limite_tokens
            utilizados = cota.tokens_utilizados
            restante = cota.tokens_restantes
            percentual = cota.percentual_utilizado

        dados_usuarios.append({
            "usuario": usuario,
            "limite": limite,
            "utilizados": utilizados,
            "restante": restante,
            "percentual": percentual,
        })

    return render(
        request,
        "ia/usuarios.html",
        {
            "usuarios": dados_usuarios,
            "mes_atual": hoje.month,
            "ano_atual": hoje.year,
        }
    )


@login_required
@user_passes_test(usuario_administrador)
@require_POST
def atualizar_cota(request, usuario_id):
    Usuario = get_user_model()
    usuario = get_object_or_404(Usuario, pk=usuario_id)

    try:
        limite = int(request.POST.get("limite_tokens", ""))

        if limite < 1:
            raise ValueError

    except (ValueError, TypeError):
        messages.error(
            request,
            "Informe um limite mensal válido, maior que zero."
        )
        return redirect("ia:usuarios")

    hoje = timezone.localdate()

    CotaMensalIA.objects.update_or_create(
        usuario=usuario,
        ano=hoje.year,
        mes=hoje.month,
        defaults={
            "limite_tokens": limite,
        }
    )

    messages.success(
        request,
        f"Cota mensal de {usuario.username} atualizada com sucesso."
    )

    return redirect("ia:usuarios")
