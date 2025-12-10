from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from shop import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # SHOP app URLs (home, products, etc.)
    path('', include('shop.urls')),

    # AUTH
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='login.html'),
        name='login'
    ),

    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='/'),
        name='logout'
    ),

    # Signup
    path('signup/', views.signup, name='signup'),

    # Profile
    path('profile-options/', views.profile_options, name='profile_options'),
    path('profile/', views.profile_options, name='profile'),

    # Welcome page
    path('welcome/', views.welcome, name='welcome'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
