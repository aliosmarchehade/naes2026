from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.urls import reverse_lazy
from .models import Lutador, CategoriaPeso, Evento
# from django.contrib.auth.mixins import LoginRequiredMixin ##vou usar isso aqui pra qnd tiver opcao de login



## CREATES ##
class LutadorCreate(CreateView):
    model = Lutador
    fields = ['nome', 'apelido', 'idade', 'peso', 'categoria']
    template_name = 'ufc/form.html'
    success_url = reverse_lazy('lutador-list')

    extra_context = {
        'titulo': 'Cadastro de Lutador',
        'botao': 'Cadastrar'
    }

    def form_valid(self, form):
        return super().form_valid(form)


class CategoriaPesoCreate(CreateView):
    model = CategoriaPeso
    fields = ['nome', 'peso_maximo']
    template_name = 'ufc/form.html'
    success_url = reverse_lazy('categoria-list')

    extra_context = {
        'titulo': 'Cadastro de Categoria de Peso',
        'botao': 'Criar Categoria'
    }

class EventoCreate(CreateView):
    model = Evento
    fields = ['nome', 'local', 'data', 'descricao']
    template_name = 'ufc/form.html'
    success_url = reverse_lazy('evento-list')

    extra_context = {
        'titulo': 'Cadastrar Evento',
        'botao': 'Cadastrar'
    }

## UPDATES ##
class LutadorUpdate(UpdateView):
    model = Lutador
    fields = ['nome', 'apelido', 'idade', 'peso', 'categoria', 'vitorias', 'derrotas']
    template_name = 'ufc/form.html'
    success_url = reverse_lazy('lutador-list')

    extra_context = {
        'titulo': 'Editar Lutador',
        'botao': 'Atualizar'
    }

class CategoriaPesoUpdate(UpdateView):
    model = CategoriaPeso
    fields = ['nome', 'peso_maximo']
    template_name = 'ufc/form.html'
    success_url = reverse_lazy('categoria-list')

    extra_context = {
        'titulo': 'Editar Categoria',
        'botao': 'Atualizar'
    }

class EventoUpdate(UpdateView):
    model = Evento
    fields = ['nome', 'local', 'data', 'descricao']
    template_name = 'ufc/form.html'
    success_url = reverse_lazy('evento-list')

    extra_context = {
        'titulo': 'Editar Evento',
        'botao': 'Atualizar'
    }

## DELETES ##
class LutadorDelete(DeleteView):
    model = Lutador
    template_name = 'ufc/form.html'
    success_url = reverse_lazy('lutador-list')

    extra_context = {
        'titulo': 'Excluir Lutador',
        'botao': 'Confirmar Exclusão'
    }

class CategoriaPesoDelete(DeleteView):
    model = CategoriaPeso
    template_name = 'ufc/form.html'
    success_url = reverse_lazy('categoria-list')

    extra_context = {
        'titulo': 'Excluir Categoria',
        'botao': 'Sim, excluir!'
    }

class EventoDelete(DeleteView):
    model = Evento
    template_name = 'ufc/form.html'
    success_url = reverse_lazy('evento-list')

    extra_context = {
        'titulo': 'Excluir Evento',
        'botao': 'Sim, excluir!'
    }

## LISTS ##
class LutadorList(ListView):
    model = Lutador
    template_name = 'ufc/list/lutador_list.html'
    context_object_name = 'lutadores'
    paginate_by = 10


class CategoriaPesoList(ListView):
    model = CategoriaPeso
    template_name = 'ufc/list/categoria_list.html'

    
class EventoList(ListView):
    model = Evento
    template_name = 'ufc/list/evento_list.html'


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