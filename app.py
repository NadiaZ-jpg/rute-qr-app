import streamlit as st
import qrcode
from io import BytesIO
import urllib.parse

st.set_page_config(page_title="Ruta QR Generator", page_icon="🗺️", layout="centered")
st.title("🗺️ Generator Cod QR pentru Rute Google Maps")

st.markdown("""
Creează rapid coduri QR pentru orice rută Google Maps.  
Introduceți **punctul de plecare**, **destinația finală** și **opriri intermediare**.  
Selectează modul de deplasare și apasă „Generează QR”.
""")

plecare = st.text_input("📍 Punct de plecare")
destinatie = st.text_input("🏁 Destinație finală")
opriri_text = st.text_input("📌 Opriri intermediare (separate prin ';')", placeholder="Ex: Ploiești;Brașov")
travelmode = st.selectbox("🚗 Mod de deplasare", ["mașina", "mers", "transit", "bicicleta"])

if st.button("🟢 Generează cod QR"):
    if plecare and destinatie:
        opriri = [o.strip() for o in opriri_text.split(";") if o.strip()]
        waypoints_str = "|".join(opriri) if opriri else ""

        url = f"https://www.google.com/maps/dir/?api=1&origin={plecare.replace(' ','+')}&destination={destinatie.replace(' ','+')}&travelmode={travelmode}"
        if waypoints_str:
            url += f"&waypoints={waypoints_str.replace(' ','+')}"

        # QR
        qr = qrcode.make(url)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        buf.seek(0)

        st.image(buf, caption="📲 Scanează pentru ruta Google Maps", use_container_width=True)
        st.markdown(f"🔗 [Deschide ruta în Google Maps]({url})")
        st.download_button("📥 Descarcă codul QR", buf, file_name="ruta_qr.png", mime="image/png")

        # Partajare rapidă
        url_encoded = urllib.parse.quote(url)
        st.markdown("### 📤 Partajare rapidă")
        st.markdown(f"- [WhatsApp](https://api.whatsapp.com/send?text={url_encoded})")
        st.markdown(f"- [Telegram](https://t.me/share/url?url={url_encoded}&text=Ruta QR)")
        st.markdown(f"- [Email](mailto:?subject=Ruta QR&body={url_encoded})")
    else:
        st.warning("⚠️ Te rog completează plecare și destinație.")
