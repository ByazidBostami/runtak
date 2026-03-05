from celery import shared_task
import requests
from django.conf import settings
from .models import Product, Category

BASE_IMAGE_URL = "https://mohasagor.com.bd/public/storage/"

HEADERS = {
    "api-key": settings.MOHASAGOR_API_KEY,
    "secret-key": settings.MOHASAGOR_SECRET_KEY,
    "Accept": "application/json",
}


def safe_json(response):
    """
    Safely parse JSON. Return {} if response is empty or invalid.
    """
    try:
        return response.json()
    except ValueError:
        return {}


# --------------------------------------------------
# SYNC CATEGORIES
# --------------------------------------------------
@shared_task(
    bind=True,
    autoretry_for=(requests.RequestException,),
    retry_kwargs={"max_retries": 3, "countdown": 15},
)
def sync_categories(self):
    url = "https://mohasagor.com.bd/api/reseller/category"

    response = requests.get(url, headers=HEADERS, timeout=60)
    response.raise_for_status()

    data = safe_json(response)
    categories = data.get("categories", [])

    for c in categories:
        if not c.get("id"):
            continue

        Category.objects.update_or_create(
            external_id=c["id"],
            defaults={
                "name": c.get("name", "")
            },
        )

    return f"{len(categories)} categories synced"


# --------------------------------------------------
# SYNC PRODUCTS
# --------------------------------------------------
@shared_task(
    bind=True,
    autoretry_for=(requests.RequestException,),
    retry_kwargs={"max_retries": 3, "countdown": 15},
)
def sync_products(self):
    page = 1
    total_synced = 0

    while True:
        url = "https://mohasagor.com.bd/api/reseller/product"
        params = {
            "page": page,
            "limit": 200,
        }

        response = requests.get(
            url,
            headers=HEADERS,
            params=params,
            timeout=60,
        )

        if response.status_code != 200:
            break

        data = safe_json(response)
        products = data.get("products", [])

        if not products:
            break

        for item in products:
            image_url = ""

            # 1️⃣ product_image array (best quality)
            images = item.get("product_image", [])
            if images and images[0].get("product_image"):
                image_url = (
                    BASE_IMAGE_URL
                    + images[0]["product_image"].lstrip("/")
                )

            # 2️⃣ thumbnail fallback
            elif item.get("thumbnail_img"):
                image_url = (
                    BASE_IMAGE_URL
                    + "images/products/"
                    + item["thumbnail_img"].lstrip("/")
                )

            Product.objects.update_or_create(
                external_id=item["id"],
                defaults={
                    "name": item.get("name", ""),
                    "slug": item.get("slug", ""),
                    "description": item.get("details", ""),
                    "price": float(item.get("price") or 0),
                    "sale_price": float(item.get("sale_price") or 0),
                    "stock": int(item.get("stock") or 0),
                    "category_id": int(item.get("category_id") or 0),
                    "image": image_url,
                },
            )

            total_synced += 1

        page += 1

    return f"{total_synced} products synced successfully"
