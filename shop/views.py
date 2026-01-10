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
from .forms import SignupForm

from django.contrib.auth.decorators import login_required
from .models import Product
from .utils import get_cart_count, get_wishlist_count  # make sure you have these

from .models import Product, CartItem

from django.contrib.auth.models import User
from .forms import SignupForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .forms import SignupForm
from .models import Profile

from .forms import UserForm, ProfileForm
from .models import Order, OrderItem





@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "shop/my_orders.html", {
        "orders": orders
    })

@login_required
def my_address(request):
    profile = request.user.profile
    return render(request, "shop/my_address.html", {
        "profile": profile
    })



@login_required
def my_profile(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            # ✅ SAVE ayyaka Profile Options ki vellali
            return redirect('profile')

    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'shop/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def profile_options(request):
    return render(request, "shop/profile_options.html", {
        "wishlist_count": get_wishlist_count(request),
    })


def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())

        # ✅ Login ayyaka direct ga Profile Options ki
        return redirect("profile")

    return render(request, "shop/login.html", {"form": form})













def logout_view(request):
    logout(request)
    return redirect("home")



def signup_view(request):
    form = SignupForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        email = form.cleaned_data["email"]
        phone = form.cleaned_data["phone"]
        address = form.cleaned_data["address"]
        password = form.cleaned_data["password"]

        # Create User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Update Profile created by signal
        profile = user.profile  # signal already created profile
        profile.phone = phone
        profile.address = address
        profile.save()

        messages.success(request, "Account created successfully. Please login.")
        return redirect("login")

    return render(request, "shop/signup.html", {"form": form})





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
    
    # Optional: update session cart if your checkout reads session
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart_item.qty
    request.session['cart'] = cart
    request.session.modified = True
    
    # Redirect to checkout page
    return redirect('checkout')  # ✅ No comma here



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

    # Fetch products
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
    images = product.images.all()  # all related images

    return render(request, 'shop/product_detail.html', {
        'product': product,
        'images': images,
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
# @login_required
# def profile_view(request):
#     profile = request.user.profile

#     if request.method == "POST":
#         u_form = UserProfileForm(request.POST, instance=request.user)
#         p_form = ProfileForm(request.POST, instance=profile)
#         if u_form.is_valid() and p_form.is_valid():
#             u_form.save()
#             p_form.save()
#             messages.success(request, "Profile updated successfully")
#             return redirect("profile")
#     else:
#         u_form = UserProfileForm(instance=request.user)
#         p_form = ProfileForm(instance=profile)

#     return render(request, "shop/profile.html", {
#         "u_form": u_form,
#         "p_form": p_form,
#         "wishlist_count": get_wishlist_count(request),
#     })




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
        'wishlist_items': get_wishlist_items(request),  # ✅ ONLY THIS LINE ADDED
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



# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# ================= CHECKOUT VIEW =================
# ================= CHECKOUT VIEW =================
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

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

    if request.method == "POST":
        address = request.POST.get("address", profile.address)
        payment_method = request.POST.get("payment_method", "COD")

        # ✅ 1. CREATE ORDER
        order = Order.objects.create(
            user=request.user,
            address=address,
            payment_method=payment_method,
            payment_status="PENDING"
        )

        # ✅ 2. CREATE ORDER ITEMS
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                quantity=item["qty"],
                price=item["product"].price
            )

        # ✅ 3. CLEAR CART
        request.session["cart"] = {}

        # ✅ 4. PAYMENT REDIRECTION (MAIN FIX)
        if payment_method == "UPI":
            # 🔥 UPI instructions page
            return redirect("upi_instructions", order_id=order.id)

        elif payment_method == "RAZORPAY":
            # 🔥 Razorpay flow
            return redirect("razorpay_payment", order_id=order.id)

        else:
            # 🔥 COD
            messages.success(request, "Order placed successfully! Payment on delivery.")
            return redirect("order_success")

    return render(request, "shop/checkout.html", {
        "items": items,
        "total": total,
        "profile": profile,
        "cart_count": get_cart_count(request),
        "wishlist_count": get_wishlist_count(request),
    })


# ================= BUY NOW VIEW =================
@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Clear cart and add only this product
    request.session['cart'] = {str(product_id): 1}
    request.session.modified = True  # ✅ Make sure session updates

    return redirect('checkout')  # This works because checkout reads from session





# ---------------- RAZORPAY SUCCESS ----------------
@csrf_exempt
@login_required
def razorpay_success(request):
    if request.method == "POST":
        payment_id = request.POST.get("razorpay_payment_id")
        razorpay_order_id = request.POST.get("razorpay_order_id")
        signature = request.POST.get("razorpay_signature")

        # Fetch the order
        order = get_object_or_404(Order, razorpay_order_id=razorpay_order_id, user=request.user)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        try:
            # Verify payment signature
            client.utility.verify_payment_signature({
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            })

            # ✅ Payment Successful
            order.payment_status = "PAID"
            order.razorpay_payment_id = payment_id
            order.save()

            # Clear cart after successful payment
            request.session['cart'] = {}

            return redirect("payment_success", order_id=order.id)

        except razorpay.errors.SignatureVerificationError:
            # ✅ Payment Failed
            order.payment_status = "FAILED"
            order.save()
            return redirect("payment_failed", order_id=order.id)

    return redirect("home")


# ---------------- PAYMENT SUCCESS PAGE ----------------
@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "shop/payment_success.html", {"order": order})


# ---------------- PAYMENT FAILED PAGE ----------------
@login_required
def payment_failed(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "shop/payment_failed.html", {"order": order})


def product_card_view(request):
    category = request.GET.get('category')  # fetch ?category=Sarees
    if category:
        products = Product.objects.filter(category__name=category)
    else:
        products = Product.objects.all()
    return render(request, 'shop/product_card.html', {'products': products})



def order_success(request):
    return render(request, 'shop/order_success.html')


@login_required
def upi_instructions(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    upi_id = "9032916659-2@ybl"   # 🔥 YOUR REAL UPI ID
    name = "My Shop"
    amount = order.get_total_amount()

    upi_deep_link = (
        f"upi://pay?pa={upi_id}"
        f"&pn={name}"
        f"&tn=Order {order.id}"
        f"&am={amount}"
        f"&cu=INR"
    )

    return render(request, "shop/upi_instructions.html", {
        "order": order,
        "amount": amount,
        "upi_id": upi_id,
        "upi_deep_link": upi_deep_link,
    })


@login_required
def upi_payment_done(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.payment_status = "PAID"
    order.save()
    return redirect("order_success")



