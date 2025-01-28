from models.store import Store
from models.product import Product
from playwright.sync_api import sync_playwright, TimeoutError

class CanadaComputersResolver:
    def __init__(self, product_id: str, product_url: str, product_title: str):
        self.store_name = Store.MICROCENTER
        self.product_id = product_id
        self.product_url = product_url
        self.product_title = product_title
    
    def resolve(self) -> Product:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(args=["--disable-gpu","--single-process"], headless=True)
                #browser = p.chromium.launch(args=["--disable-gpu","--single-process"], headless=False)
                page = browser.new_page()
                #page.set_default_timeout(5000) #5s
                page.goto(self.product_url)

                price = page.locator('span#pricing').get_attribute('content') # maybe put this after checking buy now button since it only shows price after buy now button

                in_stock_text = page.locator('span.msgInStock').first.text_content().strip()

                is_in_stock = in_stock_text == "NEW IN STOCK"
                result = Product(
                    id = self.product_id, 
                    name=self.product_title,
                    price=price,
                    url=self.product_url,
                    store=self.store_name,
                    in_stock=is_in_stock
                    )
                
                browser.close()

                return result
                
                
            except TimeoutError as te:
                price = page.locator('span#pricing').get_attribute('content')
                result = Product(
                    id = self.product_id, 
                    name=self.product_title,
                    price=price,
                    url=self.product_url,
                    store=self.store_name,
                    in_stock=False
                    )
                
                return result
            
        return None


            
            
