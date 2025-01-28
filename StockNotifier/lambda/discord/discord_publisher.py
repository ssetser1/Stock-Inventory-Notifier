import requests
from models.product import Product

def publish(webhook_url: str, product: Product) -> None:
    payload = {
        "embeds": [{
            "title": "STOCK ALERT !!!",
            "description": str(product),
            "url": "https://www.microcenter.com/product/681803/amd-radeon-rx-7900-xt-triple-fan-20gb-gddr6-pcie-40-graphics-card-?storeid=085",
            "color": 5763719
        }]
    }

    response = requests.post(webhook_url, json = payload)
    response.raise_for_status()