import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import qrcode
from io import BytesIO

st.title("Aplicație Rute Multiple & QR")

# --- Input: Lista de adrese ---
st.header("Introdu adresele (una pe linie)")
addresses_input = st.text_area("Opriri:", "București, România\nBrașov, România\nSibiu, România")
addresses = [a.strip() for a in addresses_input.split("\n") if a.strip()]

if st.button("Generează hartă și coduri QR"):
    geolocator = Nominatim(user_agent="rute_qr_app")
    locations = []
    failed = []

    # --- Geocoding pentru fiecare adresă ---
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

        # Adaugă marcatori și linie polilinie pentru rută
        coords = []
        for name, lat, lon in locations:
            folium.Marker([lat, lon], popup=name).add_to(m)
            coords.append([lat, lon])
        folium.PolyLine(coords, color="blue", weight=3, opacity=0.7).add_to(m)

        st_folium(m, width=700, height=500)

        # --- Generare coduri QR individuale ---
        st.header("Coduri QR pentru fiecare oprire")
        for name, lat, lon in locations:
            qr_data = f"{name} ({lat}, {lon})"
            qr_img = qrcode.make(qr_data)
            buf = BytesIO()
            qr_img.save(buf)
            st.image(buf, caption=qr_data)
    else:
        st.error("Trebuie să existe cel puțin două adrese valide pentru a genera ruta.")
