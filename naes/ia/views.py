
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from openai import (
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
    APIError,
)

from .agents.assistente import responder


@login_required
def assistente(request):
    historico = request.session.get('historico_ia', [])

    if request.method == 'POST':
        pergunta = request.POST.get('pergunta', '').strip()

        if not pergunta:
            messages.warning(request, 'Digite uma pergunta.')
            return redirect('ia:assistente')

        try:
            resposta = responder(pergunta)

            historico.append({
                'tipo': 'usuario',
                'mensagem': pergunta,
            })

            historico.append({
                'tipo': 'ia',
                'mensagem': resposta,
            })

            request.session['historico_ia'] = historico[-30:]

        except RateLimitError:
            messages.error(
                request,
                'A API da OpenAI está sem créditos disponíveis.'
            )

        except AuthenticationError:
            messages.error(
                request,
                'Não foi possível autenticar com a OpenAI. Verifique sua chave.'
            )

        except APIConnectionError:
            messages.error(
                request,
                'Não foi possível conectar à API da OpenAI.'
            )

        except APIError:
            messages.error(
                request,
                'Ocorreu um erro ao consultar a inteligência artificial.'
            )

        except Exception:
            messages.error(
                request,
                'Ocorreu um erro inesperado ao processar sua pergunta.'
            )

        return redirect('ia:assistente')

    return render(request, 'ia/assistente.html', {
        'historico': historico,
    })
