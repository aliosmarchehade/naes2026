from django.urls import path
from .views import *

urlpatterns = [
    path('lutadores/', LutadorList.as_view(), name='lutador-list'),
    path('lutadores/novo/', LutadorCreate.as_view(), name='lutador-create'),
    path('lutadores/<int:pk>/editar/', LutadorUpdate.as_view(), name='lutador-update'),
    path('lutadores/<int:pk>/excluir/', LutadorDelete.as_view(), name='lutador-delete'),
    path('lutadores/<int:pk>/', LutadorDetail.as_view(), name='lutador-detail'),

    path('categorias/', CategoriaPesoList.as_view(), name='categoria-list'),
    path('categorias/nova/', CategoriaPesoCreate.as_view(), name='categoria-create'),
    path('categorias/<int:pk>/editar/', CategoriaPesoUpdate.as_view(), name='categoria-update'),
    path('categorias/<int:pk>/excluir/', CategoriaPesoDelete.as_view(), name='categoria-delete'),
    path('categorias/<int:pk>/', CategoriaPesoDetail.as_view(), name='categoria-detail'),

    path('eventos/', EventoList.as_view(), name='evento-list'),
    path('eventos/novo/', EventoCreate.as_view(), name='evento-create'),
    path('eventos/<int:pk>/', EventoDetail.as_view(), name='evento-detail'),
    path('eventos/editar/<int:pk>/', EventoUpdate.as_view(), name='evento-update'),
    path('eventos/excluir/<int:pk>/', EventoDelete.as_view(), name='evento-delete'),

    path('paises/', PaisList.as_view(), name='pais-list'),
    path('paises/novo/', PaisCreate.as_view(), name='pais-create'),
    path('paises/<int:pk>/editar/', PaisUpdate.as_view(), name='pais-update'),
    path('paises/<int:pk>/excluir/', PaisDelete.as_view(), name='pais-delete'),
    path('paises/<int:pk>/', PaisDetail.as_view(), name='pais-detail'),
]