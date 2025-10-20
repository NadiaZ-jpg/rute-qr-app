import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import qrcode
from PIL import Image
from io import BytesIO
import urllib.parse

st.set_page_config(page_title="ruteQR", layout="wide")
st.title("ruteQR")

# --- Istoric rutelor (în memorie) ---
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["Ruta", "Google Maps URL"])

# --- Input: Lista de adrese ---
st.header("Introdu adresele (una pe linie)")
addresses_input = st.text_area("Opriri:", "București, România\nBrașov, România\nSibiu, România")
addresses = [a.strip() for a in addresses_input.split("\n") if a.strip()]

# --- Setări QR personalizat ---
st.sidebar.header("Setări QR")
qr_color = st.sidebar.color_picker("Culoare QR", "#000000")
bg_color = st.sidebar.color_picker("Culoare fundal", "#ffffff")
qr_size = st.sidebar.slider("Dimensiune QR (pixeli)", 200, 800, 400)
logo_file = st.sidebar.file_uploader("Logo în centru (PNG)", type=["png"])

# --- Buton pentru generare ---
if st.button("Generează hartă și QR Google Maps"):
    geolocator = Nominatim(user_agent="rute_qr_app")
    locations = []
    failed = []

    # --- Geocoding ---
    for addr in addresses:
        loc = geolocator.geocode(addr)
        if loc:
            locations.append((addr, loc.latitude, loc.longitude))
        else:
            failed.append(addr)

    if failed:
        st.warning(f"Nu am putut găsi următoarele adrese: {', '.join(failed)}")

    if len(locations) >= 2:
        # --- Hartă Folium ---
        avg_lat = sum([lat for _, lat, _ in locations])/len(locations)
        avg_lon = sum([lon for _, _, lon in locations])/len(locations)
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=7)
        coords = []
        for name, lat, lon in locations:
            folium.Marker([lat, lon], popup=name).add_to(m)
            coords.append([lat, lon])
        folium.PolyLine(coords, color="blue", weight=3, opacity=0.7).add_to(m)
        st_folium(m, width=700, height=500)

        # --- Link Google Maps ---
        base_url = "https://www.google.com/maps/dir/"
        route_str = " -> ".join([addr for addr, _, _ in locations])
        route_url = base_url + "/".join([urllib.parse.quote(addr) for addr, _, _ in locations])

        # --- Generare QR personalizat ---
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4
        )
        qr.add_data(route_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color=qr_color, back_color=bg_color).convert('RGB')

        if logo_file:
            logo = Image.open(logo_file)
            box_size = qr_img.size[0] // 4
            logo = logo.resize((box_size, box_size))
            pos = ((qr_img.size[0]-box_size)//2, (qr_img.size[1]-box_size)//2)
            qr_img.paste(logo, pos, mask=logo)

        qr_img = qr_img.resize((qr_size, qr_size))
        buf = BytesIO()
        qr_img.save(buf, format="PNG")
        buf.seek(0)

        st.header("QR personalizat pentru ruta completă")
        st.image(buf, caption="QR pentru ruta completă")
        st.download_button("Descarcă QR ca PNG", buf, file_name="ruta_completa_qr.png", mime="image/png")

        # --- Salvare istoric în sesiune ---
        st.session_state.history = pd.concat([
            st.session_state.history,
            pd.DataFrame({"Ruta":[route_str], "Google Maps URL":[route_url]})
        ], ignore_index=True)

# --- Afișare istoric și export CSV ---
if not st.session_state.history.empty:
    st.header("Istoric rute generate")
    st.dataframe(st.session_state.history)

    csv_buf = BytesIO()
    st.session_state.history.to_csv(csv_buf, index=False)
    csv_buf.seek(0)
    st.download_button("Exportă istoricul ca CSV", csv_buf, file_name="istoric_rute.csv", mime="text/csv")
