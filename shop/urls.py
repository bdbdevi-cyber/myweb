from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView, LoginView

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('login/', LoginView.as_view(template_name='shop/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('signup/', views.signup, name='signup'),
    # path('cart/', views.cart, name='cart'),
    path('cart/add/<int:id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:id>/', views.cart_remove, name='cart_remove'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/', views.cart_view, name='cart'),
    path('filters/', views.filters_page, name='filters'),
    path('category/<str:category_name>/', views.category_view, name='category'),
    # మిగతా URLs...

     path('checkout/', views.checkout, name='checkout'),
    path('razorpay/success/', views.razorpay_success, name='razorpay_success'),
    path('payment/success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('payment/failed/<int:order_id>/', views.payment_failed, name='payment_failed'),
    # path('payment/upi-instructions/<int:order_id>/', views.upi_instructions, name='upi_instructions'),  # optional if separate view
    


]

    

 




   

    


