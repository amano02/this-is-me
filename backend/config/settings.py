"""
Django settings for config project.
"""

import os
from pathlib import Path

from decouple import Csv, config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Vercel / 本番環境判定
IS_VERCEL = os.environ.get("VERCEL") == "1"
IS_PRODUCTION = IS_VERCEL or config("DJANGO_PRODUCTION", default=False, cast=bool)


SECRET_KEY = config(
    "DJANGO_SECRET_KEY",
    default="django-insecure-zy6u$2dqp#hv9zcymjlkbevon+zu)1q)r0s!lb!xv06&)8t%s@",
)

DEBUG = config("DJANGO_DEBUG", default=not IS_PRODUCTION, cast=bool)

if IS_VERCEL:
    # Vercel のデプロイ URL は都度変わるためワイルドカードを許可
    ALLOWED_HOSTS = ["*"]
else:
    DEFAULT_ALLOWED_HOSTS = (
        "localhost,127.0.0.1,.vercel.app,this-is-me-one.vercel.app,amano02.github.io"
    )
    ALLOWED_HOSTS = config(
        "DJANGO_ALLOWED_HOSTS", default=DEFAULT_ALLOWED_HOSTS, cast=Csv()
    )


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd party
    "adminsortable2",
    # local apps
    "apps.core",
    "apps.works",
    "apps.contact",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site_profile",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# DATABASE_URL があれば Vercel/Neon 等の本番 DB に接続。なければ .env の PostgreSQL。

database_url = os.environ.get("DATABASE_URL") or config("DATABASE_URL", default="")

if database_url:
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.config(
            default=database_url,
            conn_max_age=600,
            ssl_require=not database_url.startswith("postgres://localhost"),
        )
    }
elif IS_VERCEL:
    # DATABASE_URL 未設定時の Vercel フォールバック（閲覧専用）
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("DB_NAME", default="portfolio_db"),
            "USER": config("DB_USER", default="portfolio_user"),
            "PASSWORD": config("DB_PASSWORD", default="postgres"),
            "HOST": config("DB_HOST", default="localhost"),
            "PORT": config("DB_PORT", default="5432"),
            "CONN_MAX_AGE": config("DB_CONN_MAX_AGE", default=60, cast=int),
        }
    }


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization

LANGUAGE_CODE = "ja"
TIME_ZONE = "Asia/Tokyo"
USE_I18N = True
USE_TZ = True


# Static files

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DATA_UPLOAD_MAX_MEMORY_SIZE = config(
    "DATA_UPLOAD_MAX_MEMORY_SIZE", default=100 * 1024 * 1024, cast=int
)
FILE_UPLOAD_MAX_MEMORY_SIZE = config(
    "FILE_UPLOAD_MAX_MEMORY_SIZE", default=100 * 1024 * 1024, cast=int
)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Security (production)

if IS_PRODUCTION:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

_default_csrf_origins = (
    "http://localhost:8000,"
    "https://this-is-me-one.vercel.app,"
    "https://this-is-me.vercel.app,"
    "https://amano02.github.io"
)
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default=_default_csrf_origins, cast=Csv())

# Vercel のプレビュー URL (*.vercel.app) を動的に許可
_vercel_url = os.environ.get("VERCEL_URL")
if _vercel_url:
    CSRF_TRUSTED_ORIGINS.append(f"https://{_vercel_url}")

# GitHub Pages からの API 呼び出し用（同一オリジンリダイレクト後は不要だが保険）
if "https://amano02.github.io" not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append("https://amano02.github.io")
