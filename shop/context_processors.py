from .models import Wishlist

def user_counts(request):
    """
    Context processor to provide cart and wishlist counts
    for top nav.
    """
    cart_count = 0
    wishlist_count = 0

    if request.user.is_authenticated:
        # Session cart count
        cart = request.session.get('cart', {})
        cart_count = sum(cart.values())  # sum of all quantities

        # Wishlist count from DB
        wishlist_count = Wishlist.objects.filter(user=request.user).count()

    return {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
    }
