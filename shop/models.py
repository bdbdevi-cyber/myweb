from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


# -----------------------
# PROFILE MODEL
# -----------------------
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.user.username


# -----------------------
# PRODUCT MODEL
# -----------------------
class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    available = models.BooleanField(default=True)
    # image = models.ImageField(upload_to='products/', blank=True, null=True)
    image = models.ImageField(upload_to='products/')

    description = models.TextField(blank=True)
    show_on_homepage = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.id])


# ===============================
# ORDER MODEL (UPDATED FOR PAYMENT)
# ===============================
class Order(models.Model):

    PAYMENT_METHODS = [
        ("COD", "Cash on Delivery"),
        ("RAZORPAY", "Razorpay Online Payment"),
        ("UPI", "UPI Payment"),
    ]

    PAYMENT_STATUS = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("FAILED", "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    delivered = models.BooleanField(default=False)
    address = models.TextField(blank=True)

    # 👇 new fields for payments
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default="COD")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="PENDING")
    razorpay_order_id = models.CharField(max_length=200, blank=True)
    razorpay_payment_id = models.CharField(max_length=200, blank=True)
    razorpay_signature = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


# -----------------------
# ORDER ITEM MODEL
# -----------------------
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
