import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshopp.settings')
application = get_wsgi_application()
import os
from django.core.wsgi import get_wsgi_application

# Set the default settings module for the 'django' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshopp.settings')

# Get the WSGI application for serving your project.
application = get_wsgi_application()
