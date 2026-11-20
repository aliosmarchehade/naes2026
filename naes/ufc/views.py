
from django.views.generic import (
    CreateView,
    UpdateView,
    DeleteView,
    ListView,
    DetailView,
    TemplateView
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Prefetch

from .models import Lutador, CategoriaPeso, Evento, Pais
from .filters import LutadorFilter, EventoFilter


# =========================
# CONTROLE DE ACESSO
# =========================

class GroupRequiredMixin(UserPassesTestMixin):

    group_required = None

    def test_func(self):

        if self.request.user.is_superuser:
            return True

        return self.request.user.groups.filter(
            name=self.group_required
        ).exists()


class AcessoPorProprietarioMixin:

    owner_field = None

    def get_queryset(self):

        queryset = super().get_queryset()
        usuario = self.request.user

        if usuario.is_superuser or usuario.groups.filter(
            name="Administradores"
        ).exists():
            return queryset

        return queryset.filter(**{
            self.owner_field: usuario
        })


# =========================
# MENSAGENS DE EXCLUSÃO
# =========================

class MensagemExclusaoMixin:

    mensagem_sucesso = "Registro excluído com sucesso!"

    def form_valid(self, form):

        response = super().form_valid(form)

        messages.success(
            self.request,
            self.mensagem_sucesso
        )

        return response


# =========================
# CREATES
# =========================

class LutadorCreate(
    LoginRequiredMixin,
    SuccessMessageMixin,
    CreateView
):

    model = Lutador

    fields = [
        'nome',
        'apelido',
        'foto',
        'pais',
        'idade',
        'peso',
        'categoria'
    ]

    template_name = 'ufc/form.html'
    success_url = reverse_lazy('lutador-list')
    success_message = "Lutador cadastrado com sucesso!"

    extra_context = {
        'titulo': 'Cadastro de Lutador',
        'botao': 'Cadastrar'
    }

    def form_valid(self, form):

        form.instance.cadastrado_por = self.request.user

        return super().form_valid(form)


class CategoriaPesoCreate(
    LoginRequiredMixin,
    SuccessMessageMixin,
    CreateView
):

    model = CategoriaPeso
    fields = ['nome', 'peso_maximo']

    template_name = 'ufc/form.html'
    success_url = reverse_lazy('categoria-list')
    success_message = "Categoria cadastrada com sucesso!"

    extra_context = {
        'titulo': 'Cadastro de Categoria de Peso',
        'botao': 'Criar Categoria'
    }


class EventoCreate(
    LoginRequiredMixin,
    SuccessMessageMixin,
    CreateView
):

    model = Evento

    fields = [
        'nome',
        'pais',
        'local',
        'data',
        'descricao'
    ]

    template_name = 'ufc/form.html'
    success_url = reverse_lazy('evento-list')
    success_message = "Evento cadastrado com sucesso!"

    extra_context = {
        'titulo': 'Cadastrar Evento',
        'botao': 'Cadastrar'
    }

    def form_valid(self, form):

        form.instance.usuario = self.request.user

        return super().form_valid(form)


class PaisCreate(
    LoginRequiredMixin,
    SuccessMessageMixin,
    CreateView
):

    model = Pais
    fields = ['nome', 'sigla']

    template_name = 'ufc/form.html'
    success_url = reverse_lazy('pais-list')
    success_message = "País cadastrado com sucesso!"

    extra_context = {
        'titulo': 'Cadastrar País',
        'botao': 'Cadastrar'
    }


# =========================
# UPDATES
# =========================

class LutadorUpdate(
    LoginRequiredMixin,
    AcessoPorProprietarioMixin,
    SuccessMessageMixin,
    UpdateView
):

    model = Lutador
    owner_field = 'cadastrado_por'

    fields = [
        'nome',
        'apelido',
        'foto',
        'pais',
        'idade',
        'peso',
        'categoria',
        'vitorias',
        'derrotas'
    ]

    template_name = 'ufc/form.html'
    success_url = reverse_lazy('lutador-list')
    success_message = "Lutador atualizado com sucesso!"

    extra_context = {
        'titulo': 'Editar Lutador',
        'botao': 'Atualizar'
    }


class CategoriaPesoUpdate(
    LoginRequiredMixin,
    SuccessMessageMixin,
    UpdateView
):

    model = CategoriaPeso
    fields = ['nome', 'peso_maximo']

    template_name = 'ufc/form.html'
    success_url = reverse_lazy('categoria-list')
    success_message = "Categoria atualizada com sucesso!"

    extra_context = {
        'titulo': 'Editar Categoria',
        'botao': 'Atualizar'
    }


class EventoUpdate(
    LoginRequiredMixin,
    AcessoPorProprietarioMixin,
    SuccessMessageMixin,
    UpdateView
):

    model = Evento
    owner_field = 'usuario'

    fields = [
        'nome',
        'pais',
        'local',
        'data',
        'descricao'
    ]

    template_name = 'ufc/form.html'
    success_url = reverse_lazy('evento-list')
    success_message = "Evento atualizado com sucesso!"

    extra_context = {
        'titulo': 'Editar Evento',
        'botao': 'Atualizar'
    }


class PaisUpdate(
    LoginRequiredMixin,
    SuccessMessageMixin,
    UpdateView
):

    model = Pais
    fields = ['nome', 'sigla']

    template_name = 'ufc/form.html'
    success_url = reverse_lazy('pais-list')
    success_message = "País atualizado com sucesso!"

    extra_context = {
        'titulo': 'Editar País',
        'botao': 'Atualizar'
    }


# =========================
# DELETES
# =========================

class LutadorDelete(
    LoginRequiredMixin,
    AcessoPorProprietarioMixin,
    MensagemExclusaoMixin,
    DeleteView
):

    model = Lutador
    owner_field = 'cadastrado_por'

    mensagem_sucesso = "Lutador excluído com sucesso!"

    template_name = 'ufc/form.html'
    success_url = reverse_lazy('lutador-list')

    extra_context = {
        'titulo': 'Excluir Lutador',
        'botao': 'Confirmar Exclusão'
    }


class CategoriaPesoDelete(
    LoginRequiredMixin,
    MensagemExclusaoMixin,
    DeleteView
):

    model = CategoriaPeso

    mensagem_sucesso = "Categoria excluída com sucesso!"

    template_name = 'ufc/form.html'
    success_url = reverse_lazy('categoria-list')

    extra_context = {
        'titulo': 'Excluir Categoria',
        'botao': 'Sim, excluir!'
    }


class EventoDelete(
    LoginRequiredMixin,
    AcessoPorProprietarioMixin,
    MensagemExclusaoMixin,
    DeleteView
):

    model = Evento
    owner_field = 'usuario'

    mensagem_sucesso = "Evento excluído com sucesso!"

    template_name = 'ufc/form.html'
    success_url = reverse_lazy('evento-list')

    extra_context = {
        'titulo': 'Excluir Evento',
        'botao': 'Sim, excluir!'
    }


class PaisDelete(
    LoginRequiredMixin,
    MensagemExclusaoMixin,
    DeleteView
):

    model = Pais

    mensagem_sucesso = "País excluído com sucesso!"

    template_name = 'ufc/form.html'
    success_url = reverse_lazy('pais-list')

    extra_context = {
        'titulo': 'Excluir País',
        'botao': 'Sim, excluir!'
    }


# =========================
# LISTS
# =========================

class LutadorList(
    LoginRequiredMixin,
    AcessoPorProprietarioMixin,
    ListView
):

    model = Lutador
    owner_field = 'cadastrado_por'

    template_name = 'ufc/list/lutador_list.html'
    context_object_name = 'lutadores'
    paginate_by = 10

    def get_queryset(self):

        queryset = super().get_queryset().select_related(
            'pais',
            'categoria'
        ).order_by('nome')

        self.filterset = LutadorFilter(
            self.request.GET,
            queryset=queryset
        )

        return self.filterset.qs

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset

        parametros = self.request.GET.copy()
        parametros.pop('page', None)

        context['querystring'] = parametros.urlencode()

        return context


class CategoriaPesoList(ListView):

    model = CategoriaPeso
    template_name = 'ufc/list/categoria_list.html'


class EventoList(
    LoginRequiredMixin,
    AcessoPorProprietarioMixin,
    ListView
):

    model = Evento
    owner_field = 'usuario'

    template_name = 'ufc/list/evento_list.html'
    context_object_name = 'eventos'
    paginate_by = 10

    def get_queryset(self):

        queryset = super().get_queryset().select_related(
            'pais',
            'usuario'
        ).order_by('data')

        self.filterset = EventoFilter(
            self.request.GET,
            queryset=queryset
        )

        return self.filterset.qs

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset

        parametros = self.request.GET.copy()
        parametros.pop('page', None)

        context['querystring'] = parametros.urlencode()

        return context


class PaisList(ListView):

    model = Pais
    template_name = 'ufc/list/pais_list.html'
    paginate_by = 10


# =========================
# DETAILS
# =========================

class LutadorDetail(
    LoginRequiredMixin,
    AcessoPorProprietarioMixin,
    DetailView
):

    model = Lutador
    owner_field = 'cadastrado_por'
    template_name = 'ufc/detail/lutador_detail.html'


class CategoriaPesoDetail(DetailView):

    model = CategoriaPeso
    template_name = 'ufc/detail/categoria_detail.html'


class EventoDetail(
    LoginRequiredMixin,
    AcessoPorProprietarioMixin,
    DetailView
):

    model = Evento
    owner_field = 'usuario'
    template_name = 'ufc/detail/evento_detail.html'


class PaisDetail(DetailView):

    model = Pais
    template_name = 'ufc/detail/pais_detail.html'


# =========================
# RANKING
# =========================

class RankingView(TemplateView):

    template_name = 'ufc/ranking.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        lutadores = Lutador.objects.select_related(
            'pais',
            'categoria'
        ).order_by(
            '-vitorias',
            'derrotas'
        )

        categorias = CategoriaPeso.objects.prefetch_related(
            Prefetch(
                'lutador_set',
                queryset=lutadores,
                to_attr='lutadores_ranking'
            )
        )

        ranking = []

        for categoria in categorias:

            ranking.append({
                'categoria': categoria,
                'lutadores': categoria.lutadores_ranking
            })

        context['ranking'] = ranking

        return context
