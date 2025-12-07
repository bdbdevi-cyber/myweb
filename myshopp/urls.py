from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from shop import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),  # Main app URLs only
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    


    path(
        'login/',
        auth_views.LoginView.as_view(template_name='login.html'),
        name='login'
    ),





    path('profile-options/', views.profile_options, name='profile_options'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('welcome/', views.welcome, name='welcome'),

    path('', views.home, name='home'),



    




    path('profile/', views.profile_options, name="profile"),
   
]



    # path('cart/', include('cart.urls')),  # <----- COMMENT *THIS* IF NO cart app


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


