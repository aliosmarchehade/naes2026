
from django import forms

from .models import ConfiguracaoIA


class ConfiguracaoIAForm(forms.ModelForm):

    class Meta:
        model = ConfiguracaoIA

        fields = [
            "provedor",
            "modelo",
            "ativa",
            "temperatura",
            "max_tokens_saida",
        ]

        widgets = {
            "provedor": forms.Select(
                attrs={"class": "form-select"}
            ),
            "modelo": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "ativa": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "temperatura": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.1",
                    "min": "0",
                    "max": "2",
                }
            ),
            "max_tokens_saida": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),
        }

    def clean_modelo(self):
        modelo = self.cleaned_data["modelo"].strip()

        if not modelo:
            raise forms.ValidationError(
                "Informe o modelo da inteligência artificial."
            )

        return modelo
