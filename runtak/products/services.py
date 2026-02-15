import requests
from django.conf import settings

def send_order_to_mohasagor(order_data):
    url = "https://mohasagor.com.bd/api/reseller/order"

    headers = {
        "api-key": settings.MOHASAGOR_API_KEY,
        "secret-key": settings.MOHASAGOR_SECRET_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    response = requests.post(url, json=order_data, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()
