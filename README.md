# Packaged Food Rating App
A Streamlit-based application to rate packaged foods by calculating a Health Score from nutrition information.  
The app lets users search by Barcode, Product Name, or Image URL, standardizes the data, and computes a score (0–100) based on sugar, fat, and salt content.

## 🏗 High-Level Architecture

```
┌─────────────┐    ┌──────────────┐    ┌───────────┐    ┌──────────────┐
│ acquire.py  │──▶│ normalize.py │──▶│ score.py   │──▶│ app.py (UI)   │
└─────────────┘    └──────────────┘    └───────────┘    └──────────────┘
    (fetch raw)        (standardize)      (compute)        (Streamlit)
```

## Module Roles & I/O Schemas

### acquire.py
- **Input:** query (Barcode, Product Name, or Image URL)
- **Output:** `raw_product_data` (dict)
  ```python
  {
     "name": "Oreo Biscuits",
     "sugar": 38,
     "fat": 20,
     "salt": 0.5
  }
  ```

### normalize.py
- **Input:** `raw_product_data` (dict)
- **Output:** `normalized_data` (dict, floats)
  ```python
  {
     "sugar": 38.0,
     "fat": 20.0,
     "salt": 0.5
  }
  ```

### score.py
- **Input:** `normalized_data` (dict)
- **Output:** `health_score` (int, 0–100)

### app.py
- Integrates all modules
- Provides Streamlit UI for user interaction
- Logs events into `logs/app_log.txt`

## 📊 Scoring Design

- **Score Range:** 0 – 100

**Bands:**
- 🟢 80–100 → Healthy
- 🟡 50–79 → Moderate
- 🔴 0–49 → Unhealthy

**Guardrails:**
- Score capped at 100 (max) and floored at 0 (min)

**Deductions:**
- sugar × 0.5
- fat × 0.3
- salt × 1.0

## ⚙️ Installation & Setup

1. **Clone the repository**
    ```sh
    git clone https://github.com/yourusername/packaged-food-rating-app.git
    cd packaged-food-rating-app
    ```

2. **Create virtual environment & install dependencies**
    ```sh
    python -m venv venv
    source venv/bin/activate      # (Linux/Mac)
    venv\Scripts\activate         # (Windows)
    pip install -r requirements.txt
    ```

3. **Run the app (single command 🚀)**
    ```sh
    streamlit run app.py
    ```

## Outputs

- **Streamlit UI:** shows live Health Score results
- **Logs:** saved at `logs/app_log.txt`

**Example log entry:**
```
2025-09-05 18:50:12 [INFO] [Score] Final Health Score = 59
```

## Refreshing Cached Records

If product data looks stale:
- Delete the cached file (if you implement caching later, e.g., `cache/`).
- Restart the app:
  ```sh
  streamlit run app.py
  ```
- Logs will show fresh acquisition steps.

## 📚 References & Citations

- [WHO Guidelines on Sugars Intake for Adults and Children](https://www.who.int/publications/i/item/9789241549028)
- [FDA – Guidance for Industry: Nutrition Labeling Manual](https://www.fda.gov/media/81606/download)
- [FSSAI (Food Safety and Standards Authority of India) Nutritional Standards](https://www.fssai.gov.in/)
