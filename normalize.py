import re
from acquire import get_product_by_barcode, extract_text_from_image_url, search_product_name

SYNONYMS = {
    "salt":      ["sodium chloride", "sea salt", "table salt", "salt"],
    "sugar":     ["sucrose", "glucose", "fructose", "corn syrup", "sugar", "brown sugar", "dextrose", "maltose", "invert sugar", "honey", "molasses", "agave nectar", "maple syrup"],
    "fat":       ["palm oil", "vegetable oil", "canola oil", "butter", "margarine", "coconut oil", "sunflower oil", "rapeseed oil"],
    "trans fat": ["hydrogenated fat", "partially hydrogenated oil", "trans fat"],
    "wheat":     ["semolina", "farina", "maida", "atta", "refined wheat flour", "wheat flour", "wheat"],
    "milk":      ["skimmed milk", "whole milk", "cream", "milk", "casein", "caseinate", "whey protein", "lactose"],
    "egg":       ["egg white", "egg yolk", "albumen", "egg"],
}

def normalize_ingredient(ingredient: str) -> str:
    """Lowercase, remove punctuation, replace synonyms with standard terms."""
    ingredient = ingredient.lower()
    ingredient = re.sub(r'[^\w\s]', '', ingredient)
    for standard, variants in SYNONYMS.items():
        for var in variants:
            pattern = r'\b' + re.escape(var) + r'\b'
            ingredient = re.sub(pattern, standard, ingredient)
    return ingredient.strip()

def normalize_ingredients(ingredients_text: str) -> list:
    """Splits a string and normalizes all ingredient tokens."""
    tokens = re.split(r',|;|\n', ingredients_text)
    result = [normalize_ingredient(tok) for tok in tokens if tok.strip()]
    return list(dict.fromkeys(result))

def normalize_nutrient_name(nutrient: dict) -> dict:
    """Standardizes nutrient data and casts to float where possible."""
    def safe_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
    return {
        "energy_kcal": safe_float(nutrient.get("energy-kcal_100g")),
        "sugars_g": safe_float(nutrient.get("sugars_100g")),
        "salt_g": safe_float(nutrient.get("salt_100g")),
        "fat_g": safe_float(nutrient.get("fat_100g")),
        "saturated_fat_g": safe_float(nutrient.get("saturated-fat_100g")),
        "fiber_g": safe_float(nutrient.get("fiber_100g")),
        "proteins_g": safe_float(nutrient.get("proteins_100g")),
    }
def extract_nutrition_from_text(raw_text: str) -> dict:
    """
    Extract common nutrition fields from raw OCR text (very basic example).
    """
    res = {}
    if m := re.search(r"(\d+)\s*(kcal|cal)", raw_text.lower()):
        res["energy_kcal"] = float(m.group(1))
    if m := re.search(r"(\d+\.?\d*)\s*g\s*fat", raw_text.lower()):
        res["fat_g"] = float(m.group(1))
    if m := re.search(r"(\d+\.?\d*)\s*g\s*saturat", raw_text.lower()):
        res["saturated_fat_g"] = float(m.group(1))
    if m := re.search(r"(\d+\.?\d*)\s*g\s*carbohydrate", raw_text.lower()):
        res["carbohydrate_g"] = float(m.group(1))
    if m := re.search(r"(\d+\.?\d*)\s*g\s*sugars?", raw_text.lower()):
        res["sugars_g"] = float(m.group(1))
    if m := re.search(r"(\d+\.?\d*)\s*g\s*fiber", raw_text.lower()):
        res["fiber_g"] = float(m.group(1))
    if m := re.search(r"(\d+\.?\d*)\s*g\s*salt", raw_text.lower()):
        res["salt_g"] = float(m.group(1))
    return res
if __name__ == "__main__":
    print("Packaged Food Normalization System")
    print("Pick input source:\n1. Barcode\n2. Product name\n3. Image URL (OCR)\n4. Manual ingredients")
    mode = input("Select mode (1/2/3/4): ").strip()

    if mode == "1":
        barcode = input("Enter product barcode: ").strip()
        product = get_product_by_barcode(barcode)
        if product:
            name = product.get('product_name', 'No name')
            print("Product:", name)
            ingredients_text = product.get("ingredients_text", "")
            norm_ingredients = normalize_ingredients(ingredients_text)
            print("Normalized Ingredients:", norm_ingredients)
            norm_nutrients = normalize_nutrient_name(product.get("nutriments", {}))
            print("Normalized Nutrients (per 100g):", norm_nutrients)
        else:
            print("No product found for this barcode.")
    elif mode == "2":
        name = input("Enter product name: ").strip()
        results = search_product_name(name, page_size=3)
        if not results:
            print("No products found.")
        else:
            for idx, prod in enumerate(results):
                pname = prod.get('product_name', 'No name')
                brand = prod.get('brands', 'No brand')
                print(f"{idx + 1}. {pname} [{brand}]")
            try:
                choice = int(input("Select product (1/2/3): ")) - 1
                if 0 <= choice < len(results):
                    selected = results[choice]
                    print("Product:", selected.get("product_name", ""))
                    norm_ingredients = normalize_ingredients(selected.get("ingredients_text", ""))
                    print("Normalized Ingredients:", norm_ingredients)
                    norm_nutrients = normalize_nutrient_name(selected.get("nutriments", {}))
                    print("Normalized Nutrients (per 100g):", norm_nutrients)
                else:
                    print("Invalid selection.")
            except Exception as e:
                print("Invalid input:", e)
    elif mode == "3":
        img_url = input("Enter image URL: ").strip()
        ocr_text = extract_text_from_image_url(img_url)
        print("OCR Extracted Text:", ocr_text)
        norm_ingredients = normalize_ingredients(ocr_text)
        print("Normalized Ingredients from OCR:", norm_ingredients)
    elif mode == "4":
        user_text = input("Enter ingredients (comma/semicolon separated): ")
        norm_ingredients = normalize_ingredients(user_text)
        print("Normalized Ingredients:", norm_ingredients)
    else:
        print("Invalid mode selected.")
