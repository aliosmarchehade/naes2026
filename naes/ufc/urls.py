from django.urls import path
from .views import *

urlpatterns = [
    path('lutadores/', LutadorList.as_view(), name='lutador-list'),
    path('lutadores/novo/', LutadorCreate.as_view(), name='lutador-create'),
    path('lutadores/<int:pk>/editar/', LutadorUpdate.as_view(), name='lutador-update'),
    path('lutadores/<int:pk>/excluir/', LutadorDelete.as_view(), name='lutador-delete'),
    path('lutadores/<int:pk>/', LutadorDetail.as_view(), name='lutador-detail'),
]