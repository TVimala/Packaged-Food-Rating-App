# Packaged-Food-Rating-App

A Streamlit-based application to rate packaged foods by calculating a Health Score from nutrition information.  
Users can search by Barcode, Product Name, or Image URL. The app standardizes nutrition data and computes a score (0–100) based on nutrients.

---

### 🏗 High-Level Architecture

```
┌─────────────┐   ┌──────────────┐   ┌───────────┐   ┌──────────────┐
│ acquire.py  │──▶│ normalize.py │──▶│ score.py  │──▶│ app.py (UI)  │
└─────────────┘   └──────────────┘   └───────────┘   └──────────────┘
    (fetch raw)      (standardize)      (compute)      (Streamlit)
```

## Repository Contents

```
Packaged-Food-Rating-App/
│
├─ app.py                    # Streamlit frontend + orchestration
├─ acquire.py                # API fetch & OCR extraction functions
├─ normalize.py              # Ingredient and nutrient normalization
├─ score.py                  # Health score calculation & explanation
├─ requirements.txt          # Python dependencies
├─ run.log                   # Full log of last run
├─ trace_example.txt         # Short trace: ingest → normalize → score → explain
├─ samples/
│   ├─ outputs/              # JSON/CSV outputs for 3+ products
│   └─ screenshots/          # Screenshots of UI pages
├─ config_template.json      # Sample configuration template
└─ README.md
```

---

## Module I/O Schemas

### `acquire.py`
- **Input:** Barcode, Product Name, or Image URL (OCR)
- **Output:** `raw_product_data` (dict)
  ```json
  {
    "product_name": "Ready Salted Crisps",
    "brands": "Lay's",
    "ingredients_text": "Potatoes, sunflower oil, salt",
    "nutriments": {
        "energy-kcal_100g": 133,
        "fat_100g": 8.5,
        "salt_100g": 2.4
    },
    "image_url": "https://c8.alamy.com/comp/BA63M6/nutritional-label-on-food-packaging-for-ready-salted-crisps-BA63M6.jpg"
  }
  ```

### `normalize.py`
- **Input:** `raw_product_data` or OCR text
- **Output:** `normalized_data` (dict)
  ```json
  {
    "ingredients": ["potatoes", "fat", "salt"],
    "nutrients": {
        "energy_kcal": 133.0,
        "fat_g": 8.5,
        "salt_g": 2.4
    }
  }
  ```

### `score.py`
- **Input:** `normalized_data` (dict)
- **Output:** Health score details
  ```json
  {
    "score": 50,
    "band": "Moderate",
    "grade": "C",
    "drivers": ["High sodium: 24 g salt/100g"],
    "evidence": ["Sodium > 900 mg/100g"]
  }
  ```

---

## 📊 Health Score Design

- **Range:** 0 – 100 (higher = healthier)
- **Bands:**
  - 80–100 → Healthy (A)
  - 65–79 → Lightly Healthy (B)
  - 50–64 → Moderate (C)
  - 35–49 → Less Healthy (D)
  - 0–34 → Unhealthy (E)
- **Negative Points:** Energy (kcal), sugar (total & added), saturated fat, salt (sodium), ultra-processed food penalty
- **Positive Points:** Fiber, protein, fruit/vegetable content
- **Score:** Normalized to 0–100 and mapped to Nutri-Score grades

---

## 🖥️ Streamlit UI Features

- **Sidebar Search Modes:** Barcode, Product Name, Image URL (OCR)
- **Displays:** Normalized ingredients, nutritional info per 100g, health score + band, drivers & evidence (expandable panel)
- **Logs:** Saved at `run.log`
  ```
  2025-09-07 15:10:12 [INFO] [SCORE] Result: 50, Band: Moderate, Grade: C
  ```

---

## Sample Output

```json
{
  "product_name": "Ready Salted Crisps",
  "nutrients": {
    "energy_kcal": 133,
    "fat_g": 8.5,
    "salt_g": 2.4
  },
  "score": {
    "value": 50,
    "band": "Moderate",
    "grade": "C"
  },
  "explanation": {
    "drivers": ["High sodium: 24 g salt/100g"],
    "evidence": ["Sodium > 900 mg/100g"]
  }
}
```

---

## 🔖 Config Sample (`config_template.json`)

```json
{
  "tesseract_path": "D:/Tesseract/tesseract.exe",
  "openfoodfacts_url": "https://world.openfoodfacts.org/api/v0/product",
  "ocr_languages": ["eng"]
}
```
---
<!-- 
### 🗂 Run Artifacts

This repository includes:
- `run.log` → Full run logs from the last execution.
- `trace_example.txt` → Short trace of a single run (ingest → normalize → score → explain).
- `samples/outputs/` → JSON/CSV outputs for 3 example products.
- `samples/screenshots/` → Screenshots of the UI showing results.

--- -->

### ⚙️ Installation & Setup

1. **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/packaged-food-rating-app.git
    cd packaged-food-rating-app
    ```

2. **Create virtual environment & install dependencies**
    ```bash
    python -m venv venv
    source venv/bin/activate   # (Linux/Mac)
    venv\Scripts\activate      # (Windows)
    pip install -r requirements.txt
    ```

3. **Run the app**
    ```bash
    streamlit run app.py
    ```

---

### Refreshing Cached Records

If product data looks stale:
- Delete the cached file (if implemented, e.g., `cache/`)
- Restart the app:
  ```bash
  streamlit run app.py
  ```
- Logs will show fresh acquisition steps.

---

### 🚧 Limitations & Future Work
- Some products may not have barcodes in OpenFoodFacts.
- OCR may miss text in blurry/curved packaging images.
- Scoring is simplified (not a medical substitute).
- Future: add support for multiple languages and offline caching.
---

### 📚 References & Citations

- [WHO Guidelines on Sugars Intake for Adults and Children](https://www.who.int/publications/i/item/9789241549028)
- [FDA – Guidance for Industry: Nutrition Labeling Manual](https://www.fda.gov/media/81606/download)
- [FSSAI Nutritional Standards](https://www.fssai.gov.in/)
