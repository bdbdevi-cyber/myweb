from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from decimal import Decimal
import razorpay

from django.contrib.auth.models import User

from .models import Product, Order, Profile, Wishlist
from .forms import SignUpForm, UserProfileForm, ProfileForm


from .models import Product, Order, OrderItem
from .utils import get_cart_count, get_wishlist_count


from shop.models import Product, CartItem
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import Profile
from .forms import SignUpForm


from decimal import Decimal
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Product, Order, OrderItem
from .utils import get_cart_count, get_wishlist_count

@login_required
def wishlist_buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Add item to cart, qty=1 by default
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'qty': 1}
    )
    if not created:
        # If already in cart, increase qty by 1
        cart_item.qty += 1
        cart_item.save()
    
    # Redirect to checkout page
    return redirect('checkout')



# ================= HELPER =================
def get_cart_count(request):
    
    return sum(request.session.get('cart', {}).values())


def get_wishlist_items(request):
    if request.user.is_authenticated:
        return Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
    return []


def get_wishlist_count(request):
    if request.user.is_authenticated:
        return Wishlist.objects.filter(user=request.user).count()
    return 0


# ---------------- HOME ----------------
def home(request):
    products = Product.objects.filter(show_on_homepage=True)

    return render(request, 'shop/home.html', {
        'products': products,
        'cart_count': get_cart_count(request),
        'wishlist_items': get_wishlist_items(request),
        'wishlist_count': get_wishlist_count(request),
    })


# ---------------- CATEGORY ----------------
def category_view(request, category_name):
    CATEGORY_MAP = {
        "dresses": "Dress",
        "dress": "Dress",
        "sarees": "Sarees",
        "offers": "Offers",
    }

    db_category = CATEGORY_MAP.get(category_name.lower())

    products = Product.objects.filter(category__iexact=db_category) if db_category else Product.objects.none()

    return render(request, 'shop/category.html', {
        'products': products,
        'category_name': category_name,
        'cart_count': get_cart_count(request),
        'wishlist_items': get_wishlist_items(request),
        'wishlist_count': get_wishlist_count(request),
    })




# ---------------- PRODUCT DETAIL ----------------
def product_detail(request, id):
    product = get_object_or_404(Product, id=id, available=True)

    return render(request, 'shop/product_detail.html', {
        'product': product,
        'cart_count': get_cart_count(request),
        'wishlist_items': get_wishlist_items(request),
        'wishlist_count': get_wishlist_count(request),
    })




# ---------------- CART ----------------
@login_required
def cart_view(request):
    cart = request.session.get('cart', {})
    items = []
    total = Decimal("0.00")

    for pid, qty in cart.items():
        product = get_object_or_404(Product, id=int(pid))
        subtotal = product.price * qty
        items.append({"product": product, "qty": qty, "subtotal": subtotal})
        total += subtotal

    return render(request, "shop/cart.html", {
        "items": items,
        "total": total,
        "wishlist_count": get_wishlist_count(request),
    })


@login_required
def cart_add(request, id):
    cart = request.session.get('cart', {})
    cart[str(id)] = cart.get(str(id), 0) + 1
    request.session['cart'] = cart
    return redirect("cart")


@login_required
def cart_remove(request, id):
    cart = request.session.get('cart', {})
    cart.pop(str(id), None)
    request.session['cart'] = cart
    return redirect("cart")


# ---------------- WISHLIST ----------------
@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user)

    return render(request, 'shop/wishlist.html', {
        'items': items,
        'cart_count': get_cart_count(request),
        'wishlist_count': get_wishlist_count(request),
    })


@login_required
def wishlist_add(request, id):
    product = get_object_or_404(Product, id=id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def wishlist_remove(request, id):
    Wishlist.objects.filter(user=request.user, product_id=id).delete()
    return redirect(request.META.get('HTTP_REFERER', 'home'))


# ---------------- AUTH ----------------
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import Profile
from .forms import SignUpForm


def signup(request):
    form = SignUpForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()

        # ✅ SAFE PROFILE CREATION
        Profile.objects.get_or_create(
            user=user,
            defaults={
                "phone": form.cleaned_data.get("phone")
            }
        )

        messages.success(request, "Account created successfully. Please login.")
        return redirect("login")

    return render(request, "shop/signup.html", {"form": form})





def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("home")
    return render(request, "shop/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")


# ---------------- PROFILE ----------------
@login_required
def profile_view(request):
    profile = request.user.profile

    if request.method == "POST":
        u_form = UserProfileForm(request.POST, instance=request.user)
        p_form = ProfileForm(request.POST, instance=profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Profile updated successfully")
            return redirect("profile")
    else:
        u_form = UserProfileForm(instance=request.user)
        p_form = ProfileForm(instance=profile)

    return render(request, "shop/profile.html", {
        "u_form": u_form,
        "p_form": p_form,
        "wishlist_count": get_wishlist_count(request),
    })


@login_required
def profile_options(request):
    return render(request, "shop/profile_options.html", {
        "wishlist_count": get_wishlist_count(request),
    })


# ---------------- FILTERS ----------------
def filters_view(request):
    order = request.GET.get('order')
    products = Product.objects.all()

    if order == 'price_asc':
        products = products.order_by('price')
    elif order == 'price_desc':
        products = products.order_by('-price')

    return render(request, 'shop/filters.html', {
        'products': products,
        'cart_count': get_cart_count(request),
        'wishlist_count': get_wishlist_count(request),
    })


# ---------------- OFFERS ----------------
def offers_view(request):
    products = Product.objects.filter(is_offer=True)

    return render(request, 'shop/offers.html', {
        'products': products,
        'cart_count': get_cart_count(request),
        'wishlist_items': get_wishlist_items(request),
        'wishlist_count': get_wishlist_count(request),
    })







@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.info(request, "Your cart is empty.")
        return redirect("home")

    items = []
    total = Decimal("0.00")

    for pid, qty in cart.items():
        product = get_object_or_404(Product, id=int(pid))
        subtotal = product.price * qty
        items.append({
            "product": product,
            "qty": qty,
            "subtotal": subtotal
        })
        total += subtotal

    profile = request.user.profile

    # ✅ IMPORTANT PART — PLACE ORDER
    if request.method == "POST":
        address = request.POST.get("address", "")
        payment_method = request.POST.get("payment_method", "COD")

        # 1️⃣ CREATE ORDER
        order = Order.objects.create(
            user=request.user,
            address=address,
            payment_method=payment_method,
            payment_status="PENDING"
        )

        # 2️⃣ CREATE ORDER ITEMS
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                quantity=item["qty"],
                price=item["product"].price
            )

        # 3️⃣ CLEAR CART
        request.session['cart'] = {}

        messages.success(request, "Order placed successfully!")
        return redirect("order_success")

    return render(request, "shop/checkout.html", {
        "items": items,
        "total": total,
        "profile": profile,
        "cart_count": get_cart_count(request),
        "wishlist_count": get_wishlist_count(request),
    })



@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Clear cart and add only this product
    request.session['cart'] = {
        str(product_id): 1
    }

    return redirect('checkout')   # ✅ IMPORTANT




@login_required
def order_success(request):
    # clear cart after order
    request.session['cart'] = {}

    return render(request, "shop/order_success.html")
