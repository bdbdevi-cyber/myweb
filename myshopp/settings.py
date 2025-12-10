import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# -------------------------------
# BASE DIR
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent


# -------------------------------
# SECURITY
# -------------------------------
SECRET_KEY = 'replace-this-with-a-secure-key'
DEBUG = False

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "myweb-6-01tx.onrender.com",
    ".onrender.com",
]


# -------------------------------
# CLOUDINARY CONFIG
# -------------------------------
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'


# -------------------------------
# APPS
# -------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your app
    'shop',

    # Cloudinary
    'cloudinary',
    'cloudinary_storage',
]


# -------------------------------
# MIDDLEWARE
# -------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # Whitenoise BEFORE SessionMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'myshopp.urls'


# -------------------------------
# TEMPLATES
# -------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myshopp.wsgi.application'



# -------------------------------
# DATABASE
# -------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


AUTH_PASSWORD_VALIDATORS = []


# -------------------------------
# LANGUAGE & TIMEZONE
# -------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# -------------------------------
# STATIC FILES (Render)
# -------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# -------------------------------
# MEDIA (Cloudinary)
# -------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# -------------------------------
# LOGIN URL
# -------------------------------
LOGIN_URL = '/login/'


# -------------------------------
# RAZORPAY
# -------------------------------
RAZORPAY_KEY_ID = "rzp_test_xxx"
RAZORPAY_KEY_SECRET = "rzp_test_secret"

UPI_ID = "yourupi@bank"
UPI_NAME = "My Shop"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

