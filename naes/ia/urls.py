
from django.urls import path
from . import views

app_name = "ia"

urlpatterns = [
    path("", views.assistente, name="assistente"),
    path("configuracao/", views.configuracao, name="configuracao"),
    path("testar-conexao/", views.testar_conexao, name="testar_conexao"),
    path("auditoria/", views.auditoria, name="auditoria"),
    path("usuarios/", views.usuarios, name="usuarios"),
    path(
        "usuarios/<int:usuario_id>/atualizar-cota/",
        views.atualizar_cota,
        name="atualizar_cota",
    ),
]
