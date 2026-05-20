from django.views.generic import TemplateView
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from ufc.models import Lutador, Evento

class IndexView(TemplateView):

    template_name = "website/index.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        # ÚLTIMOS LUTADORES
        context['ultimos_lutadores'] = Lutador.objects.order_by(
            '-cadastrado_em'
        )[:5]

        # ÚLTIMOS EVENTOS
        context['ultimos_eventos'] = Evento.objects.order_by(
            '-id'
        )[:5]

        # TOTAL DE LUTADORES
        context['total_lutadores'] = Lutador.objects.count()

        # TOTAL DE EVENTOS
        context['total_eventos'] = Evento.objects.count()

        # SE USUÁRIO ESTIVER LOGADO
        if self.request.user.is_authenticated:

            context['meus_lutadores'] = Lutador.objects.filter(
                cadastrado_por=self.request.user
            ).count()

            context['meus_eventos'] = Evento.objects.filter(
                usuario=self.request.user
            ).count()

        return context

class ContatoView(TemplateView):
    template_name = "website/contato.html"

class SobreView(TemplateView):
    template_name = "website/sobre.html"

class RegistrarUsuario(CreateView):
    form_class = UserCreationForm
    template_name = 'usuarios/register.html'
    success_url = reverse_lazy('login')