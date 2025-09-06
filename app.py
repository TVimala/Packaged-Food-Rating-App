import streamlit as st
import re
from acquire import get_product_by_barcode, search_product_name, extract_text_from_image_url
from normalize import normalize_ingredient, normalize_nutrient_name, extract_nutrition_from_text
from score import calculate_score

st.set_page_config(page_title="Health Analyzer", layout="centered")

# Theme and container setup
st.markdown(
    "<h2 style='color:#FFD600; text-align:center;'>Packaged Food Health Analyzer</h2>",
    unsafe_allow_html=True
)
st.markdown("""
    <style>
        .reportview-container { background: #16181b;}
        .sidebar .sidebar-content { background: #24262b;}
        .stButton>button { background-color: #FFD600; color: #24262b; border:none; }
        .stRadio label { color: #ffd600; }
        .stExpander > .summary { color: #ffd600 !important; }
    </style>
""", unsafe_allow_html=True)

def color_band(band):
    if "Green" in band: return "#40e600"
    if "Yellow" in band: return "#ffd600"
    return "#ff4545"

with st.sidebar:
    st.markdown('<h3 style="color:#FFD600;">Search Options</h3>', unsafe_allow_html=True)
    search_mode = st.radio(
        "", ["Barcode", "Product Name", "Image URL"],
        index=1,
        help="Choose how you want to look up or analyze your food product."
    )

product = None
ingreds = []
nutri = {}

if search_mode == "Barcode":
    barcode = st.sidebar.text_input("Enter product barcode:")
    if st.sidebar.button("Fetch Product", use_container_width=True):
        with st.spinner("Looking up product..."):
            product = get_product_by_barcode(barcode)
        if not product:
            st.error("No product found for this barcode.")
        else:
            st.success(f"Found: {product.get('product_name', '')}")
            st.image(product.get('image_url', ""), width=240)

elif search_mode == "Product Name":
    query = st.sidebar.text_input("Enter product name:")
    if st.sidebar.button("Search Products", use_container_width=True):
        with st.spinner("Searching products..."):
            results = search_product_name(query, page_size=3)
        if not results:
            st.error("No products found.")
        else:
            st.write("### Top Matches")
            options = [
                f"{prod.get('product_name', 'No name')} [{prod.get('brands', 'No brand')}]"
                for prod in results
            ]
            idx = st.radio("Select product below:", range(len(options)), format_func=lambda i: options[i])
            product = results[idx]
            st.success(f"Selected: {product.get('product_name', '')}")
            st.image(product.get('image_url', ""), width=240)

elif search_mode == "Image URL":
    img_url = st.sidebar.text_input("Enter packaging image URL:")
    if st.sidebar.button("Extract Text", use_container_width=True):
        with st.spinner("Extracting text with OCR..."):
            ocr_text = extract_text_from_image_url(img_url)
        with st.expander("Extracted Ingredients & Nutrition Label Text", expanded=False):
            st.write(ocr_text)
        ingreds = [normalize_ingredient(ing) for ing in re.split(r',|\n|;', ocr_text) if ing.strip()]
        with st.expander("Normalized Ingredients", expanded=True):
            st.write(ingreds)
        # Parse nutrients from OCR text
        nutri = extract_nutrition_from_text(ocr_text)
        st.write("### Nutritional Information (extracted from image):")
        st.write(nutri if nutri else "No nutrition values detected in image.")
        product = None  

        # Score only if we were able to extract nutrients
        if nutri:
            if st.button("Analyze Health Score", key="score_from_image"):
                score, band, drivers, evidence = calculate_score(nutri)
                st.markdown(
                    f"<h2 style='background-color:{color_band(band)}; color:#16181b; padding:0.4em 1em; border-radius:10px; text-align:center;'>{score} : {band}</h2>",
                    unsafe_allow_html=True
                )
                with st.expander("Score Drivers & Evidence", expanded=True):
                    for d, e in zip(drivers, evidence):
                        st.markdown(f"<div style='color:#ffd600'><b>{d}</b><br><i>{e}</i></div>", unsafe_allow_html=True)
        else:
            st.info("No nutritional info detected. Only ingredients available.")

# Product scoring/results display (product came from barcode/name)
if product:
    with st.container():
        st.markdown(
            "<h4 style='color:#FFD600;'>Normalized Ingredients:</h4>",
            unsafe_allow_html=True
        )
        ingreds = [normalize_ingredient(ing) for ing in re.split(r',|\n|;', product.get("ingredients_text") or "") if ing.strip()]
        st.write(ingreds or "No ingredient info available.")

        nutri = normalize_nutrient_name(product.get("nutriments", {}))
        st.markdown(
            "<h4 style='color:#FFD600;'>Nutritional Information (per 100g):</h4>",
            unsafe_allow_html=True
        )
        st.write(nutri)

        score_button = st.button("Analyze Health Score", use_container_width=True)
        if score_button:
            score, band, drivers, evidence = calculate_score(nutri)
            st.markdown(
                f"<h2 style='background-color:{color_band(band)}; color:#16181b; padding:0.4em 1em; border-radius:10px; text-align:center;'>{score} : {band}</h2>",
                unsafe_allow_html=True
            )
            with st.expander("See why this is the score ➜", expanded=True):
                for d, e in zip(drivers, evidence):
                    st.markdown(f"<div style='color:#ffd600'><b>{d}</b><br><i>{e}</i></div>", unsafe_allow_html=True)

if not product and not (ingreds and nutri):
    st.info("Search and select a product or extract ingredients/nutritional info to get the health score.")

st.markdown("---")
st.markdown(
    """<div style='color:#ffd600;font-size:1rem;margin-top:1.5em;'>Scoring based on Nutri-Score, UK FSA, and WHO guidelines.<br>See documentation for sources.</div>""", 
    unsafe_allow_html=True
)