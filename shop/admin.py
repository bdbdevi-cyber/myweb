from django.contrib import admin
from .models import (
    Product,
    ProductImage,
    Profile,
    Order,
    OrderItem,
    Wishlist
)

# ---------- Product Images Inline ----------
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3


# ---------- Product Admin ----------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "available", "is_offer")
    list_filter = ("available", "is_offer")
    search_fields = ("name",)
    inlines = [ProductImageInline]


# ---------- Profile ----------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "address")


# ---------- Order ----------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "payment_method", "payment_status")
    list_filter = ("payment_status", "payment_method")
    search_fields = ("user__username",)


# ---------- Order Item ----------
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price")


# ---------- Wishlist ----------
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "product")
