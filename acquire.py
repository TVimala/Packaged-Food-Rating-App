import requests 
from PIL import Image
import pytesseract
from io import BytesIO
OPEN_FOOD_FACTS_SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"
def get_product_by_barcode(barcode):
    url=f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 1:
            return data['product']
        else:
            return None
    else:
        response.raise_for_status()
def search_product_name(name,page_size=3):
    params = {
        'search_terms': name,
        'search_simple': 1,
        'action': 'process',
        'json': 1,
        'page_size': page_size
    }
    response = requests.get(OPEN_FOOD_FACTS_SEARCH_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        products= data.get('products', [])
    #     if products:
    #         return products[0]
    # return None 
    if products:
        return products
    return []
def extract_text_from_image(image_file):
    response = requests.get(image_file, stream=True)
    image = Image.open(BytesIO(response.content))
    text = pytesseract.image_to_string(image)
    return text.strip()

if __name__ == "__main__":
    p=get_product_by_barcode("3017620429484")
    print(p['product_name'])
    url = "https://images.openfoodfacts.org/images/products/301/762/042/9484/front_en.373.400.jpg"
    text=extract_text_from_image(url)
    print(text)
    res=search_product_name("Coca Cola",page_size=3)
    if res:
        for product in res:
            print(product['product_name'],product['brands'])
    else:
        print("No products found")