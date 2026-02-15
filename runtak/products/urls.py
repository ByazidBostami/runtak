from django.urls import path
from .views import product_list, product_detail, place_order, cart_view

urlpatterns = [
    path("", product_list, name="home"),
    path("product/<int:pk>/", product_detail, name="product_detail"),
    path("cart/", cart_view, name="cart"),   # ✅ FIX
    path("order/", place_order, name="place_order"),
]
