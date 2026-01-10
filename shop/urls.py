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
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # PROFILE (IMPORTANT)
    path('profile/', views.profile_options, name='profile'),
    path('profile/edit/', views.my_profile, name='my_profile'),

    # FILTERS & OFFERS
    path('filters/', views.filters_view, name='filters'),
    path('offers/', views.offers_view, name='offers'),

    # ORDER & PAYMENT
    path('checkout/', views.checkout, name='checkout'),
    path('wishlist/buy-now/<int:product_id>/', views.wishlist_buy_now, name='wishlist_buy_now'),
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
    path("order-success/", views.order_success, name="order_success"),
    path("my-orders/", views.my_orders, name="my_orders"),
    path("my-address/", views.my_address, name="my_address"),

    # ================= PAYMENT =================
    path("razorpay-success/", views.razorpay_success, name="razorpay_success"),
    path("payment-success/<int:order_id>/", views.payment_success, name="payment_success"),
    path("payment-failed/<int:order_id>/", views.payment_failed, name="payment_failed"),
    path("upi-instructions/<int:order_id>/", views.upi_instructions, name="upi_instructions"),
    path("upi-paid/<int:order_id>/", views.upi_payment_done, name="upi_payment_done"),

    


]
