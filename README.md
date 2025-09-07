# Packaged-Food-Rating-App

A Streamlit-based application to rate packaged foods by calculating a Health Score from nutrition information.  
Users can search by Barcode, Product Name, or Image URL. The app standardizes nutrition data and computes a score (0–100) based on sugar, fat, and salt content.

---

### 🏗 High-Level Architecture

```
┌─────────────┐   ┌──────────────┐   ┌───────────┐   ┌──────────────┐
│ acquire.py  │──▶│ normalize.py │──▶│ score.py  │──▶│ app.py (UI)  │
└─────────────┘   └──────────────┘   └───────────┘   └──────────────┘
    (fetch raw)      (standardize)      (compute)      (Streamlit)
```

---

### Module Roles & I/O Schemas

#### `acquire.py`
- **Input:** query (Barcode, Product Name, or Image URL)
- **Output:** `raw_product_data` (dict)
  ```json
  {
     "name": "Oreo Biscuits",
     "sugar": 38,
     "fat": 20,
     "salt": 0.5
  }
  ```

#### `normalize.py`
- **Input:** `raw_product_data` (dict)
- **Output:** `normalized_data` (dict, floats)
  ```json
  {
     "sugar": 38.0,
     "fat": 20.0,
     "salt": 0.5
  }
  ```

#### `score.py`
- **Input:** `normalized_data` (dict)
- **Output:** `health_score` (int, 0–100)

#### `app.py`
- Integrates all modules
- Provides Streamlit UI for user interaction
- Logs events into `run.log`

---
### 🗂 Run Artifacts

This repository includes:
- `run.log` → Full run logs from the last execution.
- `trace_example.txt` → Short trace of a single run (ingest → normalize → score → explain).
- `samples/outputs/` → JSON/CSV outputs for 3 example products.
- `samples/screenshots/` → Screenshots of the UI showing results.
<!-- - `REFERENCES.md` → Source/Reference manifest (databases used, limitations). -->
---

### 📊 Scoring Design

- **Score Range:** 0 – 100

#### Bands
- 🟢 80–100 → Healthy
- 🟡 50–79 → Moderate
- 🔴 0–49 → Unhealthy

#### Guardrails
- Score capped at 100 (max) and floored at 0 (min)

#### Deductions
- sugar × 0.5
- fat × 0.3
- salt × 1.0

---

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

### Outputs

- **Streamlit UI:** Shows live Health Score results
- **Logs:** Saved at `logs/app_log.txt`

  Example log entry:
  ```
  2025-09-05 18:50:12 [INFO] [Score] Final Health Score = 59
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
