"""
Django settings for GmailAccount project.
"""

from pathlib import Path
import os
import json

# dotenv is only needed locally; on Vercel env vars are injected directly
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ============================================================
# BASE DIRECTORY
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================
# SECURITY SETTINGS
# ============================================================
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-lxzi8k8=8t81_hr_j_5gs9d-5a2-nyv4_3$s3!c0+6=w0g+=vb'
)

# On Vercel, set DEBUG=False in environment variables
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# ============================================================
# OAUTH SETTINGS — must come AFTER DEBUG is defined
# ============================================================
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
if DEBUG:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# ============================================================
# GOOGLE CREDENTIALS — write credentials.json from env var
# Vercel filesystem is read-only except /tmp
# ============================================================
GOOGLE_CREDENTIALS_PATH = '/tmp/credentials.json'

google_creds = os.environ.get('GOOGLE_CREDENTIALS')
if google_creds:
    with open(GOOGLE_CREDENTIALS_PATH, 'w') as f:
        json.dump(json.loads(google_creds), f)
elif (BASE_DIR / 'credentials.json').exists():
    # Local development: use the file directly
    GOOGLE_CREDENTIALS_PATH = str(BASE_DIR / 'credentials.json')

# ============================================================
# INSTALLED APPS
# ============================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drive',
]

# ============================================================
# MIDDLEWARE
# ============================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ============================================================
# URL & WSGI
# ============================================================
ROOT_URLCONF = 'GmailAccount.urls'
WSGI_APPLICATION = 'GmailAccount.wsgi.application'

# ============================================================
# TEMPLATES
# ============================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ============================================================
# DATABASE
# SQLite doesn't persist on Vercel between requests.
# Fine for sessions/OAuth state since those are short-lived,
# but don't use it for persistent user data in production.
# ============================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/tmp/db.sqlite3',  # /tmp is writable on Vercel
    }
}

# ============================================================
# PASSWORD VALIDATION
# ============================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================================
# INTERNATIONALIZATION
# ============================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ============================================================
# STATIC FILES
# ============================================================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================
# GOOGLE DRIVE / OAUTH SETTINGS
# ============================================================
GOOGLE_CLIENT_SECRETS_FILE = GOOGLE_CREDENTIALS_PATH

GOOGLE_DRIVE_SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
]

GOOGLE_REDIRECT_URI = os.environ.get(
    "GOOGLE_REDIRECT_URI",
    "http://localhost:8000/oauth2callback/"
)

# ============================================================
# SESSION SETTINGS
# ============================================================
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
SESSION_SAVE_EVERY_REQUEST = True