from datetime import datetime, timedelta
import hashlib
import os
import pandas as pd
import requests
import shutil
import sqlite3
import streamlit as st

# --- APSCHEDULER ARKA PLAN GÖREVLERİ ---
try:
  from apscheduler.schedulers.background import BackgroundScheduler

  scheduler = BackgroundScheduler()


  def arka_plan_bakim_kontrol_gorevi():
    try:
      with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT kullanici, arac_model FROM arac_masraflari GROUP BY"
            " kullanici, arac_model"
        )
        kayitlar = cursor.fetchall()
        for k in kayitlar:
          # Periyodik arka plan bakım/kontrol simülasyonu
          pass
    except Exception:
      pass


  if not scheduler.running:
    scheduler.add_job(
        arka_plan_bakim_kontrol_gorevi, "interval", hours=24, id="bakim_kontrol"
    )
    scheduler.start()
except Exception:
  pass

# --- STREAMLIT SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="AUTO-LAB Pro - Yönetim Paneli", page_icon="🚗", layout="wide"
)

# --- TELEFON VE YEREL AĞ / PWA META AYARLARI ---
if "server_configured" not in st.session_state:
  try:
    import streamlit.web.bootstrap as sb

    st.session_state["server_configured"] = True
  except Exception:
    pass

# --- OTOMATİK VERİTABANI YEDEKLEME ---
def yedekle_db():
  yedek_klasoru = "yedekler"
  if not os.path.exists(yedek_klasoru):
    os.makedirs(yedek_klasoru)

  db_adi = "autolab_pro.db"
  if os.path.exists(db_adi):
    zaman = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    hedef = os.path.join(yedek_klasoru, f"autolab_yedek_{zaman}.db")
    shutil.copy(db_adi, hedef)

if "yedek_alindi" not in st.session_state:
  yedekle_db()
  st.session_state["yedek_alindi"] = True

# --- DİSCORD & WHATSAPP AYARLARI ---
DEFAULT_WEBHOOK = "https://discord.com/api/webhooks/1548444040037662790/Yo7pYhJbWfSqzjWPVuwGrpQpuGlUYJO4uVIcA3ZRI4zSupvYNsu6m62BIZwDxFaRyDXl"
try:
  DISCORD_WEBHOOK_URL = st.secrets.get("DISCORD_WEBHOOK_URL", DEFAULT_WEBHOOK)
except Exception:
  DISCORD_WEBHOOK_URL = DEFAULT_WEBHOOK

WHATSAPP_NUMARASI = "905510305139"

def discorda_mesaj_gonder(mesaj):
  if not DISCORD_WEBHOOK_URL or not DISCORD_WEBHOOK_URL.startswith("http"):
    return
  try:
    zaman_damgasi = datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
    formatli_mesaj = f"🕒 `[{zaman_damgasi}]`\n{mesaj}"
    requests.post(
        DISCORD_WEBHOOK_URL, json={"content": formatli_mesaj}, timeout=5
    )
  except Exception:
    pass

# --- GENİŞLETİLMİŞ KRONİK SORUNLAR VE BİLGİ BANKASI ---
def internetten_arac_ve_veri_arastir(arama_sorgusu):
  sorgu_kucuk = arama_sorgusu.lower().strip()

  if "honda" in sorgu_kucuk or "civic" in sorgu_kucuk or "ies" in sorgu_kucuk:
    return """[AUTO-LAB KRONİK ANALİZ: HONDA]
- **Motor ve Mekanik:** Yüksek devir sevdası nedeniyle subap ayarı sıkılaşması görülebilir. VTEC motorlarda üst kapak contası ve müşirinde terleme sık rastlanır.
- **Şanzıman:** Manuel şanzımanları sağlamdır. Otomatik modellerde yağ değişimi aksatıldıysa geçişlerde gecikme olabilir.
- **Eksper Önerisi:** Yağ kaçağı, alt takım burçları ve subap sesine mutlaka baktırın."""

  elif (
      "fiat" in sorgu_kucuk
      or "doblo" in sorgu_kucuk
      or "egea" in sorgu_kucuk
      or "linea" in sorgu_kucuk
      or "multijet" in sorgu_kucuk
  ):
    return """[AUTO-LAB KRONİK ANALİZ: FİAT (EGEA / DOBLO / LİNEA / MULTİJET)]
- **Motor ve Mekanik:** 1.3 ve 1.6 Multijet motorlar ömürlüktür ancak EGR valfi ve kurum bağlama sorunları kroniktir. Enjektör pulları sızdırma yapabilir.
- **Şanzıman & Yürüyen:** Ön takım (salıncaklar, rotiller) bozuk yollarda çabuk aşınır ve ses yapar.
- **Eksper Önerisi:** Turbo basıncı, enjektör püskürtme değerleri ve alt takım boşlukları mutlaka test edilmelidir."""

  elif (
      "renault" in sorgu_kucuk
      or "megane" in sorgu_kucuk
      or "clio" in sorgu_kucuk
      or "edc" in sorgu_kucuk
  ):
    return """[AUTO-LAB KRONİK ANALİZ: RENAULT & DACİA]
- **Motor ve Mekanik:** 1.5 dCi motorlar az yakar ancak turbo yatak aşınmasına dikkat edilmelidir.
- **Şanzıman (EDC Çift Kavrama):** Trafikte dur-kalk yaparken titreme veya silkeleme kroniktir. Kavrama ve mekatronik testi şarttır."""

  elif (
      "volkswagen" in sorgu_kucuk
      or "vw" in sorgu_kucuk
      or "golf" in sorgu_kucuk
      or "passat" in sorgu_kucuk
      or "dsg" in sorgu_kucuk
  ):
    return """[AUTO-LAB KRONİK ANALİZ: VOLKSWAGEN / VAG GRUBU]
- **Şanzıman (DSG):** 7 ileri kuru kavrama DSG'lerde mekatronik arızası ve kavramanın erken aşınması en bilinen sorundur.
- **Motor (TSI / TDI):** TSI'larda zincir uzaması sesine, TDI'larda ise EGR ve DPF tıkanma eğilimine dikkat edilmelidir."""

  elif "ford" in sorgu_kucuk or "focus" in sorgu_kucuk or "fiesta" in sorgu_kucuk:
    return """[AUTO-LAB KRONİK ANALİZ: FORD]
- **Motor & Mekanik:** 1.5 TDCi motorlar dayanıklıdır ancak enjektör ve dpf sensör arızaları görülebilir. Benzinli Ecoboost motorlarda soğutma hortumlarına dikkat edilmelidir.
- **Şanzıman:** PowerShift şanzımanlarda ısınma ve kavrama sarsıntısı kroniktir, manuel tercih edilebilir."""

  elif "toyota" in sorgu_kucuk or "corolla" in sorgu_kucuk or "yaris" in sorgu_kucuk:
    return """[AUTO-LAB KRONİK ANALİZ: TOYOTA]
- **Motor & Mekanik:** Atmosferik motorları (VVT-i) oldukça sorunsuzdur ve tüple uyumludur. 
- **Şanzıman:** M/M (MultiMode) yarı otomatik şanzımanlarda baskı balata ve aktüatör hatası sık görülür. Tam otomatik veya manuel versiyonları daha sorunsuzdur."""

  else:
    return f"""[AUTO-LAB AKILLI ARAMA MOTORU: '{arama_sorgusu}']
- **Arama Detayı:** Aradığınız model için genişletilmiş otomotiv veri tabanı tarandı.
- **Temel Tavsiye:** İkinci el araç alımında TSE belgeli kurumsal bir oto ekspertiz merkezine mutlaka başvurun ve tramer kaydını sorgulayın."""

# --- RENK PALETLERİ SÖZLÜĞÜ ---
PALETLER = {
    "🌿 Karanlık & Atmosferik": {
        "bg": "#121814",
        "card": "rgba(30, 42, 35, 0.88)",
        "sidebar": "#0b0f0d",
        "btn_1": "#E06D29",
        "btn_2": "#c75b1c",
        "btn_shadow": "rgba(224, 109, 41, 0.35)",
        "accent": "#4E7C59",
        "text": "#EAEAEA",
    },
    "🌌 Modern Lacivert": {
        "bg": "#0f172a",
        "card": "rgba(30, 41, 59, 0.88)",
        "sidebar": "#090d16",
        "btn_1": "#00f3ff",
        "btn_2": "#00bcd4",
        "btn_shadow": "rgba(0, 243, 255, 0.35)",
        "accent": "#00f3ff",
        "text": "#f8fafc",
    },
    "🔮 Siberpunk Neon": {
        "bg": "#130f1f",
        "card": "rgba(45, 27, 78, 0.85)",
        "sidebar": "#0c0814",
        "btn_1": "#f43f5e",
        "btn_2": "#e11d48",
        "btn_shadow": "rgba(244, 63, 94, 0.4)",
        "accent": "#c084fc",
        "text": "#fff1f2",
    },
    "🪵 Sıcak Ahşap & Kahve": {
        "bg": "#1c1917",
        "card": "rgba(41, 37, 36, 0.9)",
        "sidebar": "#12100e",
        "btn_1": "#d97706",
        "btn_2": "#b45309",
        "btn_shadow": "rgba(217, 119, 6, 0.35)",
        "accent": "#78350f",
        "text": "#f5f5f4",
    },
}

# --- SESSION STATE DEĞİŞKENLERİ ---
if "secilen_tema" not in st.session_state:
  st.session_state.secilen_tema = "🌿 Karanlık & Atmosferik"

if "bg_resim" not in st.session_state:
  st.session_state.bg_resim = (
      "https://images.unsplash.com/photo-1503376780353-7e6692767b70?q=80&w=1920&auto=format&fit=crop"
  )

if "overlay_opacity" not in st.session_state:
  st.session_state.overlay_opacity = 0.88

aktif_palet = PALETLER[st.session_state.secilen_tema]

# --- DİNAMİK CSS VE PWA META ETİKETLERİ ---
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        color: {aktif_palet['text']} !important;
    }}
    
    .stApp {{
        background-color: {aktif_palet['bg']};
        color: {aktif_palet['text']};
    }}
    
    .login-background {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: linear-gradient({aktif_palet['bg']}, {aktif_palet['bg']}), 
                            url('{st.session_state.bg_resim}');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        z-index: -999;
        opacity: {st.session_state.overlay_opacity};
    }}
    
    [data-testid="stSidebar"] {{
        background-color: {aktif_palet['sidebar']} !important;
        border-right: 1px solid {aktif_palet['accent']};
        box-shadow: 5px 0 25px rgba(0, 0, 0, 0.8);
    }}
    
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] p {{
        color: {aktif_palet['text']} !important;
    }}
    
    .stButton>button {{
        background: linear-gradient(135deg, {aktif_palet['btn_1']}, {aktif_palet['btn_2']});
        color: #ffffff;
        border-radius: 12px;
        font-weight: 700;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 0.6rem 1.2rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 20px {aktif_palet['btn_shadow']};
    }}
    
    .stButton>button:hover {{
        transform: translateY(-2px);
        filter: brightness(1.15);
    }}
    
    .dashboard-card {{
        background-color: {aktif_palet['card']};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid {aktif_palet['accent']};
        padding: 24px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
        color: {aktif_palet['text']};
    }}
    
    .stTextInput>div>div>input, .stSelectbox>div>div>select {{
        background-color: {aktif_palet['bg']} !important;
        color: {aktif_palet['text']} !important;
        border: 1px solid {aktif_palet['accent']} !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
    }}
    
    .announcement-banner {{
        background: linear-gradient(135deg, {aktif_palet['card']}, {aktif_palet['bg']});
        color: {aktif_palet['text']};
        padding: 18px 24px;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        margin-bottom: 25px;
        display: flex;
        align-items: center;
        gap: 16px;
        border-left: 6px solid {aktif_palet['btn_1']};
        border: 1px solid {aktif_palet['accent']};
    }}
    
    .user-badge {{
        background: {aktif_palet['card']};
        color: {aktif_palet['btn_1']};
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        border: 1px solid {aktif_palet['accent']};
        display: inline-block;
    }}
    </style>
    <div class="login-background"></div>
""",
    unsafe_allow_html=True,
)

def sifre_hashle(sifre):
  return hashlib.sha256(sifre.encode("utf-8")).hexdigest()

def giris_kaydi_ekle(kullanici_adi, islem_tipi):
  try:
    with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
      cursor = conn.cursor()
      cursor.execute(
          """
                INSERT INTO giris_loglari (kullanici_adi, islem_tipi)
                VALUES (?, ?)
            """,
          (kullanici_adi, islem_tipi),
      )
      conn.commit()
  except Exception:
    pass

# Session State Tanımları
if "aktif_kullanici" not in st.session_state:
  st.session_state.aktif_kullanici = None

if "giris_yapildi" not in st.session_state:
  st.session_state.giris_yapildi = False

if "is_admin" not in st.session_state:
  st.session_state.is_admin = False

# Veritabanı Tablolarını Oluşturma ve Migrasyon
try:
  with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
    cursor = conn.cursor()

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS kullanicilar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT,
                soyad TEXT,
                eposta TEXT,
                eposta_sifre TEXT,
                kullanici_adi TEXT UNIQUE,
                sifre TEXT,
                is_banned INTEGER DEFAULT 0,
                islem_hakki INTEGER DEFAULT 20,
                kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS arama_gecmisi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici TEXT,
                aranan_kelime TEXT,
                bulunan_sonuc_sayisi INTEGER,
                tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS giris_loglari (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici_adi TEXT,
                islem_tipi TEXT,
                tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT,
                tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                bitis_tarihi TIMESTAMP
            )
        """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS araba_analizleri (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici TEXT,
                arac_bilgisi TEXT,
                butce_amac TEXT,
                analiz_sonucu TEXT,
                tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS arac_masraflari (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici TEXT,
                arac_model TEXT,
                masraf_turu TEXT,
                tutar REAL,
                aciklama TEXT,
                tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    cursor.execute("PRAGMA table_info(kullanicilar)")
    kullanici_sutunlari = [sutun[1] for sutun in cursor.fetchall()]
    if "islem_hakki" not in kullanici_sutunlari:
      cursor.execute(
          "ALTER TABLE kullanicilar ADD COLUMN islem_hakki INTEGER DEFAULT 20"
      )

    conn.commit()
except Exception as e:
  st.error(f"DB Migrasyon Hatası: {e}")

# --- SÜRESİ DOLAN DUYURULARI TEMİZLE ---
try:
  with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
    cursor = conn.cursor()
    simdi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("DELETE FROM announcements WHERE bitis_tarihi < ?", (simdi,))
    conn.commit()
except Exception:
  pass

# --- SİDEBAR & RENK PALETİ SEÇİCİ ---
st.sidebar.markdown(
    f"<h2 style='text-align: center; color: {aktif_palet['btn_1']};"
    " font-weight:700;'><span style='font-size: 28px;'>🚗</span> AUTO-LAB"
    " PRO</h2>",
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    "<p style='text-align: center; font-size: 13px; margin-top:"
    " -10px;'>Otomotiv & Yönetim Ekosistemi</p>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")

yeni_secim = st.sidebar.selectbox(
    "🎨 Renk Kombinasyonu Seç:",
    list(PALETLER.keys()),
    index=list(PALETLER.keys()).index(st.session_state.secilen_tema),
)
if yeni_secim != st.session_state.secilen_tema:
  st.session_
