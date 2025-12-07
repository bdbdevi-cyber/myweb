from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from decimal import Decimal
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

import razorpay

from .models import Product, Order, OrderItem, Profile
from .forms import UserProfileForm, ProfileForm, SignupForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .forms import SignupForm, UserProfileForm, ProfileForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm



from .models import Product, Order, OrderItem, Profile
from .forms import UserProfileForm, ProfileForm, SignupForm

@login_required
def upi_instructions(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    total = sum(item.price * item.quantity for item in order.items.all())

    upi_id = getattr(settings, "UPI_ID", "yourupi@bank")
    upi_name = getattr(settings, "UPI_NAME", request.user.username)
    upi_note = f"Order {order.id} MyShop"
    amount_str = "{:.2f}".format(total)

    upi_deep_link = f"upi://pay?pa={upi_id}&pn={upi_name}&am={amount_str}&cu=INR&tn={upi_note}"

    return render(request, 'shop/upi_instructions.html', {
        'order': order,
        'upi_id': upi_id,
        'upi_deep_link': upi_deep_link,
        'amount': amount_str
    })





# --------------------------
# Razorpay Client Init
# --------------------------
razorpay_client = razorpay.Client(auth=(
    getattr(settings, "RAZORPAY_KEY_ID", ""), 
    getattr(settings, "RAZORPAY_KEY_SECRET", "")
))














@login_required
def cart_add(request):
    cart = request.session.get("cart", {})
    items = []
    total = Decimal('0.00')

    for pid, qty in cart.items():
        p = Product.objects.get(pk=int(pid))
        items.append({'product': p, 'qty': qty, 'subtotal': p.price * qty})
        total += p.price * qty

    return render(request, 'shop/cart.html', {
        'items': items,
        'total': total
    })


@login_required
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    messages.success(request, "Item added to cart.")
    return redirect("cart")


def filters(request):
    order = request.GET.get('order')
    show = request.GET.get('show')

    products = Product.objects.filter(available=True)

    if show == "available":
        products = products.filter(available=True)

    if order == "price_asc":
        products = products.order_by("price")
    elif order == "price_desc":
        products = products.order_by("-price")

    return render(request, "shop/filters.html", {"products": products})


# ======================================================
# CHECKOUT + PAYMENTS (COD + UPI + RAZORPAY)
# ======================================================
@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("home")

    profile = Profile.objects.get(user=request.user)

    items = []
    total = Decimal('0.00')
    for pid, qty in cart.items():
        p = Product.objects.get(pk=int(pid))
        items.append({'product': p, 'qty': qty, 'subtotal': p.price * qty})
        total += p.price * qty

    if request.method == 'POST':
        address = request.POST.get('address', profile.address)
        payment_choice = request.POST.get('payment', 'cod')

        order = Order.objects.create(
            user=request.user,
            address=address,
            payment_method="COD" if payment_choice == "cod" else ("UPI" if payment_choice == "upi" else "RAZORPAY"),
            payment_status="PENDING"
        )

        for entry in items:
            OrderItem.objects.create(
                order=order,
                product=entry['product'],
                quantity=entry['qty'],
                price=entry['product'].price
            )

        # --------------------
        # COD
        # --------------------
        if payment_choice == 'cod':
            request.session['cart'] = {}
            messages.success(request, f"Order placed using COD. Order ID: {order.id}")
            return redirect('payment_success', order_id=order.id)

        # --------------------
        # UPI
        # --------------------
        elif payment_choice == 'upi':
            upi_id = getattr(settings, "UPI_ID", "yourupi@bank")
            upi_name = getattr(settings, "UPI_NAME", request.user.username)
            upi_note = f"Order {order.id} MyShop"
            amount_str = "{:.2f}".format(total)

            upi_deep_link = (
                f"upi://pay?pa={upi_id}&pn={upi_name}&am={amount_str}&cu=INR&tn={upi_note}"
            )

            request.session['cart'] = {}
            return render(request, 'shop/upi_instructions.html', {
                'order': order,
                'upi_id': upi_id,
                'upi_deep_link': upi_deep_link,
                'amount': amount_str
            })

        # --------------------
        # Razorpay
        # --------------------
        else:
            amount_paise = int(total * 100)

            razorpay_order = razorpay_client.order.create({
                "amount": amount_paise,
                "currency": "INR",
                "receipt": str(order.id),
                "payment_capture": 1,
            })

            order.razorpay_order_id = razorpay_order.get('id')
            order.save()

            return render(request, 'shop/razorpay_checkout.html', {
                'order': order,
                'order_items': items,
                'total': total,
                'razorpay_key_id': getattr(settings, "RAZORPAY_KEY_ID", ""),
                'razorpay_order_id': razorpay_order.get('id'),
                'amount_paise': amount_paise,
                'user_email': request.user.email,
                'user_name': request.user.username,
            })

    return render(request, 'shop/checkout.html', {
        'items': items,
        'total': total,
        'profile': profile
    })


# ======================================================
# RAZORPAY CALLBACK VERIFICATION
# ======================================================
@csrf_exempt
@login_required
def razorpay_success(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        try:
            order = Order.objects.get(razorpay_order_id=razorpay_order_id, user=request.user)
        except Order.DoesNotExist:
            messages.error(request, "Order not found.")
            return redirect("home")

        params = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        try:
            razorpay_client.utility.verify_payment_signature(params)
        except:
            order.payment_status = "FAILED"
            order.save()
            return redirect('payment_failed', order_id=order.id)

        order.payment_status = "PAID"
        order.razorpay_payment_id = payment_id
        order.save()

        request.session['cart'] = {}
        return redirect('payment_success', order_id=order.id)

    return redirect("home")


@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/payment_success.html', {'order': order})


@login_required
def payment_failed(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/payment_failed.html', {'order': order})



# ====================================================================================================================

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from decimal import Decimal

from .models import Product, Order, OrderItem, Profile
from .forms import UserProfileForm, ProfileForm, SignupForm


# --------------------------
# PROFILE OPTION PAGE
# --------------------------
def profile_options(request):
    return render(request, "shop/profile_options.html")


# --------------------------
# SIGNUP PAGE  (NEW FORM)
# --------------------------
def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            messages.success(request, "Account created. Please login.")
            return redirect("login")

    else:
        form = SignupForm()

    return render(request, "shop/signup.html", {"form": form})


# --------------------------
# LOGIN PAGE
# --------------------------
def login_view(request):
    form = AuthenticationForm()

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful. Welcome!")
            return redirect("welcome")

    return render(request, "shop/login.html", {"form": form})


# --------------------------
# WELCOME PAGE AFTER LOGIN
# --------------------------
def welcome(request):
    return render(request, "shop/welcome.html")


# --------------------------
# HOME PAGE
# --------------------------
def home(request):
    products = Product.objects.all()
    cart_count = sum(request.session.get('cart', {}).values())
    return render(request, 'shop/home.html', {'products': products, 'cart_count': cart_count})


# --------------------------
# CATEGORY PAGE
# --------------------------
def category_view(request, category_name):
    products = Product.objects.filter(category__iexact=category_name)
    cart_count = sum(request.session.get('cart', {}).values())
    return render(request, 'shop/category.html', {
        'products': products,
        'category_name': category_name,
        'cart_count': cart_count
    })


# --------------------------
# FILTERS PAGE
# --------------------------
def filters_page(request):
    order = request.GET.get('order')
    show = request.GET.get('show')

    products = Product.objects.all()

    if show == 'available':
        products = products.filter(available=True)

    if order == 'price_asc':
        products = products.order_by('price')
    elif order == 'price_desc':
        products = products.order_by('-price')

    return render(request, 'shop/filters.html', {
        'products': products,
        'cart_count': sum(request.session.get('cart', {}).values())
    })


# --------------------------
# PROFILE VIEW
# --------------------------
@login_required
def profile_view(request):
    user = request.user
    profile = user.profile

    if request.method == "POST":
        u_form = UserProfileForm(request.POST, instance=user)
        p_form = ProfileForm(request.POST, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")

    else:
        u_form = UserProfileForm(instance=user)
        p_form = ProfileForm(instance=profile)

    return render(request, "shop/profile.html", {
        "u_form": u_form,
        "p_form": p_form
    })


# --------------------------
# PRODUCT DETAIL
# --------------------------
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'cart_count': cart_count
    })


# --------------------------
# CART VIEW
# --------------------------
@login_required
def cart_view(request):
    cart = request.session.get('cart', {})
    items = []
    total = Decimal('0.00')

    for pid, qty in cart.items():
        try:
            p = Product.objects.get(pk=int(pid))
        except Product.DoesNotExist:
            continue
        items.append({'product': p, 'qty': qty, 'subtotal': p.price * qty})
        total += p.price * qty

    return render(request, 'shop/cart.html', {'items': items, 'total': total})


# --------------------------
# ADD TO CART
# --------------------------
@login_required
def cart_add(request, id):
    cart = request.session.get('cart', {})
    cart[str(id)] = cart.get(str(id), 0) + 1
    request.session['cart'] = cart
    return redirect(request.META.get('HTTP_REFERER', 'cart'))


# --------------------------
# REMOVE FROM CART
# --------------------------
@login_required
def cart_remove(request, id):
    cart = request.session.get('cart', {})
    if str(id) in cart:
        del cart[str(id)]
    request.session['cart'] = cart
    return redirect('cart')


# --------------------------
# CHECKOUT
# --------------------------
@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("home")

    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        address = request.POST.get('address', profile.address)
        order = Order.objects.create(user=request.user, address=address)

        for pid, qty in cart.items():
            p = Product.objects.get(pk=int(pid))
            OrderItem.objects.create(order=order, product=p, quantity=qty, price=p.price)

        request.session['cart'] = {}
        messages.success(request, f"Order placed successfully! Order ID: {order.id}")
        return redirect("home")

    items = []
    total = Decimal('0.00')

    for pid, qty in cart.items():
        p = Product.objects.get(pk=int(pid))
        items.append({'product': p, 'qty': qty, 'subtotal': p.price * qty})
        total += p.price * qty

    return render(request, 'shop/checkout.html', {
        'items': items,
        'total': total,
        'profile': profile
    })


# --------------------------
# LOGOUT VIEW
# --------------------------
def logout_view(request):
    logout(request)
    return redirect("/")
