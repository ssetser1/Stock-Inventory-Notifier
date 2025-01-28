from product_resolvers.cc_resolver import CanadaComputersResolver
import os
from aws_accesors import ssm_accessor, dynamodb_accessor
from discord import discord_publisher
from models.store import Store
from models.product import Product

PRODUCT_ID = "RX 7900"
PRODUCT_TITLE= "AMD Radeon RX 7900 XT Triple Fan 20GB GDDR6 PCIe 4.0 Graphics Card"
#OUT OF STOCK STORE (TEST)
#PRODUCT_URL = 'https://www.microcenter.com/product/681803/amd-radeon-rx-7900-xt-triple-fan-20gb-gddr6-pcie-40-graphics-card-?storeid=101'

# IN STOCK STORE 
PRODUCT_URL = 'https://www.microcenter.com/product/681803/amd-radeon-rx-7900-xt-triple-fan-20gb-gddr6-pcie-40-graphics-card-?storeid=085'

def find_product_availability() -> Product:
    resolver = CanadaComputersResolver(PRODUCT_ID, PRODUCT_URL, PRODUCT_TITLE)
    return resolver.resolve()

def publish_to_discord(product: Product) -> None:
    discord_webhook_url_arn = os.environ['DISCORD_WEBHOOK_URL_ARN']
    discord_webhook_url = ssm_accessor.retrieve_parameter(discord_webhook_url_arn)

    discord_publisher.publish(discord_webhook_url, product)

def handle(event, context):

    product = find_product_availability()
    previous = dynamodb_accessor.query_item(PRODUCT_ID, Store.MICROCENTER.name)

    # Case 1 - First time we've run - save state, publish if IS
    # Case 2 - Previous=OOS, Current=IS - publish & Save
    # Case 3 - Previous=IS, Current=OOS - save
    # Case 4 - Previous=OOS, Current=OOS - do nothing
    # Case 5 - Previous=IS, Current=IS - do nothing

    if previous is None:
        # Case 1
        print("First run - adding the item to dynamodb")
        dynamodb_accessor.put_item(product)
        if product.in_stock:
            print("Item is in stock - publish to discord")
            publish_to_discord(product)
    else:
        if previous.in_stock is False and product.in_stock is True:
            #Case 2    
            print("Product was previously out of stock, but is now in stock - publish and save!")
            publish_to_discord(product)
            dynamodb_accessor.put_item(product)
        elif previous.in_stock is True and product.in_stock is False:
            # Case 3
            print("Product was previously in stock but is now out of stock, just save state")
            dynamodb_accessor.put_item(product)
        else:
            #Case 4 & 5
            print("No change in stock status - noop")

#handle(None, None)