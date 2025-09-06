import requests
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from io import BytesIO
import logging
pytesseract.pytesseract.tesseract_cmd = r"D:/Tesseract/tesseract.exe"
OPEN_FOOD_FACTS_SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"

def get_product_by_barcode(barcode:str)->dict:
    """
    Fetch product details from OpenFoodFacts using barcode.
    """
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == 1:
            return data["product"]
        return None
    else:
        response.raise_for_status()

def search_product_name(name:str,page_size:int = 3) -> list:
    """
    Search OpenFoodFacts by product name.
    Returns a list of product dicts.
    """
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": page_size,
    }
    response = requests.get(OPEN_FOOD_FACTS_SEARCH_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        return data.get("products", [])
    else:
        response.raise_for_status()


def extract_text_from_image_url(image_url:str)->str:
    """
    Extract text from an online image URL using OCR with preprocessing.
    """
    try:
        # 1. Fetch the image from the URL
        response = requests.get(image_url, stream=True, timeout=10)
        response.raise_for_status()  
        # 2. Open the image with Pillow
        img = Image.open(BytesIO(response.content))
        
        # 3. Preprocessing steps for better OCR accuracy
        # Convert to grayscale
        img = img.convert('L')
        
        # Increase contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2) # You can adjust this value
        
        # Apply a filter to sharpen the image
        img = img.filter(ImageFilter.SHARPEN)
        
        # Binarize the image (convert to pure black and white) using a threshold
        threshold = 128
        img = img.point(lambda p: p > threshold and 255)
        
        # 4. Use pytesseract to extract text from the preprocessed image
        text = pytesseract.image_to_string(img, lang="eng")
        
        # 5. Clean up the extracted text
        return text.strip()
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image from URL: {e}")
        return ""
    except Exception as e:
        print(f"An error occurred during OCR: {e}")
        return ""


def extract_text_from_local(image_path: str) -> str:
    """
    Extract text from a local image file.
    """
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang="eng")
    return text.strip()


if __name__ == "__main__":
    # Example: Barcode lookup
    product = get_product_by_barcode("3017620429484")
    if product:
        print("Product by Barcode:", product.get("product_name"))

    # Example: OCR from URL
    url = "https://c8.alamy.com/comp/BA63M6/nutritional-label-on-food-packaging-for-ready-salted-crisps-BA63M6.jpg"
    print("\nExtracted Text from Image URL:\n", extract_text_from_image_url(url))

    # Example: Search by Name
    results = search_product_name("Coca Cola", page_size=3)
    print("\nSearch Results:")
    for prod in results:
        print(prod.get("product_name"), "| Brand:", prod.get("brands"))