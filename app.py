import streamlit as st
import re
import logging
from acquire import get_product_by_barcode, search_product_name, extract_text_from_image_url
from normalize import normalize_ingredient, normalize_nutrient_name, extract_nutrition_from_text
from score import calculate_score

# --- Persistent logging setup ---
log_filename = "run.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    filemode="a",  
)
log = logging.info

# --- Streamlit setup ---
st.set_page_config(page_title="Health Analyzer", layout="centered")
st.markdown("<h2 style='color:#FFD600; text-align:center;'>Packaged Food Health Analyzer</h2>", unsafe_allow_html=True)

st.markdown("""
<style>
    .reportview-container { background: #16181b; }
    .sidebar .sidebar-content { background: #24262b; }
    .stButton>button {
        background-color: #FFD600;
        color: #24262b;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #a38f00; /* darker yellow */
        color: white !important;   /* white text on hover */
    }
    .stRadio label { color: #ffd600; }
    .stExpander > .summary { color: #ffd600 !important; }
</style>
""", unsafe_allow_html=True)
def color_band(band):
    band_colors = {
        "Healthy": "#40e600",          
        "Lightly Healthy": "#99ff33", 
        "Moderate": "#ffd600",         
        "Less Healthy": "#ff9933",     
        "Unhealthy": "#ff4545"         
    }
    return band_colors.get(band, "#ff4545")  
# --- Session state ---
if 'product' not in st.session_state: st.session_state.product = None
if 'ingreds' not in st.session_state: st.session_state.ingreds = []
if 'nutri' not in st.session_state: st.session_state.nutri = {}

log("=== NEW RUN START ===")

with st.sidebar:
    st.markdown('<h3 style="color:#FFD600;">Search Options</h3>', unsafe_allow_html=True)

    search_mode = st.radio(
        "Choose how you want to look up or analyze your food product:",
        ["Barcode", "Product Name", "Image URL"],
        index=0,   
        label_visibility="collapsed"
    )
def search_by_barcode():
    st.info("🔍 Searching by Barcode... (implement logic here)")

def search_by_name():
    st.info("🔍 Searching by Product Name... (implement logic here)")

def search_by_image():
    st.info("🔍 Searching by Image URL... (implement logic here)")

# --- Route based on selection ---
if search_mode == "Barcode":
    search_by_barcode()
elif search_mode == "Product Name":
    search_by_name()
elif search_mode == "Image URL":
    search_by_image()

# --- Barcode search ---
if search_mode == "Barcode":
    barcode = st.sidebar.text_input("Enter product barcode:")
    if st.sidebar.button("Fetch Product", use_container_width=True):
        with st.spinner("Looking up product..."):
            product = get_product_by_barcode(barcode)
            if product:
                st.session_state.product = product
                log(f"[INGEST] Barcode lookup: {barcode} → {product.get('product_name', '')}")
                st.success(f"Found: {product.get('product_name', '')}")
                st.image(product.get('image_url', ""), width=240)
            else:
                log(f"[INGEST] Barcode lookup failed: {barcode}")
                st.error("No product found.")
# --- Product name search ---
elif search_mode == "Product Name":
    query = st.sidebar.text_input("Enter product name:")
    if st.sidebar.button("Search Products", use_container_width=True):
        with st.spinner("Searching products..."):
            results = search_product_name(query, page_size=3)
            if results:
                # Display product images and options
                options = []
                for p in results:
                    # Create label with product name + brand
                    label = f"{p.get('product_name', 'No Name')} [{p.get('brands', 'No Brand')}]"
                    options.append(label)

                # One radio for all products
                selected_idx = st.radio("Select a product:", range(len(options)), format_func=lambda i: options[i])
                
                # Access the selected product data
                product = results[selected_idx]
                st.session_state.product = product

                # Display selected product image & info
                st.success(f"Selected: {product.get('product_name', '')}")
                st.image(product.get('image_url', ""), width=240)
                log(f"[INGEST] Product search: {query} → Selected {product.get('product_name', '')}")

            else:
                log(f"[INGEST] Product search failed: {query}")
                st.error("No products found.")

# --- Image/OCR input ---
elif search_mode == "Image URL":
    img_url = st.sidebar.text_input("Enter packaging image URL:")
    if st.sidebar.button("Extract Text", use_container_width=True):
        with st.spinner("Extracting text with OCR..."):
            ocr_text = extract_text_from_image_url(img_url)
            ingreds = [normalize_ingredient(i) for i in re.split(r',|\n|;', ocr_text) if i.strip()]
            nutri = extract_nutrition_from_text(ocr_text)
            nutri = {k: (v or 0) for k, v in nutri.items()}
            st.session_state.product = None
            st.session_state.ingreds = ingreds
            st.session_state.nutri = nutri
            log(f"[INGEST] OCR text extracted from URL: {img_url}")
            log(f"[NORMALIZE] Ingredients: {ingreds}")
            log(f"[NORMALIZE] Nutrients: {nutri}")

# --- Display product details & normalize ---
if st.session_state.product:
    product = st.session_state.product
    ingreds = [normalize_ingredient(i) for i in re.split(r',|\n|;', product.get("ingredients_text") or "") if i.strip()]
    nutri = normalize_nutrient_name(product.get("nutriments", {}))
    nutri = {k: (v or 0) for k, v in nutri.items()}
    st.session_state.ingreds = ingreds
    st.session_state.nutri = nutri
    st.markdown("<h4 style='color:#FFD600;'>Normalized Ingredients:</h4>", unsafe_allow_html=True)
    st.write(ingreds or "No ingredient info available.")
    st.markdown("<h4 style='color:#FFD600;'>Nutritional Information (per 100g):</h4>", unsafe_allow_html=True)
    st.write(nutri)
    log(f"[NORMALIZE] Product ingredients: {ingreds}")
    log(f"[NORMALIZE] Product nutrients: {nutri}")

# --- Health Score Analysis ---
if (st.session_state.nutri and st.session_state.ingreds) or st.session_state.product:
    if st.button("Analyze Health Score", key="score_button"):
        nutri = st.session_state.nutri
        log(f"[SCORE] Calculation started")
        score, grade,band, drivers, evidence = calculate_score(nutri)
        st.markdown(
            f"<h2 style='background-color:{color_band(band)}; color:#16181b; padding:0.4em 1em; border-radius:10px; text-align:center;'>{score} : {band}</h2>",
            unsafe_allow_html=True
        )
        with st.expander("Score Drivers & Evidence", expanded=True):
            for d, e in zip(drivers, evidence):
                st.markdown(f"<div style='color:#ffd600'><b>{d}</b><br><i>{e}</i></div>", unsafe_allow_html=True)
        log(f"[SCORE] Result: {score}, Band: {band}, Grade: {grade}")
        log(f"[EXPLAIN] Drivers: {drivers}")
        log(f"[EXPLAIN] Evidence: {evidence}")

# --- Info if nothing selected ---
if not st.session_state.product and not (st.session_state.ingreds and st.session_state.nutri):
    st.info("Search and select a product or extract ingredients/nutritional info to get the health score.")

st.markdown("---")
st.markdown(
    """<div style='color:#ffd600;font-size:1rem;margin-top:1.5em;'>Scoring based on Nutri-Score, UK FSA, and WHO guidelines.<br>See documentation for sources.</div>""", 
    unsafe_allow_html=True
)
log("=== RUN COMPLETE ===\n")