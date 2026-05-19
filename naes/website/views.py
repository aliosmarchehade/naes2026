from django.views.generic import TemplateView
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy


class IndexView(TemplateView):
    template_name = "website/index.html"

class ContatoView(TemplateView):
    template_name = "website/contato.html"

class SobreView(TemplateView):
    template_name = "website/sobre.html"

class RegistrarUsuario(CreateView):
    form_class = UserCreationForm
    template_name = 'usuarios/register.html'
    success_url = reverse_lazy('login')