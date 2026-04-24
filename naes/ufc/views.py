from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.urls import reverse_lazy
from .models import Lutador


# CREATE
class LutadorCreate(CreateView):
    model = Lutador
    fields = ['nome', 'apelido', 'idade', 'peso', 'categoria']
    template_name = 'form.html'
    success_url = reverse_lazy('lutador-list')

    extra_context = {
        'titulo': 'Cadastro de Lutador',
        'botao': 'Cadastrar'
    }

    def form_valid(self, form):
        form.instance.cadastrado_por = self.request.user
        return super().form_valid(form)


# UPDATE
class LutadorUpdate(UpdateView):
    model = Lutador
    fields = ['nome', 'apelido', 'idade', 'peso', 'categoria', 'vitorias', 'derrotas']
    template_name = 'form.html'
    success_url = reverse_lazy('lutador-list')

    extra_context = {
        'titulo': 'Editar Lutador',
        'botao': 'Atualizar'
    }


# DELETE
class LutadorDelete(DeleteView):
    model = Lutador
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('lutador-list')

    extra_context = {
        'titulo': 'Excluir Lutador',
        'botao': 'Confirmar Exclusão'
    }


# LIST
class LutadorList(ListView):
    model = Lutador
    template_name = 'lutador_list.html'
    context_object_name = 'lutadores'
    paginate_by = 10


# DETAIL
class LutadorDetail(DetailView):
    model = Lutador
    template_name = 'lutador_detail.html'