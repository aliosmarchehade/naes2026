
import django_filters
from django import forms
from .models import Lutador, Evento, CategoriaPeso, Pais


class LutadorFilter(django_filters.FilterSet):

    nome = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Nome do lutador',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o nome'
        })
    )

    apelido = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Apelido',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o apelido'
        })
    )

    categoria = django_filters.ModelChoiceFilter(
        queryset=CategoriaPeso.objects.all(),
        lookup_expr='exact',
        label='Categoria'
    )

    idade_min = django_filters.NumberFilter(
        field_name='idade',
        lookup_expr='gte',
        label='Idade mínima',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Idade mínima'
        })
    )

    idade_max = django_filters.NumberFilter(
        field_name='idade',
        lookup_expr='lte',
        label='Idade máxima',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Idade máxima'
        })
    )

    class Meta:
        model = Lutador
        fields = []


class EventoFilter(django_filters.FilterSet):

    nome = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Nome do evento',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o nome do evento'
        })
    )

    pais = django_filters.ModelChoiceFilter(
        queryset=Pais.objects.all(),
        lookup_expr='exact',
        label='País'
    )

    data_inicio = django_filters.DateFilter(
        field_name='data',
        lookup_expr='gte',
        label='Data inicial',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    data_fim = django_filters.DateFilter(
        field_name='data',
        lookup_expr='lte',
        label='Data final',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    class Meta:
        model = Evento
        fields = []
