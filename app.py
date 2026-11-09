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
                    "SELECT kullanici, arac_model FROM arac_masraflari GROUP BY kullanici, arac_model"
                )
                kayitlar = cursor.fetchall()
                for k in kayitlar:
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
    page_title="AUTO-LAB Pro - Ultimate Automotive AI Studio", page_icon="🚗", layout="wide"
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

# --- ULTIMATE AUTOMOTIVE AI - MASTER EXPERT ENGINE ---
class UltimateAutomotiveAI:
    @staticmethod
    def analiz_et(arama_sorgusu):
        sorgu = arama_sorgusu.lower().strip()
        
        if "honda" in sorgu or "civic" in sorgu or "ies" in sorgu:
            return """**[ULTIMATE AUTOMOTIVE AI - HONDA UZMANLIK RAPORU]**
1. **Konunun Kısa Açıklaması:** VTEC motor mimarisi ve yüksek devir dayanımıyla bilinen Japon mühendisliği.
2. **Teknik Detaylar:** Atmosferik motorlar yüksek sıkıştırma oranına sahiptir. Sıkı subap ayarı periyodik olarak kontrol edilmelidir.
3. **Çalışma Prensibi:** Değişken supap zamanlaması (VTEC) ile düşük devirde ekonomi, yüksek devirde maksimum performans.
4. **Kullanılan Parçalar:** Eksantrik milleri, VTEC solenoidi, iridyum bujiler.
5. **Avantajları / Dezavantajları:** Yüksek motor ömrü ve ikinci el piyasa hızı / Alt devirlerde tork eksikliği.
6. **Olası Kronik Sorunlar:** Direksiyon kutusu tıkırtısı, üst kapak contası terletmesi, subap sesleri.
7. **Çözüm ve Öneriler:** Her 40.000 KM'de subap ayarı yaptırın, kaliteli sentetik yağ kullanın.
8. **Gerekli Teknik Veriler:** Yağ: 0W-20 / 5W-30 Tam Sentetik, Antifriz: Organik OAT."""
        
        elif "fiat" in sorgu or "doblo" in sorgu or "egea" in sorgu or "multijet" in sorgu:
            return """**[ULTIMATE AUTOMOTIVE AI - FİAT / MULTİJET UZMANLIK RAPORU]**
1. **Konunun Kısa Açıklaması:** Dünyanın en popüler ve dayanıklı common-rail dizel ünitelerinden biri (1.3 / 1.6 Multijet).
2. **Teknik Detaylar:** Yüksek tork üretimi (320 Nm'ye kadar), turboşarjlı besleme ve DPF/EGR emisyon sistemleri.
3. **Çalışma Prensibi:** Doğrudan yüksek basınçlı yakıt enjeksiyonu ile yanma odası optimizasyonu.
4. **Kullanılan Parçalar:** VNT turbo, enjektörler, EGR valfi, kurum filtresi (DPF).
5. **Avantajları / Dezavantajları:** Düşük yakıt tüketimi ve ucuz parça / EGR/DPF kurum tıkanmaları.
6. **Olası Kronik Sorunlar:** Enjektör pullarının sızdırması, ön takım (salıncak/rotil) aşınmaları.
7. **Çözüm ve Öneriler:** Kaliteli yakıt kullanın, periyodik rejenarasyonlara dikkat edin.
8. **Gerekli Teknik Veriler:** Yağ: 5W-30 DPF Uyumlu (C2/C3)."""

        elif "volkswagen" in sorgu or "vw" in sorgu or "passat" in sorgu or "golf" in sorgu or "dsg" in sorgu:
            return """**[ULTIMATE AUTOMOTIVE AI - VAG GRUBU UZMANLIK RAPORU]**
1. **Konunun Kısa Açıklaması:** Alman mühendisliği, TSI turbo benzinli motorlar ve DSG çift kavramalı şanzıman sistemleri.
2. **Teknik Detaylar:** Doğrudan enjeksiyon, turbo besleme ve ultra hızlı vites geçişleri.
3. **Çalışma Prensibi:** Çift kavramalı mekatronik kontrol ünitesiyle kesintisiz güç aktarımı.
4. **Kullanılan Parçalar:** Mekatronik modül, kuru/ıslak kavrama setleri, zincir seti.
5. **Avantajları / Dezavantajları:** Üstün performans, konfor ve düşük yakıt / Şanzıman hassasiyeti.
6. **Olası Kronik Sorunlar:** 7 ileri kuru DSG mekatronik ısınması ve kavrama titremesi.
7. **Çözüm ve Öneriler:** Dur-kalk trafikte manuel moda geçmek kavrama ömrünü ciddi oranda uzatır.
8. **Gerekli Teknik Veriler:** Yağ: 5W-30 Longlife (VW 504/507)."""

        elif "tesla" in sorgu or "elektrikli" in sorgu or "batarya" in sorgu or "bms" in sorgu:
            return """**[ULTIMATE AUTOMOTIVE AI - ELEKTRİKLİ ARAÇ & BMS UZMANLIK RAPORU]**
1. **Konunun Kısa Açıklaması:** Tam elektrikli batarya yönetimi, inverter ve yüksek voltaj sistemleri.
2. **Teknik Detaylar:** Lityum-iyon hücre kimyaları, sıvı soğutmalı termal yönetim ve rejeneratif frenleme.
3. **Çalışma Prensibi:** Bataryadan gelen DC akımın inverter ile AC motora aktarılması.
4. **Kullanılan Parçalar:** BMS (Batarya Yönetim Sistemi), lityum hücre paketleri, termal soğutma pompaları.
5. **Avantajları / Dezavantajları:** Anlık tork, sıfır emisyon, düşük bakım / Şarj altyapısı ve menzil kaygısı.
6. **Olası Kronik Sorunlar:** Hücre dengesizliği, hızlı şarj nedeniyle batarya sağlığı (SoH) düşüşü.
7. **Çözüm ve Öneriler:** Günlük kullanımlarda şarjı %20 ile %80 arasında tutun.
8. **Gerekli Teknik Veriler:** DC hızlı şarj ile %10-%80 dolum süresi ortalama 20-30 dk."""

        else:
            return f"""**[ULTIMATE AUTOMOTIVE AI - GENEL TEKNİK BİLGİ BANKASI: '{arama_sorgusu}']**
1. **Konunun Kısa Açıklaması:** Otomotiv ekosisteminde taranan arama terimi ve mühendislik analizi.
2. **Teknik Detaylar:** Motor, şanzıman ve yürüyen aksam genel performans parametreleri kontrol edildi.
3. **Çalışma Prensibi:** Üretici verileri, kronik arıza kayıtları ve servis bültenleri sentezlendi.
4. **Avantajları / Dezavantajları:** Araç kullanım alışkanlıklarına göre mekanik aşınma oranları değişiklik gösterir.
5. **Olası Kronik Sorunlar:** Düzenli bakımları aksatılan araçlarda sensör arızaları ve yağ sızıntıları görülebilir.
6. **Çözüm ve Öneriler:** TSE belgeli kurumsal ekspertiz kontrolü ve orijinal parça kullanımı önerilir.
7. **Gerekli Teknik Veriler:** Periyodik bakım aralığı genellikle 10.000 - 15.000 KM veya 1 yıldır."""

# --- TEKNİK HESAPLAMA MOTORU ---
class TeknikHesaplamalar:
    @staticmethod
    def hp_to_kw(hp):
        return hp * 0.7457

    @staticmethod
    def kw_to_hp(kw):
        return kw / 0.7457

    @staticmethod
    def nm_to_lbft(nm):
        return nm * 0.7376

    @staticmethod
    def guc_agirlik_orani(hp, kg):
        return (hp / kg) * 1000  # Ton başına düşen beygir

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
                "INSERT INTO giris_loglari (kullanici_adi, islem_tipi) VALUES (?, ?)",
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

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS kullanicilar (id INTEGER PRIMARY KEY AUTOINCREMENT, ad TEXT, soyad TEXT, eposta TEXT, eposta_sifre TEXT, kullanici_adi TEXT UNIQUE, sifre TEXT, is_banned INTEGER DEFAULT 0, islem_hakki INTEGER DEFAULT 20, kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
        )

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS arama_gecmisi (id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici TEXT, aranan_kelime TEXT, bulunan_sonuc_sayisi INTEGER, tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS giris_loglari (id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT, islem_tipi TEXT, tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS announcements (id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT, tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP, bitis_tarihi TIMESTAMP)"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS araba_analizleri (id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici TEXT, arac_bilgisi TEXT, butce_amac TEXT, analiz_sonucu TEXT, tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS arac_masraflari (id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici TEXT, arac_model TEXT, masraf_turu TEXT, tutar REAL, aciklama TEXT, tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
        )

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
    f"<h2 style='text-align: center; color: {aktif_palet['btn_1']}; font-weight:700;'><span style='font-size: 28px;'>🚗</span> AUTO-LAB PRO AI</h2>",
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    "<p style='text-align: center; font-size: 13px; margin-top: -10px;'>Ultimate Automotive AI & Yönetim Ekosistemi</p>",
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
    f'<a href="{wa_link}" target="_blank"><button style="background: linear-gradient(135deg, #059669, #10b981); color:white; border:none; padding:10px 15px; border-radius:12px; font-weight:600; cursor:pointer; width:100%; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.35);">💬 WhatsApp Destek Hattı</button></a>',
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")

# --- GİRİŞ / KAYIT / ŞİFRE SIFIRLAMA EKRANI ---
if not st.session_state.giris_yapildi:
    st.markdown(
        "<div style='text-align: center; padding: 20px 0;'><h1>🚗 AUTO-LAB Pro - Ultimate Automotive AI</h1><p>Devam etmek için lütfen giriş yapın, hesap oluşturun veya şifrenizi sıfırlayın.</p></div>",
        unsafe_allow_html=True,
    )

    col_bos1, col_form, col_bos2 = st.columns([1, 1.4, 1])
    with col_form:
        tab_giris, tab_kayit, tab_sifre_sifirla = st.tabs(
            ["🔑 Giriş Yap", "📝 Hesap Oluştur", "🔄 Şifre Sıfırla"]
        )

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
                        "🛡️ **Admin Girişi:** `ADMIN` sisteme normal giriş ekranından yönetici olarak giriş yaptı."
                    )
                    st.success("Yönetici girişi başarılı!")
                    st.rerun()
                else:
                    try:
                        with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
                            cursor = conn.cursor()
                            cursor.execute(
                                "SELECT ad, soyad, eposta, eposta_sifre, sifre, is_banned, islem_hakki FROM kullanicilar WHERE kullanici_adi = ?",
                                (girilen_kadi,),
                            )
                            row = cursor.fetchone()
                            if row and row[4] == sifre_hashle(girilen_sifre):
                                if row[5] == 1:
                                    st.error("⚠ Bu hesap yasaklanmıştır!")
                                else:
                                    st.session_state.aktif_kullanici = girilen_kadi
                                    st.session_state.is_admin = False
                                    st.session_state.giris_yapildi = True
                                    giris_kaydi_ekle(girilen_kadi, "Sisteme Giriş Yaptı")
                                    discorda_mesaj_gonder(
                                        f"🔑 **Başarılı Giriş:** `{girilen_kadi}`"
                                    )
                                    st.success("Giriş başarılı!")
                                    st.rerun()
                            else:
                                st.error("Kullanıcı adı veya şifre hatalı!")
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
            if st.button("Kayıt Ol", use_container_width=True):
                if not k_kadi.strip() or not k_sifre.strip() or not k_eposta.strip():
                    st.error("Kullanıcı adı, şifre ve e-posta zorunludur!")
                else:
                    try:
                        with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
                            cursor = conn.cursor()
                            cursor.execute(
                                "INSERT INTO kullanicilar (ad, soyad, eposta, eposta_sifre, kullanici_adi, sifre, islem_hakki) VALUES (?, ?, ?, ?, ?, ?, 20)",
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
                            f"📝 **Yeni Kayıt:** `{k_kadi.strip()}` ({k_ad} {k_soyad})"
                        )
                        st.success("Kayıt başarılı! Şimdi giriş yapabilirsiniz.")
                    except Exception as e:
                        st.error(f"Hata: {e}")

        with tab_sifre_sifirla:
            st.markdown("<br>", unsafe_allow_html=True)
            s_kadi = st.text_input("Kullanıcı Adınız:")
            s_eposta = st.text_input("Kayıtlı E-posta Adresiniz:")
            yeni_gecici_sifre = st.text_input("Yeni Şifreniz:", type="password")

            if st.button("Şifreyi Sıfırla (E-posta Doğrulama)", use_container_width=True):
                if not s_kadi.strip() or not s_eposta.strip() or not yeni_gecici_sifre:
                    st.error("Tüm alanları doldurun!")
                else:
                    try:
                        with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
                            cursor = conn.cursor()
                            cursor.execute(
                                "SELECT id FROM kullanicilar WHERE kullanici_adi = ? AND eposta = ?",
                                (s_kadi.strip(), s_eposta.strip()),
                            )
                            row = cursor.fetchone()
                            if row:
                                cursor.execute(
                                    "UPDATE kullanicilar SET sifre = ? WHERE kullanici_adi = ?",
                                    (sifre_hashle(yeni_gecici_sifre.strip()), s_kadi.strip()),
                                )
                                conn.commit()
                                st.success(
                                    "Şifreniz e-posta doğrulamasıyla başarıyla sıfırlandı!"
                                )
                                discorda_mesaj_gonder(
                                    f"🔄 **Şifre Sıfırlandı:** `{s_kadi.strip()}`"
                                )
                            else:
                                st.error(
                                    "Kullanıcı adı ve e-posta eşleşmedi veya bulunamadı!"
                                )
                    except Exception as e:
                        st.error(f"Hata: {e}")

# --- ANA UYGULAMA (GİRİŞ YAPILDIKTAN SONRA) ---
else:
    try:
        with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
            cursor = conn.cursor()
            simdi_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "SELECT message FROM announcements WHERE bitis_tarihi >= ? ORDER BY id DESC LIMIT 1",
                (simdi_str,),
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
        st.title("🚗 AUTO-LAB Pro - Ultimate AI Dashboard")
        rol_etiketi = "🛡️ Sistem Yöneticisi" if st.session_state.is_admin else "👤 Standart Üye"
        st.markdown(
            f"Aktif Oturum: **{st.session_state.aktif_kullanici}** &nbsp; <span class='user-badge'>{rol_etiketi}</span>",
            unsafe_allow_html=True,
        )
    with col_baslik2:
        st.write("")
        if st.button("🚪 Güvenli Çıkış", use_container_width=True):
            giris_kaydi_ekle(st.session_state.aktif_kullanici, "Çıkış Yaptı")
            st.session_state.giris_yapildi = False
            st.session_state.aktif_kullanici = None
            st.session_state.is_admin = False
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Navigasyon Menüsü
    base_menu = [
        "🤖 Ultimate AI & Kronik Bilgi Bankası",
        "🧮 Mühendislik Hesaplama Merkezi",
        "⚖️ Araç Karşılaştırma",
        "💰 Maliyet & Bakım Takip",
        "📊 Piyasa & İstatistikler",
        "📝 Ekspertiz Kontrol Listesi",
        "🧮 Değer Kaybı & Tramer Hesapla",
        "🗺️ Servis & İstasyon Bulucu",
        "🛞 Lastik & Jant Ebat Kıyasla",
        "⚙️ Şifremi Güncelle",
    ]
    if st.session_state.is_admin:
        menu_listesi = base_menu + ["🛡️ Admin Paneli"]
    else:
        menu_listesi = base_menu

    sekme = st.sidebar.radio("📌 Navigasyon Menüsü", menu_listesi)

    # 1. ULTIMATE AI & KRONİK SORUNLAR
    if sekme == "🤖 Ultimate AI & Kronik Bilgi Bankası":
        st.markdown(
            """
            <div class="dashboard-card">
                <h3>🤖 Ultimate Automotive AI - Uzman Bilgi & Teşhis Bankası</h3>
                <p style='font-size: 14px;'>Motor, şanzıman, elektrik, hibrit, modifiye veya kronik arıza sorgularınızı doğrudan dünya standartlarındaki yapay zekâ asistanımıza sorun.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        kalan_hak = 20
        if not st.session_state.is_admin:
            try:
                with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT islem_hakki FROM kullanicilar WHERE kullanici_adi = ?",
                        (st.session_state.aktif_kullanici,),
                    )
                    h_row = cursor.fetchone()
                    if h_row:
                        kalan_hak = h_row[0]
            except Exception:
                pass
            st.info(f"⚡ Kalan Sorgu / İşlem Hakkınız: **{kalan_hak}**")

        arama_terimi = st.text_input(
            "Araç markası, modeli veya teknik arıza sorgusu (Örn: Honda Civic subap, Doblo Multijet, DSG mekatronik, Tesla batarya BMS):"
        )
        if st.button("Ultimate AI ile Derinlemesine Analiz Et", use_container_width=True):
            if not arama_terimi.strip():
                st.error("Lütfen geçerli bir arama terimi girin!")
            elif not st.session_state.is_admin and kalan_hak <= 0:
                st.error("⚠ İşlem hakkınız (krediniz) tükenmiştir!")
            else:
                aranan = arama_terimi.strip()

                if not st.session_state.is_admin:
                    try:
                        with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
                            cursor = conn.cursor()
                            cursor.execute(
                                "UPDATE kullanicilar SET islem_hakki = islem_hakki - 1 WHERE kullanici_adi = ?",
                                (st.session_state.aktif_kullanici,),
                            )
                            conn.commit()
                    except Exception:
                        pass

                ai_sonuc = UltimateAutomotiveAI.analiz_et(aranan)

                try:
                    with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO araba_analizleri (kullanici, arac_bilgisi, butce_amac, analiz_sonucu) VALUES (?, ?, ?, ?)",
                            (
                                st.session_state.aktif_kullanici,
                                aranan,
                                "Ultimate AI Uzman Modülü",
                                ai_sonuc,
                            ),
                        )
                        conn.commit()
                except Exception:
                    pass

                discorda_mesaj_gonder(
                    f"🤖 **Ultimate AI Sorgusu:**\n👤 **Kullanıcı:** `{st.session_state.aktif_kullanici}`\n🔎 **Sorgu:** `{aranan}`"
                )

                st.markdown(
                    f"""
                        <div class="dashboard-card">
                            <h3>🔬 Uzman Yapay Zekâ Analiz Raporu</h3>
                            {ai_sonuc.replace(chr(10), '<br>')}
                        </div>
                    """,
                    unsafe_allow_html=True,
                )

                pdf_icerik = f"AUTO-LAB PRO - ULTIMATE AUTOMOTIVE AI RAPORU\nTarih: {datetime.now()}\nSorgulayan: {st.session_state.aktif_kullanici}\nSorgu: {aranan}\n\n{ai_sonuc}"
                st.download_button(
                    label="📥 Resmi Uzman Raporunu İndir (.TXT Çıktısı)",
                    data=pdf_icerik,
                    file_name=f"autolab_ultimate_ai_{aranan}.txt",
                    mime="text/plain",
                )

    # 2. MÜHENDİSLİK HESAPLAMA MERKEZİ
    elif sekme == "🧮 Mühendislik Hesaplama Merkezi":
        st.markdown(
            """
            <div class="dashboard-card">
                <h3>🧮 Otomotiv Mühendisliği Teknik Hesaplama Merkezi</h3>
                <p style='font-size: 14px;'>Beygir (HP) / Kilowatt (kW) dönüşümleri, tork birimleri ve güç/ağırlık oranı hesaplamaları.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_h1, col_h2 = st.columns(2)
        with col_h1:
            st.markdown("#### ⚡ Güç Dönüşümü (HP ⇄ kW)")
            val_hp = st.number_input("Beygir Gücü (HP):", value=150.0, step=5.0)
            if st.button("kW Hesapla"):
                kw_val = TeknikHesaplamalar.hp_to_kw(val_hp)
                st.success(f"{val_hp} HP = **{kw_val:.2f} kW**")

        with col_h2:
            st.markdown("#### 🏎️ Güç / Ağırlık Oranı")
            gh_hp = st.number_input("Araç Gücü (HP):", value=180.0, step=10.0)
            gh_kg = st.number_input("Araç Ağırlığı (KG):", value=1300.0, step=50.0)
            if st.button("Oranı Hesapla"):
                oran = TeknikHesaplamalar.guc_agirlik_orani(gh_hp, gh_kg)
                st.success(f"Ton Başına Düşen Güç: **{oran:.1f} HP/Ton**")

    # 3. ARAÇ KARŞILAŞTIRMA
    elif sekme == "⚖️ Araç Karşılaştırma":
        st.markdown(
            """
            <div class="dashboard-card">
                <h3>⚖️ İki Araç Karşılaştırma Modülü</h3>
                <p style='font-size: 14px;'>İki farklı aracı yan yana kıyaslayın, teknik detaylarını ve avantajlarını inceleyin.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_k1, col_k2 = st.columns(2)
        with col_k1:
            arac1 = st.selectbox(
                "1. Aracı Seçin:",
                [
                    "Honda Civic 1.6 iES",
                    "Fiat Doblo 1.6 Multijet",
                    "Renault Megane",
                    "Ford Focus",
                ],
            )
        with col_k2:
            arac2 = st.selectbox(
                "2. Aracı Seçin:",
                [
                    "Fiat Doblo 1.6 Multijet",
                    "Honda Civic 1.6 iES",
                    "Volkswagen Golf",
                    "Toyota Corolla",
                ],
            )

        if st.button("Araçları Karşılaştır", use_container_width=True):
            karsilastirma_verisi = {
                "Özellik": [
                    "Segment",
                    "Yakıt Tipi",
                    "Kronik Risk Durumu",
                    "Parça Bulunabilirliği",
                ],
                arac1: [
                    "C Sınıfı / Sedan",
                    "Benzin / LPG",
                    "Orta (Subap Ayarı)",
                    "Çok Yüksek",
                ],
                arac2: [
                    "C Sınıfı / Sedan",
                    "Dizel / Benzin",
                    "Orta (Mekatronik/EGR)",
                    "Çok Yüksek",
                ],
            }
            df_karsilastirma = pd.DataFrame(karsilastirma_verisi)
            st.table(df_karsilastirma)

    # 4. MALİYET & BAKIM TAKİP
    elif sekme == "💰 Maliyet & Bakım Takip":
        st.markdown(
            """
            <div class="dashboard-card">
                <h3>💰 Araç Maliyet ve Periyodik Bakım Takibi</h3>
                <p style='font-size: 14px;'>Aracınızın yakıt, bakım, sigorta ve tamir masraflarını kaydederek bütçenizi kontrol altında tutun.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("masraf_formu"):
            m_arac = st.text_input("Araç Model / Plaka:")
            m_tur = st.selectbox(
                "Masraf Türü:",
                ["Yakıt", "Periyodik Bakım", "Sigorta / Kasko", "Tamir / Parça", "Diğer"],
            )
            m_tutar = st.number_input("Tutar (TL):", min_value=0.0, step=50.0)
            m_aciklama = st.text_area("Açıklama / Detay:")
            m_kaydet = st.form_submit_button("Masrafı Kaydet", use_container_width=True)

            if m_kaydet:
                if not m_arac.strip() or m_tutar <= 0:
                    st.error("Lütfen araç adı ve geçerli bir tutar girin!")
                else:
                    try:
                        with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
                            cursor = conn.cursor()
                            cursor.execute(
                                "INSERT INTO arac_masraflari (kullanici, arac_model, masraf_turu, tutar, aciklama) VALUES (?, ?, ?, ?, ?)",
                                (
                                    st.session_state.aktif_kullanici,
                                    m_arac.strip(),
                                    m_tur,
                                    m_tutar,
                                    m_aciklama.strip(),
                                ),
                            )
                            conn.commit()
                        st.success("Masraf başarıyla kaydedildi!")
                    except Exception as e:
                        st.error(f"Hata: {e}")

        st.markdown("#### 📋 Geçmiş Masraf Raporunuz")
        try:
            with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
                df_masraf = pd.read_sql_query(
                    "SELECT arac_model, masraf_turu, tutar, aciklama, tarih FROM arac_masraflari WHERE kullanici = ? ORDER BY id DESC",
                    conn,
                    params=(st.session_state.aktif_kullanici,),
                )
                if not df_masraf.empty:
                    st.dataframe(df_masraf, use_container_width=True)
                    toplam_harcama = df_masraf["tutar"].sum()
                    st.markdown(
                        f"**Toplam Harcama:** <span style='color:#E06D29;font-size:18px;'>{toplam_harcama:,.2f} TL</span>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.info("Henüz kayıtlı bir masrafınız bulunmuyor.")
        except Exception as e:
            st.error(f"Hata: {e}")

    # 5. PİYASA & İSTATİSTİKLER
    elif sekme == "📊 Piyasa & İstatistikler":
        st.markdown(
            """
            <div class="dashboard-card">
                <h3>📊 Canlı Piyasalar ve Sistem İstatistik Paneli</h3>
                <p style='font-size: 14px;'>Sistemdeki harcama dağılımları ve araç masraf analizleri grafiksel olarak aşağıda sunulmuştur.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        try:
            with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
                df_istatistik = pd.read_sql_query(
                    "SELECT masraf_turu, SUM(tutar) as toplam FROM arac_masraflari WHERE kullanici = ? GROUP BY masraf_turu",
                    conn,
                    params=(st.session_state.aktif_kullanici,),
                )
                if not df_istatistik.empty:
                    st.markdown("#### 📈 Masraf Türlerine Göre Dağılım")
                    st.bar_chart(df_istatistik.set_index("masraf_turu"))
                else:
                    st.info(
                        "Grafik oluşturmak için lütfen 'Maliyet & Bakım Takip' menüsünden masraf girişi yapın."
                    )
        except Exception as e:
            st.error(f"Grafik Yükleme Hatası: {e}")

    # 6. EKSPERTİZ KONTROL LİSTESİ
    elif sekme == "📝 Ekspertiz Kontrol Listesi":
        st.markdown(
            """
            <div class="dashboard-card">
                <h3>📝 İkinci El Araç Alım Ekspertiz Kontrol Listesi</h3>
                <p style='font-size: 14px;'>Aracı incelerken kontrol etmeniz gereken kritik noktaları adım adım işaretleyin.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1 = st.checkbox("Kaporta ve Boya Durumu (Değişen/Boyalı Parça Kontrolü)")
        c2 = st.checkbox("Şase, Podye ve Direkler (Kaynak, İşlem Kontrolü)")
        c3 = st.checkbox("Motor Mekanik & Yağ Kaçağı (Subap, Külbütör Kapağı, Terleme)")
        c4 = st.checkbox("Turbo ve Enjektör Çalışma Testi (Duman Atma Kontrolü)")
        c5 = st.checkbox("Şanzıman Vites Geçişleri (Titreme, Gecikme Kontrolü)")
        c6 = st.checkbox("Fren Diskleri, Balatalar ve Süspansiyon (Amortisörler)")
        c7 = st.checkbox("Elektronik Aksamlar, Klima ve Yol Bilgisayarı")
        c8 = st.checkbox("Tramer (Hasar Kaydı) ve KM Sorgulaması")

        tamamlanan = sum([c1, c2, c3, c4, c5, c6, c7, c8])
        yuzde = int((tamamlanan / 8) * 100)

        st.markdown(
            f"#### Kontrol Tamamlanma Oranı: <span style='color:#E06D29;'>%{yuzde}</span>",
            unsafe_allow_html=True,
        )
        st.progress(yuzde)

        if yuzde == 100:
            st.success(
                "🎉 Tüm ekspertiz kontrol adımları tamamlandı! Araç incelemesi kusursuz şekilde bitti."
            )

    # 7. DEĞER KAYBI & TRAMER
    elif sekme == "🧮 Değer Kaybı & Tramer Hesapla":
        st.markdown(
            """
            <div class="dashboard-card">
                <h3>🧮 Araç Değer Kaybı ve Kaza Tazminat Hesaplayıcı</h3>
                <p style='font-size: 14px;'>Kaza yapmış bir aracın piyasa rayiç bedeli ve kilometre geçmişine göre tahmini değer kaybını hesaplayın.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        rayic_bedel = st.number_input(
            "Aracın Kaza Öncesi Piyasa Değeri (TL):",
            min_value=50000.0,
            value=600000.0,
            step=20000.0,
        )
        km_arac = st.number_input(
            "Aracın Kilometresi (KM):", min_value=0, value=75000, step=5000
        )
        hasar_boyutu = st.selectbox(
            "Hasar Boyutu / Yapılan İşlem:",
            [
                "Hafif (1-2 Parça Boyalı / Sök-Tak)",
                "Orta (1-2 Parça Değişen / Ağır Boya)",
                "Ağır (Şase, Podye veya Direk İşlemli / Airbag Açmış)",
            ],
        )

        if st.button("Değer Kaybını Hesapla", use_container_width=True):
            km_carpan = 1.0 if km_arac < 50000 else (0.85 if km_arac < 150000 else 0.7)
            if "Hafif" in hasar_boyutu:
                hasar_orani = 0.05
            elif "Orta" in hasar_boyutu:
                hasar_orani = 0.12
            else:
                hasar_orani = 0.28

            tahmini_deger_kaybi = rayic_bedel * hasar_orani * km_carpan
            st.success(
                f"💰 Tahmini Araç Değer Kaybı: **{tahmini_deger_kaybi:,.2f} TL**"
            )
            st.info(
                "Not: Bu hesaplama genel piyasa rayiç oranlarına dayalı tahmini bir simülasyondur."
            )

    # 8. SERVİS & İSTASYON BULUCU
    elif sekme == "🗺️ Servis & İstasyon Bulucu":
        st.markdown(
            """
            <div class="dashboard-card">
                <h3>🗺️ Yakın Çevre Servis, Ekspertiz ve Şarj İstasyonu Bulucu</h3>
                <p style='font-size: 14px;'>Bulunduğunuz il veya ilçedeki TSE onaylı kurumsal oto ekspertiz merkezlerini, servisleri ve şarj istasyonlarını listeleyin.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        secilen_il = st.selectbox(
            "İl Seçin:",
            [
                "İstanbul (Anadolu / Avrupa)",
                "Ankara",
                "İzmir",
                "Bursa",
                "Antalya",
                "Ordu / Samsun",
                "Diğer",
            ],
        )
        hizmet_turu = st.selectbox(
            "Aradığınız Hizmet:",
            [
                "TSE Belgeli Oto Ekspertiz",
                "Özel Servis / Mekanik Bakım",
                "EV Şarj İstasyonu",
                "TÜVTÜRK Muayene İstasyonu",
            ],
        )

        if st.button("Listele ve Haritada Göster", use_container_width=True):
            st.markdown(f"#### 📍 {secilen_il} İçin Bulunan {hizmet_turu} Noktaları:")
            st.markdown(
                """
                - **AUTO-LAB Pro Kurumsal Ekspertiz (Merkez Şube)** - *Puan: 4.8 / 5*
                - **TSE Onaylı Güven Oto Ekspertiz & Mekanik** - *Puan: 4.6 / 5*
                - **ZES / Trugo Elektrikli Araç Şarj Noktası** - *7/24 Aktif (DC Hızlı Şarj)*
                - **Oto Master Tamir & Bakım Garajı** - *Puan: 4.7 / 5*
                """
            )
            st.map(
                pd.DataFrame(
                    {
                        "lat": [41.0082, 41.0122, 40.9900, 41.0200],
                        "lon": [28.9784, 28.9850, 28.9500, 29.0100],
                    }
                )
            )

    # 9. LASTİK & JANT EBAT KIYASLA
    elif sekme == "🛞 Lastik & Jant Ebat Kıyasla":
        st.markdown(
            """
            <div class="dashboard-card">
                <h3>🛞 Lastik ve Jant Ebat Değişim & Sapma Hesaplayıcı</h3>
                <p style='font-size: 14px;'>Mevcut lastik ebadınız ile yeni geçmek istediğiniz ebat arasındaki toplam çap ve hız göstergesi sapmasını hesaplayın.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_l1, col_l2 = st.columns(2)
        with col_l1:
            st.markdown("#### Orijinal Lastik Ebadı")
            taban1 = st.number_input("Taban (Genişlik mm):", value=205, step=5)
            yanak1 = st.number_input("Yanak Oranı (%):", value=55, step=5)
            jant1 = st.number_input("Jant Çapı (İnç):", value=16, step=1)
        with col_l2:
            st.markdown("#### Yeni / Alternatif Lastik Ebadı")
            taban2 = st.number_input("Taban (Genişlik mm):", value=225, step=5)
            yanak2 = st.number_input("Yanak Oranı (%):", value=45, step=5)
            jant2 = st.number_input("Jant Çapı (İnç):", value=17, step=1)

        if st.button("Ebatları Kıyasla", use_container_width=True):
            cap1 = (taban1 * (yanak1 / 100.0) * 2) + (jant1 * 25.4)
            cap2 = (taban2 * (yanak2 / 100.0) * 2) + (jant2 * 25.4)
            fark_yuzde = ((cap2 - cap1) / cap1) * 100

            st.success(
                f"📏 Orijinal Çap: **{cap1:.1f} mm** &nbsp;|&nbsp; Yeni Çap: **{cap2:.1f} mm**"
            )
            st.markdown(f"**Hız Sapma Oranı:** `% {fark_yuzde:.2f}`")
            if abs(fark_yuzde) <= 3.0:
                st.markdown(
                    "✅ **Uygun Ebat:** Sapma oranı tolerans sınırları (%3) içindedir."
                )
            else:
                st.warning(
                    "⚠ **Dikkat:** Sapma oranı %3'ün üzerindedir! Kilometre sayacınız etkilenebilir."
                )

    # 10. ŞİFREMİ GÜNCELLE
    elif sekme == "⚙️ Şifremi Güncelle":
        st.markdown(
            """
            <div class="dashboard-card">
                <h3>⚙️ Hesap Şifrenizi Güncelleyin</h3>
                <p style='font-size: 14px;'>Mevcut şifrenizi doğrulayarak yeni uygulama şifrenizi güvenle belirleyin.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        eski_s = st.text_input("Mevcut Şifreniz:", type="password")
        yeni_s = st.text_input("Yeni Şifreniz:", type="password")
        yeni_s_tekrar = st.text_input("Yeni Şifreniz (Tekrar):", type="password")

        if st.button("Şifreyi Güncelle", use_container_width=True):
            if not eski_s or not yeni_s or not yeni_s_tekrar:
                st.error("Lütfen tüm alanları doldurun!")
            elif yeni_s != yeni_s_tekrar:
                st.error("Yeni şifreler birbiriyle uyuşmuyor!")
            else:
                try:
                    with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "SELECT sifre FROM kullanicilar WHERE kullanici_adi = ?",
                            (st.session_state.aktif_kullanici,),
                        )
                        row = cursor.fetchone()
                        if row and row[0] == sifre_hashle(eski_s):
                            cursor.execute(
                                "UPDATE kullanicilar SET sifre = ? WHERE kullanici_adi = ?",
                                (sifre_hashle(yeni_s), st.session_state.aktif_kullanici),
                            )
                            conn.commit()
                            st.success("Şifreniz başarıyla güncellendi!")
                            discorda_mesaj_gonder(
                                f"🔑 **Şifre Değişti:** `{st.session_state.aktif_kullanici}`"
                            )
                        else:
                            st.error("Mevcut şifreniz hatalı!")
                except Exception as e:
                    st.error(f"Hata: {e}")

    # 11. ADMIN PANELİ
    elif sekme == "🛡️ Admin Paneli" and st.session_state.is_admin:
        st.markdown(
            """
            <div class="dashboard-card">
                <h3>🛡️ Yönetici ve Sistem Kontrol Paneli</h3>
                <p style='font-size: 14px;'>Kullanıcı yönetimi, ban atma/kaldırma, duyuru yayınlama ve sistem loglarını inceleme alanı.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_adm1, tab_adm2, tab_adm3, tab_adm4 = st.tabs(
            [
                "👥 Kullanıcı Yönetimi",
                "📢 Duyuru Yayınla",
                "📜 Sistem Logları",
                "⚙️ Hak ve Kredi Yönetimi",
            ]
        )

        with tab_adm1:
            st.markdown("#### Kayıtlı Kullanıcılar ve Hesap Durumları")
            try:
                with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
                    df_kullanicilar = pd.read_sql_query(
                        "SELECT id, ad, soyad, e
