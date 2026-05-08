from django.db import models
from django.contrib.auth.models import User



# CATEGORIA DE PESO
class CategoriaPeso(models.Model):
    nome = models.CharField(max_length=50)  #Ex: Peso Leve / Peso Médio / Peso Meio-Pesado  
    peso_maximo = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.nome} ({self.peso_maximo}kg)"


# LUTADOR
class Lutador(models.Model):
    nome = models.CharField(max_length=80)
    apelido = models.CharField(max_length=50, blank=True) #pode ser vazio, pois nem todos os lutadores tem um apelido
    idade = models.PositiveIntegerField() #só numeros positivos
    peso = models.DecimalField(max_digits=5, decimal_places=2)
    categoria = models.ForeignKey(CategoriaPeso, on_delete=models.PROTECT)

    vitorias = models.PositiveIntegerField(default=0)
    derrotas = models.PositiveIntegerField(default=0)

    cadastrado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    cadastrado_por = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True) ## Aqui tirei a obrigatoriedade de estar logado,so para testar e apresentar

    def __str__(self):
        return f"{self.nome} ({self.apelido})"


# EVENTO (tipo UFC 300, fightnights, etc)
class Evento(models.Model):
    nome = models.CharField(max_length=100)
    local = models.CharField(max_length=100)
    data = models.DateField()
    descricao = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nome} - {self.data}"


# LUTA
class Luta(models.Model):
    lutador_1 = models.ForeignKey(Lutador, on_delete=models.PROTECT, related_name="lutador_1")
    lutador_2 = models.ForeignKey(Lutador, on_delete=models.PROTECT, related_name="lutador_2")

    evento = models.ForeignKey(Evento, on_delete=models.PROTECT)
    categoria = models.ForeignKey(CategoriaPeso, on_delete=models.PROTECT)

    data_hora = models.DateTimeField(null=True, blank=True)

    resultado = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Ex: KO, TK, SUBMISSION, SPLIT DECISION, UNANIMOUS DECISION, NC, DQ"
    )

    vencedor = models.ForeignKey(
        Lutador,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="vencedor"
    )

    cadastrado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    cadastrado_por = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.lutador_1} vs {self.lutador_2} - {self.evento}"