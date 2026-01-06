from django.urls import path
from . import views

urlpatterns = [
    # HOME
    path('', views.home, name='home'),

    # CATEGORY
    path('category/<str:category_name>/', views.category_view, name='category'),

    # PRODUCT
    path('product/<int:id>/', views.product_detail, name='product_detail'),

    # CART
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:id>/', views.cart_remove, name='cart_remove'),

    # WISHLIST
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:id>/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/remove/<int:id>/', views.wishlist_remove, name='wishlist_remove'),

    # AUTH
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # PROFILE
    path('profile/', views.profile_view, name='profile'),
    path('profile/options/', views.profile_options, name='profile_options'),

    # FILTERS & OFFERS
    path('filters/', views.filters_view, name='filters'),
    path('offers/', views.offers_view, name='offers'),
    
    path('checkout/', views.checkout, name='checkout'),
     path('wishlist/buy-now/<int:product_id>/', views.wishlist_buy_now, name='wishlist_buy_now'),



]

