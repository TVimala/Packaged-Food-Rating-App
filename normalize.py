import re

SYNONYMS = {
    "sodium chloride": "salt",
    "sea salt": "salt",
    "iodized salt": "salt",
    "table salt": "salt",
    "black salt": "salt",
    "sucrose": "sugar",
    "glucose": "sugar",
    "fructose": "sugar",
    "corn syrup": "sugar",
    "high fructose corn syrup": "sugar",
    "dextrose": "sugar",
    "maltose": "sugar",
    "invert sugar": "sugar",
    "honey": "sugar",
    "molasses": "sugar",
    "treacle": "sugar",
    "brown sugar": "sugar",
    "raw sugar": "sugar",
    "agave nectar": "sugar",
    "maple syrup": "sugar",
    "palm oil": "fat",
    "vegetable oil": "fat",
    "canola oil": "fat",
    "rapeseed oil": "fat",
    "sunflower oil": "fat",
    "coconut oil": "fat",
    "butter": "fat",
    "margarine": "fat",
    "hydrogenated fat": "trans fat",
    "partially hydrogenated oil": "trans fat",
    "trans fat": "trans fat",
    "whey protein": "milk protein",
    "casein": "milk protein",
    "caseinate": "milk protein",
    "skimmed milk": "milk",
    "whole milk": "milk",
    "cream": "milk",
    "lactose": "milk sugar",
    "egg white": "egg",
    "egg yolk": "egg",
    "albumen": "egg",
    "gluten": "wheat protein",
    "semolina": "wheat",
    "farina": "wheat",
    "maida": "wheat flour",
    "refined wheat flour": "wheat flour",
    "atta": "whole wheat flour",
    "corn starch": "corn flour",
    "maize starch": "corn flour",
    "cornmeal": "corn",
    "modified starch": "starch",
    "tapioca starch": "starch",
    "potato starch": "starch",
    "sodium nitrite": "preservative",
}
def normalize_ingredient(ingredient: str) -> str:
    """
    Normalize an ingredient name by lowercasing, removing punctuation,
    and replacing synonyms with standard terms.
    """
    ingredient = ingredient.lower()
    ingredient = re.sub(r'[^\w\s]', '', ingredient)  
    # Replace synonyms
    for synonym, standard in SYNONYMS.items():
        pattern = r'\b' + re.escape(synonym) + r'\b'
        ingredient = re.sub(pattern, standard, ingredient)

    return ingredient.strip()

def normalize_nutrient_name(nutrient: str) -> str:
    """
    Prepare key nutrients as a flat dict with standard names:
    All values are per 100g. Missing fields set to None.
    Returns: dict with energy_kcal, sugars_g, salt_g, fat_g, saturated_fat_g, fiber_g, proteins_g
    """
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

if __name__ == "__main__":
    # Example usage
    from acquire import get_product_by_barcode, extract_text_from_image_url, search_product_name

    # Example: Fetch product by barcode
    barcode = "3017620429484"  
    product = get_product_by_barcode(barcode)
    if product:
        print("Product by Barcode:", product.get("product_name"))
        ingredients = product.get("ingredients_text", "")
        normalized_ingredients = [normalize_ingredient(ing) for ing in re.split(r',|\n', ingredients) if ing.strip()]
        print("Normalized Ingredients:", normalized_ingredients)

        nutrients = product.get("nutriments", {})
        normalized_nutrients = normalize_nutrient_name(nutrients)
        print("Normalized Nutrients:", normalized_nutrients)
    else:
        print("No product found for barcode:", barcode)
    # Example: OCR from URL
    url = "https://c8.alamy.com/comp/BA63M6/nutritional-label-on-food-packaging-for-ready-salted-crisps-BA63M6.jpg"
    ocr_text = extract_text_from_image_url(url)
    print("\nExtracted Text from Image URL:\n",ocr_text)
    print("\n NorMalized Ingredients from OCR:",normalize_ingredient(ocr_text))
    # Example: Search by Name
    results = search_product_name("Coca Cola", page_size=3)
    if results:
        print("Top Searches")
        for idx, prod in enumerate(results):
            pname = prod.get('product_name', 'No name')
            brand = prod.get('brands', 'No brand')
            print(f"{idx + 1}. {pname} [{brand}]")
        try:
            choice = int(input("Select the correct product (1/2/3): ")) - 1
            if 0 <= choice < len(results):
                selected =results[choice]
                print("Selected Product:", selected.get("product_name", ""))
                print("Normalized Ingredients:", [normalize_ingredient(ing) for ing in re.split(r',|\n', selected.get("ingredients_text", "")) if ing.strip()])
                print("Normalized Nutrients:", normalize_nutrient_name(selected.get("nutriments", {})))
            else:
                print("Invalid selection.")
        except Exception as e:
            print("Invalid input:", e)
    else:
        print("No products found by name.")