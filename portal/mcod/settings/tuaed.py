"""TuAED: ustawienia lokalnego portalu do demo (na bazie local.py.sample). Admin i API tylko na 127.0.0.1, bez nginx,
więc ciasteczka bez domeny mcod.local, HTTP zamiast HTTPS."""

from mcod.settings.base import *  # noqa: F401,F403
from mcod.settings.base import LOGGING, ROOT_DIR, TEMPLATES, env

DEBUG = True
ALLOWED_HOSTS = ["*"]
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG
INTERNAL_IPS = ("127.0.0.1", "localhost")

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_SSL = False
NO_REPLY_EMAIL = "no-reply@mcod.local"

# Bez "timeout" z local.py.sample: ES 6.8 odrzuca index.timeout (illegal_argument_exception).
ELASTICSEARCH_DSL_INDEX_SETTINGS = {"number_of_shards": 1, "number_of_replicas": 0}
ELASTICSEARCH_HISTORIES_IDX_SETTINGS = {"number_of_shards": 1, "number_of_replicas": 0}

CELERY_TASK_ALWAYS_EAGER = False

FIXTURE_DIRS = [str(ROOT_DIR("test-data/fixtures"))]
MEDIA_ROOT = str(ROOT_DIR("media"))
ACADEMY_MEDIA_ROOT = str(ROOT_DIR.path(MEDIA_ROOT, "academy"))
IMAGES_MEDIA_ROOT = str(ROOT_DIR.path(MEDIA_ROOT, "images"))
LABORATORY_MEDIA_ROOT = str(ROOT_DIR.path(MEDIA_ROOT, "lab_reports"))
MEETINGS_MEDIA_ROOT = str(ROOT_DIR.path(MEDIA_ROOT, "meetings"))
NEWSLETTER_MEDIA_ROOT = str(ROOT_DIR.path(MEDIA_ROOT, "newsletter"))
RESOURCES_FILES_TO_REMOVE_ROOT = str(ROOT_DIR.path(MEDIA_ROOT, "to_be_removed", "resources"))
RESOURCES_MEDIA_ROOT = str(ROOT_DIR.path(MEDIA_ROOT, "resources"))
SHOWCASES_MEDIA_ROOT = str(ROOT_DIR.path(MEDIA_ROOT, "showcases"))

# Bez nginx i bez domeny mcod.local: ciasteczka hosta (localhost / 127.0.0.1), bez Secure.
SESSION_COOKIE_NAME = "tuaed_sessionid"
SESSION_COOKIE_DOMAIN = None
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_DOMAIN = None
CSRF_COOKIE_SECURE = False
API_TOKEN_COOKIE_NAME = "tuaed_apiauthtoken"

for _logger in ("django.request", "django.server", "mcod", "resource_file_processing", "celery.app.trace"):
    if _logger in LOGGING["loggers"]:
        LOGGING["loggers"][_logger]["handlers"] = ["console"]

COMPONENT = env("COMPONENT", default="admin")
ENVIRONMENT = "local"
AXES_ENABLED = False
