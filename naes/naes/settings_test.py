"""
Configurações usadas APENAS para rodar os testes automatizados.

Herda tudo de settings.py e troca só o que é necessário para os testes:
- banco SQLite em memória (não toca no banco PostgreSQL de verdade);
- pasta de mídia temporária (as fotos enviadas nos testes não vão para media/);
- hash de senha rápido (deixa os testes mais rápidos).

Uso:
    python manage.py test ufc --settings=naes.settings_test
"""
import tempfile

from .settings import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

MEDIA_ROOT = tempfile.mkdtemp(prefix="naes_testes_media_")

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# O debug_toolbar bloqueia a execução de testes por padrão.
DEBUG_TOOLBAR_CONFIG = {"IS_RUNNING_TESTS": False}
