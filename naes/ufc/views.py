from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.urls import reverse_lazy
from .models import Lutador, CategoriaPeso, Evento, Pais
from django.contrib.auth.mixins import LoginRequiredMixin
# from django.contrib.auth.mixins import LoginRequiredMixin ##vou usar isso aqui pra qnd tiver opcao de login



## CREATES ##
class LutadorCreate(LoginRequiredMixin, CreateView):
    model = Lutador
    fields = ['nome', 'apelido', 'pais', 'idade', 'peso', 'categoria']
    template_name = 'ufc/form.html'
    success_url = reverse_lazy('lutador-list')

    extra_context = {
        'titulo': 'Cadastro de Lutador',
        'botao': 'Cadastrar'
    }

    def form_valid(self, form):
        form.instance.cadastrado_por = self.request.user
        return super().form_valid(form)


class CategoriaPesoCreate(LoginRequiredMixin, CreateView):
    model = CategoriaPeso
    fields = ['nome', 'peso_maximo']
    template_name = 'ufc/form.html'
    success_url = reverse_lazy('categoria-list')

    extra_context = {
        'titulo': 'Cadastro de Categoria de Peso',
        'botao': 'Criar Categoria'
    }

class EventoCreate(LoginRequiredMixin, CreateView):
    model = Evento
    fields = ['nome', 'pais', 'local', 'data', 'descricao']
    template_name = 'ufc/form.html'
    success_url = reverse_lazy('evento-list')

    extra_context = {
        'titulo': 'Cadastrar Evento',
        'botao': 'Cadastrar'
    }

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)

class PaisCreate(LoginRequiredMixin, CreateView):
    model = Pais
    fields = ['nome', 'sigla']
    template_name = 'ufc/form.html'
    success_url = reverse_lazy('pais-list')

    extra_context = {
        'titulo': 'Cadastrar País',
        'botao': 'Cadastrar'
    }

## UPDATES ##
class LutadorUpdate(LoginRequiredMixin, UpdateView):
    model = Lutador
    def get_queryset(self):

        if self.request.user.is_superuser:
            return Lutador.objects.all()

        return Lutador.objects.filter(
            cadastrado_por=self.request.user
    )
    fields = ['nome', 'apelido', 'pais' , 'idade', 'peso', 'categoria', 'vitorias', 'derrotas']
    template_name = 'ufc/form.html'
    success_url = reverse_lazy('lutador-list')

    extra_context = {
        'titulo': 'Editar Lutador',
        'botao': 'Atualizar'
    }

class CategoriaPesoUpdate(LoginRequiredMixin, UpdateView):
    model = CategoriaPeso
    fields = ['nome', 'peso_maximo']
    template_name = 'ufc/form.html'
    success_url = reverse_lazy('categoria-list')

    extra_context = {
        'titulo': 'Editar Categoria',
        'botao': 'Atualizar'
    }

class EventoUpdate(LoginRequiredMixin, UpdateView):
    model = Evento
    fields = ['nome', 'pais','local', 'data', 'descricao']
    template_name = 'ufc/form.html'
    success_url = reverse_lazy('evento-list')

    extra_context = {
        'titulo': 'Editar Evento',
        'botao': 'Atualizar'
    }

    def get_queryset(self):

        if self.request.user.is_superuser:
            return Evento.objects.all()

        return Evento.objects.filter(
            usuario=self.request.user
        )


class PaisUpdate(LoginRequiredMixin, UpdateView):
    model = Pais
    fields = ['nome', 'sigla']
    template_name = 'ufc/form.html'
    success_url = reverse_lazy('pais-list')

    extra_context = {
        'titulo': 'Editar País',
        'botao': 'Atualizar'
    }

## DELETES ##
class LutadorDelete(LoginRequiredMixin, DeleteView):
    model = Lutador

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Lutador.objects.all()

        return Lutador.objects.filter(
            cadastrado_por=self.request.user
        )
    template_name = 'ufc/form.html'
    success_url = reverse_lazy('lutador-list')

    extra_context = {
        'titulo': 'Excluir Lutador',
        'botao': 'Confirmar Exclusão'
    }

class CategoriaPesoDelete(LoginRequiredMixin, DeleteView):
    model = CategoriaPeso
    template_name = 'ufc/form.html'
    success_url = reverse_lazy('categoria-list')

    extra_context = {
        'titulo': 'Excluir Categoria',
        'botao': 'Sim, excluir!'
    }

class EventoDelete(LoginRequiredMixin, DeleteView):
    model = Evento
    template_name = 'ufc/form.html'
    success_url = reverse_lazy('evento-list')

    extra_context = {
        'titulo': 'Excluir Evento',
        'botao': 'Sim, excluir!'
    }

    def get_queryset(self):

        if self.request.user.is_superuser:
            return Evento.objects.all()

        return Evento.objects.filter(
            usuario=self.request.user
        )

class PaisDelete(LoginRequiredMixin, DeleteView):
    model = Pais
    template_name = 'ufc/form.html'
    success_url = reverse_lazy('pais-list')

    extra_context = {
        'titulo': 'Excluir País',
        'botao': 'Sim, excluir!'
    }

## LISTS ##
class LutadorList(ListView):
    model = Lutador
    template_name = 'ufc/list/lutador_list.html'
    context_object_name = 'lutadores'   


class CategoriaPesoList(ListView):
    model = CategoriaPeso
    template_name = 'ufc/list/categoria_list.html'

    
class EventoList(ListView):
    model = Evento
    template_name = 'ufc/list/evento_list.html'


class PaisList(ListView):
    model = Pais
    template_name = 'ufc/list/pais_list.html'


## DETAIL ##
class LutadorDetail(DetailView):
    model = Lutador
    template_name = 'ufc/detail/lutador_detail.html'

class CategoriaPesoDetail(DetailView):
    model = CategoriaPeso
    template_name = 'ufc/detail/categoria_detail.html'

class EventoDetail(DetailView):
    model = Evento
    template_name = 'ufc/detail/evento_detail.html'

class PaisDetail(DetailView):
    model = Pais
    template_name = 'ufc/detail/pais_detail.html'