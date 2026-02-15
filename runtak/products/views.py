from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.conf import settings
import requests

from .models import Product, Category


# --------------------------------------------------
# PRODUCT LIST WITH PAGINATION
# --------------------------------------------------
def product_list(request):
    cat = request.GET.get("cat")
    q = request.GET.get("q")

    products_qs = Product.objects.all().order_by("-id")

    if cat:
        products_qs = products_qs.filter(category_id=cat)

    if q:
        products_qs = products_qs.filter(name__icontains=q)

    paginator = Paginator(products_qs, 20)  # ✅ 20 products per page
    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)

    categories = Category.objects.all()

    return render(request, "shop/product_list.html", {
        "products": products,
        "categories": categories,
        "active_cat": cat,
    })


# --------------------------------------------------
# PRODUCT DETAIL
# --------------------------------------------------
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "shop/product_detail.html", {
        "product": product
    })


# --------------------------------------------------
# CART PAGE
# --------------------------------------------------
def cart_view(request):
    return render(request, "shop/cart.html")


# --------------------------------------------------
# PLACE ORDER (MOHASAGOR API)
# --------------------------------------------------
def place_order(request):
    if request.method != "POST":
        return HttpResponse("Invalid request", status=400)

    payload = {
        "name": request.POST.get("name"),
        "phone": request.POST.get("phone"),
        "address": request.POST.get("address"),
        "product_id": request.POST.get("product_id"),
        "quantity": 1,
    }

    headers = {
        "api-key": settings.MOHASAGOR_API_KEY,
        "secret-key": settings.MOHASAGOR_SECRET_KEY,
        "Accept": "application/json",
    }

    response = requests.post(
        "https://mohasagor.com.bd/api/reseller/order",
        headers=headers,
        json=payload,
        timeout=30,
    )

    if response.status_code != 200:
        return HttpResponse("Order failed", status=500)

    return HttpResponse("Order placed successfully")
