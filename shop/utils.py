def get_cart_count(request):
    cart = request.session.get('cart', {})
    return sum(cart.values())


def get_wishlist_count(request):
    wishlist = request.session.get('wishlist', [])
    return len(wishlist)
