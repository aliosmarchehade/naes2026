
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator, MaxValueValidator


class ConfiguracaoIA(models.Model):
    """Armazena as configurações gerais da integração com IA."""

    PROVEDORES = [
        ("openai", "OpenAI"),
    ]

    provedor = models.CharField(
        max_length=30,
        choices=PROVEDORES,
        default="openai",
    )

    modelo = models.CharField(
        max_length=100,
        default="gpt-4.1-mini",
    )

    ativa = models.BooleanField(default=True)

    temperatura = models.FloatField(
        default=0.7,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(2),
        ],
    )

    max_tokens_saida = models.PositiveIntegerField(default=1000)

    atualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="configuracoes_ia_atualizadas",
    )

    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuração da IA"
        verbose_name_plural = "Configurações da IA"

    def __str__(self):
        return f"{self.get_provedor_display()} - {self.modelo}"


class CotaMensalIA(models.Model):
    """Controla o limite mensal de tokens de cada usuário."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cotas_ia",
    )

    ano = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(2000), MaxValueValidator(9999)]
    )

    mes = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )

    limite_tokens = models.PositiveIntegerField(default=100000)

    tokens_utilizados = models.PositiveIntegerField(default=0)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cota mensal de IA"
        verbose_name_plural = "Cotas mensais de IA"

        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "ano", "mes"],
                name="unique_cota_usuario_mes",
            ),
            models.CheckConstraint(
                condition=Q(mes__gte=1) & Q(mes__lte=12),
                name="cota_mes_valido",
            ),
        ]

    @property
    def tokens_restantes(self):
        return max(0, self.limite_tokens - self.tokens_utilizados)

    @property
    def percentual_utilizado(self):
        if self.limite_tokens == 0:
            return 100

        return min(
            100,
            (self.tokens_utilizados / self.limite_tokens) * 100,
        )

    @property
    def atingiu_limite(self):
        return self.tokens_utilizados >= self.limite_tokens

    def __str__(self):
        return f"{self.usuario} - {self.mes:02d}/{self.ano}"


class RegistroChamadaIA(models.Model):
    """Registra as chamadas realizadas à inteligência artificial."""

    STATUS_CHOICES = [
        ("sucesso", "Sucesso"),
        ("erro", "Erro"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chamadas_ia",
    )

    provedor = models.CharField(max_length=30, default="openai")
    modelo = models.CharField(max_length=100)

    tokens_entrada = models.PositiveIntegerField(default=0)
    tokens_saida = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="sucesso",
    )

    mensagem_erro = models.TextField(blank=True)

    identificador_resposta = models.CharField(
        max_length=150,
        blank=True,
    )

    duracao_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Registro de chamada de IA"
        verbose_name_plural = "Registros de chamadas de IA"
        ordering = ["-criado_em"]

        indexes = [
            models.Index(
                fields=["usuario", "criado_em"],
                name="ia_usuario_data_idx",
            ),
            models.Index(
                fields=["status", "criado_em"],
                name="ia_status_data_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.usuario or 'Usuário removido'} - "
            f"{self.modelo} - {self.get_status_display()}"
        )


# ==========================================================
# HISTÓRICO DE CONVERSAS DA IA
# ==========================================================

class ConversaIA(models.Model):
    """Armazena as conversas realizadas pelos usuários com a IA."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversas_ia",
    )

    titulo = models.CharField(
        max_length=200,
        default="Nova conversa",
    )

    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Conversa com IA"
        verbose_name_plural = "Conversas com IA"
        ordering = ["-atualizada_em"]

        indexes = [
            models.Index(
                fields=["usuario", "atualizada_em"],
                name="ia_conversa_usuario_idx",
            ),
        ]

    def __str__(self):
        return f"{self.titulo} - {self.usuario}"


class MensagemIA(models.Model):
    """Armazena cada mensagem enviada ou recebida em uma conversa."""

    TIPOS_MENSAGEM = [
        ("usuario", "Usuário"),
        ("ia", "Inteligência Artificial"),
    ]

    conversa = models.ForeignKey(
        ConversaIA,
        on_delete=models.CASCADE,
        related_name="mensagens",
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPOS_MENSAGEM,
    )

    conteudo = models.TextField()

    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mensagem da IA"
        verbose_name_plural = "Mensagens da IA"
        ordering = ["criada_em"]

        indexes = [
            models.Index(
                fields=["conversa", "criada_em"],
                name="ia_mensagem_conversa_idx",
            ),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.criada_em:%d/%m/%Y %H:%M}"
