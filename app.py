from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components

# --- STREAMLIT SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Perplexity Entegre Arayüz", page_icon="🌐", layout="wide"
)

# --- ÖZEL STİL VE ARKA PLAN ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #FCFCF9 !important;
        background-color: #100E12 !important;
    }
    .main-container {
        background: rgba(30, 30, 40, 0.85);
        border: 1px solid #332f3d;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
        margin-top: 20px;
    }
    .custom-title {
        color: #00f3ff;
        font-weight: 700;
        font-size: 28px;
        margin-bottom: 10px;
    }
    .custom-text {
        color: #d1d5db;
        font-size: 15px;
        line-height: 1.6;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- BAŞLIK VE KONTROL PANELİ ---
st.markdown(
    "<h1 style='text-align: center;'>🌐 Perplexity Tarayıcı & Arayüz Modülü</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #9ca3af;'>Gönderdiğiniz arayüz şablonu Python ve Streamlit altyapısına başarıyla uyarlanmıştır.</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# --- KULLANICI ETKİLEŞİM ALANI ---
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### ⚙️ Ayarlar & Tercihler")
    tema_modu = st.selectbox(
        "Renk Şeması:", ["Karanlık (Dark)", "Aydınlık (Light)"]
    )
    yazi_tipi = st.selectbox("Tipografi:", ["Serif", "Sans-Serif"])
    aktif_et = st.checkbox("Arayüz Bileşenlerini Aktifleştir", value=True)

    if st.button("Ayarları Uygula", use_container_width=True):
        st.success("Tercihleriniz başarıyla kaydedildi!")

with col2:
    st.markdown(
        """
        <div class="main-container">
            <div class="custom-title">💬 Yapay Zeka Arayüz Paneli</div>
            <p class="custom-text">
                Bu alan, gönderdiğiniz HTML/CSS yapısının Python ortamında dinamik olarak render edilmesini sağlar. 
                İstediğiniz ek özellikleri, metinleri veya bileşenleri bu yapı üzerine kolayca inşa edebilirsiniz.
            </p>
            <hr style="border-color: #332f3d;">
            <p style="font-size: 13px; color: #9ca3af;">
                🕒 Oturum Tarihi: <b>{zaman}</b> &nbsp;|&nbsp; 
                🎨 Tema: <b>{tema}</b>
            </p>
        </div>
    """.format(
            zaman=datetime.now().strftime("%d.%m.%Y %H:%M:%S"), tema=tema_modu
        ),
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# --- HTML / JAVASCRIPT GÖMME ÖRNEĞİ (Gerekirse doğrudan HTML çalıştırmak için) ---
if aktif_et:
    st.markdown("### 🧩 Canlı HTML / Bileşen Çıktısı")
    html_bileseni = """
    <div style="background-color: #18151f; border-left: 4px solid #00f3ff; padding: 15px; border-radius: 8px; color: #FCFCF9; font-family: sans-serif;">
        <h4 style="margin: 0 0 5px 0; color: #00f3ff;">Sistem Durumu: Aktif 🟢</h4>
        <p style="margin: 0; font-size: 14px; color: #d1d5db;">Gönderdiğiniz sayfa yapısı bileşeni başarıyla yüklendi ve çalışıyor.</p>
    </div>
    """
    components.html(html_bileseni, height=100)
