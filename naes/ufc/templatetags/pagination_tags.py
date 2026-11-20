
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    request = context["request"]
    parametros = request.GET.copy()

    parametros.pop("page", None)
    parametros.update(kwargs)

    return parametros.urlencode()
