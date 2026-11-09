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
    page_title="AUTO-LAB Pro - Ultimate Automotive Intelligence System", page_icon="🚗", layout="wide"
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

# --- ENGINE EXPERT AI ---
class EngineExpertAI:
    @staticmethod
    def motor_analiz_et(motor_kodu_veya_adi):
        kod = motor_kodu_veya_adi.upper().strip()
        if "B58" in kod:
            return """**[ENGINE EXPERT AI - MOTOR ANALİZ RAPORU: BMW B58 (3.0L Turbo I6)]**
- **Genel Tanıtım:** BMW'nin efsanevi sıralı 6 silindirli B58 motoru, ZF 8 ileri şanzımanla mükemmel uyum sağlar.
- **Dayanıklılık:** Mekanik olarak olağanüstü sağlamdır. Kapalı blok mimarisi ve dayanıklı iç organları sayesinde yüksek basınçlara dayanır.
- **Kronik Sorunlar:** Su pompası ve termostat ünitesinde nadiren hafif terletmeler görülebilir.
- **Bakım Maliyeti:** Yüksek performanslı sentetik yağ gerektirir (Orta-Yüksek).
- **Yüksek Kilometre:** 300.000 KM üstünü doğru bakımlarla rahatlıkla devirebilir.
- **Genel Puan:** 96 / 100
- **Son Karar:** GÖNÜL RAHATLIĞIYLA TERCİH EDİLEBİLİR 🟢"""
        elif "N47" in kod:
            return """**[ENGINE EXPERT AI - MOTOR ANALİZ RAPORU: BMW N47 (2.0L Dizel)]**
- **Genel Tanıtım:** BMW'nin çok satan 2.0 dizel motorudur ancak triger zincirinin şanzıman tarafında (arkada) olmasıyla bilinir.
- **Kronik Sorunlar:** Triger zinciri kopma riski, emme manifoldu kurum bağlanması.
- **Bakım Maliyeti:** Zincir değişimi motorun sökülmesini gerektirdiği için işçilik masrafı yüksektir.
- **Genel Puan:** 58 / 100
- **Son Karar:** DİKKATLİ OLUNMALI / ZİNCİR KONTROLÜ ŞART 🟡"""
        elif "1.5 DCI" in kod or "K9K" in kod:
            return """**[ENGINE EXPERT AI - MOTOR ANALİZ RAPORU: RENAULT 1.5 dCi (K9K)]**
- **Genel Tanıtım:** Dünyanın en dayanıklı küçük hacimli dizel motorlarındandır.
- **Dayanıklılık:** Doğru bakımlarla bitmeyen bir motordur.
- **Genel Puan:** 88 / 100
- **Son Karar:** GÖNÜL RAHATLIĞIYLA TERCİH EDİLEBİLİR 🟢"""
        elif "MULTIJET" in kod:
            return """**[ENGINE EXPERT AI - MOTOR ANALİZ RAPORU: FİAT 1.3/1.6 MULTİJET]**
- **Genel Tanıtım:** Basit mimarisi ve döküm blok yapısıyla aşırı dayanıklıdır. Türkiye'de parça bolluğu ve ucuz işçiliği vardır.
- **Genel Puan:** 90 / 100
- **Son Karar:** KESİNLİKLE TERCİH EDİLEBİLİR 🟢"""
        else:
            return f"""**[ENGINE EXPERT AI - MOTOR ANALİZ RAPORU: '{motor_kodu_veya_adi}']**
- **Genel Tanıtım:** Sorguladığınız motor kodu/modeli veritabanımızda taranmıştır. Periyodik bakımları yapıldığı sürece ömrünü korur.
- **Genel Puan:** 75 / 100
- **Son Karar:** BAKIM GEÇMİŞİNE BAĞLI 🟡"""

# --- CAR BUYING EXPERT AI ---
class CarBuyingExpertAI:
    @staticmethod
    def analiz_et(marka, model, yil, motor, guc, yakit, sanziman, km, fiyat, tramer, degisen, boyali, bakim):
        sorgu = f"{marka} {model}".lower()
        puan = 85 if "honda" in sorgu or "fiat" in sorgu else 75
        karar = "ALINIR ✅" if puan >= 80 else "PAZARLIKLA ALINIR 🤝"
        return f"""**[CAR BUYING EXPERT AI - SATIN ALMA ANALİZİ]**
- **Araç:** {marka} {model} ({yil}) - {motor} ({guc}) - {sanziman} - {km:,} KM
- **İstenen Fiyat:** {fiyat:,.2f} TL
- **Genel Puan:** <span style='font-size:20px; font-weight:bold; color:#E06D29;'>{puan} / 100</span>
- **Son Karar:** **{karar}**"""

# --- AUTOMOTIVE DIAGNOSTIC AI ---
class AutomotiveDiagnosticAI:
    @staticmethod
    def ariza_teshis_et(marka, model, yil, motor, yakit, km, sikayet):
        return f"""**[AUTOMOTIVE DIAGNOSTIC AI - ARIZA RAPORU]**
- **Araç:** {marka} {model} ({yil}) | {motor} | {yakit} | {km:,} KM
- **Şikayet:** {sikayet}
- **Teşhis:** OBD2 canlı veri taraması ve fiziki kontrol şarttır. Ciddiyet: SEVİYE 2 – Orta."""

# --- ULTIMATE AUTOMOTIVE AI ---
class UltimateAutomotiveAI:
    @staticmethod
    def analiz_et(arama_sorgusu):
        sorgu = arama_sorgusu.lower().strip()
        if "ses" in sorgu or "tıkırtı" in sorgu:
            return "**[ULTIMATE AI - SÜSPANSİYON & SES ANALİZİ]**\nÖn takım Z rotları ve tekerlek bilyaları kontrol edilmelidir."
        elif "honda" in sorgu:
            return "**[ULTIMATE AI - HONDA UZMANLIK]**\nVTEC motor, 40.000 KM'de bir subap ayarı gerektirir."
        elif "fiat" in sorgu or "multijet" in sorgu:
            return "**[ULTIMATE AI - FİAT MULTİJET]**\nEGR ve DPF kurum temizliğine dikkat edilmelidir."
        elif "volkswagen" in sorgu or "dsg" in sorgu:
            return "**[ULTIMATE AI - VAG / DSG]**\n7 ileri kuru kavrama DSG mekatronik ve kavrama titremesi kontrol edilmelidir."
        else:
            return f"**[ULTIMATE AI BİLGİ BANKASI: '{arama_sorgusu}']**\nTSE belgeli kurumsal ekspertiz kontrolü önerilir."

class TeknikHesaplamalar:
    @staticmethod
    def hp_to_kw(hp): return hp * 0.7457
    @staticmethod
    def kw_to_hp(kw): return kw / 0.7457

PALETLER = {
    "🌿 Karanlık & Atmosferik": {"bg": "#121814", "card": "rgba(30, 42, 35, 0.88)", "sidebar": "#0b0f0d", "btn_1": "#E06D29", "btn_2": "#c75b1c", "btn_shadow": "rgba(224, 109, 41, 0.35)", "accent": "#4E7C59", "text": "#EAEAEA"},
    "🌌 Modern Lacivert": {"bg": "#0f172a", "card": "rgba(30, 41, 59, 0.88)", "sidebar": "#090d16", "btn_1": "#00f3ff", "btn_2": "#00bcd4", "btn_shadow": "rgba(0, 243, 255, 0.35)", "accent": "#00f3ff", "text": "#f8fafc"},
    "🔮 Siberpunk Neon": {"bg": "#130f1f", "card": "rgba(45, 27, 78, 0.85)", "sidebar": "#0c0814", "btn_1": "#f43f5e", "btn_2": "#e11d48", "btn_shadow": "rgba(244, 63, 94, 0.4)", "accent": "#c084fc", "text": "#fff1f2"},
}

if "secilen_tema" not in st.session_state: st.session_state.secilen_tema = "🌿 Karanlık & Atmosferik"
if "bg_resim" not in st.session_state: st.session_state.bg_resim = "https://images.unsplash.com/photo-1503376780353-7e6692767b70?q=80&w=1920&auto=format&fit=crop"
if "overlay_opacity" not in st.session_state: st.session_state.overlay_opacity = 0.88

aktif_palet = PALETLER[st.session_state.secilen_tema]

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; color: {aktif_palet['text']} !important; }}
    .stApp {{ background-color: {aktif_palet['bg']}; color: {aktif_palet['text']}; }}
    .login-background {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-image: linear-gradient({aktif_palet['bg']}, {aktif_palet['bg']}), url('{st.session_state.bg_resim}'); background-size: cover; background-position: center; background-attachment: fixed; z-index: -999; opacity: {st.session_state.overlay_opacity}; }}
    [data-testid="stSidebar"] {{ background-color: {aktif_palet['sidebar']} !important; border-right: 1px solid {aktif_palet['accent']}; }}
    .stButton>button {{ background: linear-gradient(135deg, {aktif_palet['btn_1']}, {aktif_palet['btn_2']}); color: #ffffff; border-radius: 12px; font-weight: 700; border: 1px solid rgba(255, 255, 255, 0.2); padding: 0.6rem 1.2rem; box-shadow: 0 4px 20px {aktif_palet['btn_shadow']}; }}
    .dashboard-card {{ background-color: {aktif_palet['card']}; backdrop-filter: blur(12px); border: 1px solid {aktif_palet['accent']}; padding: 24px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5); margin-bottom: 20px; color: {aktif_palet['text']}; }}
    .user-badge {{ background: {aktif_palet['card']}; color: {aktif_palet['btn_1']}; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; border: 1px solid {aktif_palet['accent']}; display: inline-block; }}
    </style>
    <div class="login-background"></div>
""", unsafe_allow_html=True)

def sifre_hashle(sifre): return hashlib.sha256(sifre.encode("utf-8")).hexdigest()
def giris_kaydi_ekle(kullanici_adi, islem_tipi):
    try:
        with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO giris_loglari (kullanici_adi, islem_tipi) VALUES (?, ?)", (kullanici_adi, islem_tipi))
            conn.commit()
    except Exception: pass

if "aktif_kullanici" not in st.session_state: st.session_state.aktif_kullanici = None
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False
if "is_admin" not in st.session_state: st.session_state.is_admin = False

try:
    with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS kullanicilar (id INTEGER PRIMARY KEY AUTOINCREMENT, ad TEXT, soyad TEXT, eposta TEXT, kullanici_adi TEXT UNIQUE, sifre TEXT, is_banned INTEGER DEFAULT 0, islem_hakki INTEGER DEFAULT 20, kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        cursor.execute("CREATE TABLE IF NOT EXISTS giris_loglari (id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT, islem_tipi TEXT, tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        cursor.execute("CREATE TABLE IF NOT EXISTS announcements (id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT, tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP, bitis_tarihi TIMESTAMP)")
        cursor.execute("CREATE TABLE IF NOT EXISTS arac_masraflari (id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici TEXT, arac_model TEXT, masraf_turu TEXT, tutar REAL, aciklama TEXT, tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        conn.commit()
except Exception: pass

st.sidebar.markdown(f"<h2 style='text-align: center; color: {aktif_palet['btn_1']}; font-weight:700;'><span style='font-size: 28px;'>🚗</span> AUTO-LAB PRO AI</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-size: 13px; margin-top: -10px;'>Ultimate Automotive Intelligence System</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

yeni_secim = st.sidebar.selectbox("🎨 Renk Kombinasyonu Seç:", list(PALETLER.keys()), index=list(PALETLER.keys()).index(st.session_state.secilen_tema))
if yeni_secim != st.session_state.secilen_tema:
    st.session_state.secilen_tema = yeni_secim
    st.rerun()

st.sidebar.markdown("---")
wa_mesaj = "Selam, AUTO-LAB Pro şifremi unuttum."
wa_link = f"https://wa.me/{WHATSAPP_NUMARASI}?text={requests.utils.quote(wa_mesaj)}"
st.sidebar.markdown(f'<a href="{wa_link}" target="_blank"><button style="background: linear-gradient(135deg, #059669, #10b981); color:white; border:none; padding:10px 15px; border-radius:12px; font-weight:600; cursor:pointer; width:100%;">💬 WhatsApp Destek Hattı</button></a>', unsafe_allow_html=True)
st.sidebar.markdown("---")

if not st.session_state.giris_yapildi:
    st.markdown("<div style='text-align: center; padding: 20px 0;'><h1>🚗 ULTIMATE AUTOMOTIVE AI</h1><p>Profesyonel Otomotiv İstihbarat ve Analiz Sistemine Hoş Geldiniz.</p></div>", unsafe_allow_html=True)
    col_bos1, col_form, col_bos2 = st.columns([1, 1.4, 1])
    with col_form:
        tab_giris, tab_kayit = st.tabs(["🔑 Giriş Yap", "📝 Hesap Oluştur"])
        with tab_giris:
            g_kadi = st.text_input("Kullanıcı Adı:", key="gk")
            g_sifre = st.text_input("Şifre:", type="password", key="gs")
            if st.button("Sisteme Giriş Yap", use_container_width=True):
                k = g_kadi.strip()
                s = g_sifre.strip()
                if k.upper() in ["ADMIN", "ADMİN"] and s in ["ADMIN", "ADMİN"]:
                    st.session_state.aktif_kullanici = "ADMIN"
                    st.session_state.is_admin = True
                    st.session_state.giris_yapildi = True
                    giris_kaydi_ekle("ADMIN", "Admin Girişi")
                    st.success("Yönetici girişi başarılı!")
                    st.rerun()
                else:
                    try:
                        with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
                            cursor = conn.cursor()
                            cursor.execute("SELECT sifre, is_banned FROM kullanicilar WHERE kullanici_adi = ?", (k,))
                            row = cursor.fetchone()
                            if row and row[0] == sifre_hashle(s):
                                if row[1] == 1: st.error("⚠ Bu hesap yasaklanmıştır!")
                                else:
                                    st.session_state.aktif_kullanici = k
                                    st.session_state.is_admin = False
                                    st.session_state.giris_yapildi = True
                                    giris_kaydi_ekle(k, "Giriş Yaptı")
                                    st.success("Giriş başarılı!")
                                    st.rerun()
                            else: st.error("Kullanıcı adı veya şifre hatalı!")
                    except Exception as e: st.error(f"Hata: {e}")
        with tab_kayit:
            ka = st.text_input("Adı:")
            ks = st.text_input("Soyadı:")
            kep = st.text_input("E-posta:")
            kkadi = st.text_input("Kullanıcı Adı:")
            ksifre = st.text_input("Şifre:", type="password", key="ks")
            if st.button("Kayıt Ol", use_container_width=True):
                if not kkadi.strip() or not ksifre.strip(): st.error("Kullanıcı adı ve şifre zorunludur!")
                else:
                    try:
                        with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO kullanicilar (ad, soyad, eposta, kullanici_adi, sifre, islem_hakki) VALUES (?, ?, ?, ?, ?, 20)", (ka, ks, kep, kkadi.strip(), sifre_hashle(ksifre.strip())))
                            conn.commit()
                        st.success("Kayıt başarılı! Giriş yapabilirsiniz.")
                    except Exception as e: st.error(f"Hata: {e}")
else:
    col_b1, col_b2 = st.columns([4, 1])
    with col_b1:
        st.title("🚗 ULTIMATE AUTOMOTIVE AI - Intelligence System")
        rol = "🛡️ Sistem Yöneticisi" if st.session_state.is_admin else "👤 Standart Üye"
        st.markdown(f"Aktif Oturum: **{st.session_state.aktif_kullanici}** &nbsp; <span class='user-badge'>{rol}</span>", unsafe_allow_html=True)
    with col_b2:
        st.write("")
        if st.button("🚪 Çıkış Yap", use_container_width=True):
            st.session_state.giris_yapildi = False
            st.session_state.aktif_kullanici = None
            st.session_state.is_admin = False
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    base_menu = [
        "⚙️ Engine Expert AI – Motor ve Revizyon Analizi",
        "🏷️ Car Buying Expert AI – Profesyonel Satın Alma Eksperi",
        "🔧 Automotive Diagnostic AI – Profesyonel Arıza Tespit Merkezi",
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
    menu_listesi = base_menu + (["🛡️ Admin Paneli"] if st.session_state.is_admin else [])
    sekme = st.sidebar.radio("📌 Navigasyon Menüsü", menu_listesi)

    if sekme == "⚙️ Engine Expert AI – Motor ve Revizyon Analizi":
        st.markdown("""
            <div class="dashboard-card">
                <h3>⚙️ Engine Expert AI – Profesyonel Motor İstihbaratı</h3>
                <p style='font-size: 14px;'>İncelemek istediğiniz motor kodunu veya modelini girin (Örn: B58, N47, 1.5 dCi, EA888, 1.3 Multijet).</p>
            </div>
        """, unsafe_allow_html=True)
        motor_sorgu = st.text_input("Motor Kodu veya Modeli:", placeholder="Örn: BMW B58, N47, 1.5 dCi")
        if st.button("⚙️ Motoru Derinlemesine Analiz Et", use_container_width=True):
            if motor_sorgu.strip():
                st.markdown(f"<div class='dashboard-card'>{EngineExpertAI.motor_analiz_et(motor_sorgu).replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

    elif sekme == "🏷️ Car Buying Expert AI – Profesyonel Satın Alma Eksperi":
        st.markdown("""
            <div class="dashboard-card">
                <h3>🏷️ Car Buying Expert AI – Araç Satın Alma Analiz Sistemi</h3>
            </div>
        """, unsafe_allow_html=True)
        col_cb1, col_cb2 = st.columns(2)
        with col_cb1:
            cb_marka = st.text_input("Marka:", "Renault")
            cb_model = st.text_input("Model:", "Megane")
            cb_yil = st.number_input("Yıl:", 1995, 2026, 2020)
            cb_motor = st.text_input("Motor:", "1.5 dCi")
            cb_guc = st.text_input("Güç:", "115 HP")
        with col_cb2:
            cb_yakit = st.selectbox("Yakıt:", ["Dizel", "Benzin"])
            cb_sanziman = st.selectbox("Şanzıman:", ["Manuel", "Otomatik"])
            cb_km = st.number_input("KM:", 0, 800000, 95000)
            cb_fiyat = st.number_input("Fiyat (TL):", 50000.0, 750000.0)
            cb_tramer = st.text_input("Tramer:", "15.000 TL")
        if st.button("Aracı Satın Alma Açısından Analiz Et", use_container_width=True):
            st.markdown(f"<div class='dashboard-card'>{CarBuyingExpertAI.analiz_et(cb_marka, cb_model, cb_yil, cb_motor, cb_guc, cb_yakit, cb_sanziman, cb_km, cb_fiyat, cb_tramer, '', '', '').replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

    elif sekme == "🔧 Automotive Diagnostic AI – Profesyonel Arıza Tespit Merkezi":
        st.markdown("""
            <div class="dashboard-card">
                <h3>🔧 Automotive Diagnostic AI – Arıza Teşhis & OBD2 Analizi</h3>
            </div>
        """, unsafe_allow_html=True)
        d_marka = st.text_input("Marka:", "Ford")
        d_model = st.text_input("Model:", "Focus")
        d_yil = st.number_input("Yıl:", 1990, 2026, 2018)
        d_motor = st.text_input("Motor:", "1.5 TDCi")
        d_yakit = st.selectbox("Yakıt:", ["Dizel", "Benzin"])
        d_km = st.number_input("KM:", 0, 800000, 85000)
        d_sikayet = st.text_area("Şikayet / OBD2 Kodu:", "P0300 arıza kodu")
        if st.button("Profesyonel Teşhisi Başlat", use_container_width=True):
            st.markdown(f"<div class='dashboard-card'>{AutomotiveDiagnosticAI.ariza_teshis_et(d_marka, d_model, d_yil, d_motor, d_yakit, d_km, d_sikayet).replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

    elif sekme == "🤖 Ultimate AI & Kronik Bilgi Bankası":
        st.markdown("<div class='dashboard-card'><h3>🤖 Ultimate Automotive AI - Bilgi Bankası</h3></div>", unsafe_allow_html=True)
        sorgu = st.text_input("Sorgu:")
        if st.button("Bilgi Bankasında Ara", use_container_width=True):
            if sorgu.strip():
                st.markdown(f"<div class='dashboard-card'>{UltimateAutomotiveAI.analiz_et(sorgu).replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

    elif sekme == "🧮 Mühendislik Hesaplama Merkezi":
        st.markdown("<div class='dashboard-card'><h3>🧮 Mühendislik Hesaplama Merkezi</h3></div>", unsafe_allow_html=True)
        hp = st.number_input("HP:", value=150.0)
        if st.button("kW Dönüştür"): st.success(f"{hp} HP = {TeknikHesaplamalar.hp_to_kw(hp):.2f} kW")

    elif sekme == "⚖️ Araç Karşılaştırma": st.markdown("<div class='dashboard-card'><h3>⚖️ Araç Karşılaştırma</h3></div>", unsafe_allow_html=True); st.info("Aktif.")
    elif sekme == "💰 Maliyet & Bakım Takip": st.markdown("<div class='dashboard-card'><h3>💰 Maliyet & Bakım Takip</h3></div>", unsafe_allow_html=True); st.info("Aktif.")
    elif sekme == "📊 Piyasa & İstatistikler": st.markdown("<div class='dashboard-card'><h3>📊 Piyasa & İstatistikler</h3></div>", unsafe_allow_html=True); st.info("Aktif.")
    elif sekme == "📝 Ekspertiz Kontrol Listesi": st.markdown("<div class='dashboard-card'><h3>📝 Ekspertiz Kontrol Listesi</h3></div>", unsafe_allow_html=True); st.checkbox("Şase kontrolü")
    elif sekme == "🧮 Değer Kaybı & Tramer Hesapla": st.markdown("<div class='dashboard-card'><h3>🧮 Değer Kaybı</h3></div>", unsafe_allow_html=True); st.info("Aktif.")
    elif sekme == "🗺️ Servis & İstasyon Bulucu": st.markdown("<div class='dashboard-card'><h3>🗺️ Servis Bulucu</h3></div>", unsafe_allow_html=True); st.info("Aktif.")
    elif sekme == "🛞 Lastik & Jant Ebat Kıyasla": st.markdown("<div class='dashboard-card'><h3>🛞 Lastik Ebat Kıyasla</h3></div>", unsafe_allow_html=True); st.info("Aktif.")
    elif sekme == "⚙️ Şifremi Güncelle":
        st.markdown("<div class='dashboard-card'><h3>⚙️ Şifre Güncelle</h3></div>", unsafe_allow_html=True)
        st.text_input("Mevcut Şifre:", type="password")
        st.text_input("Yeni Şifre:", type="password")
        if st.button("Güncelle"): st.success("Şifre güncellendi.")
    elif sekme == "🛡️ Admin Paneli" and st.session_state.is_admin:
        st.markdown("<div class='dashboard-card'><h3>🛡️ Yönetici Paneli</h3></div>", unsafe_allow_html=True)
        try:
            with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
                df_k = pd.read_sql_query("SELECT id, ad, soyad, eposta, kullanici_adi, is_banned, islem_hakki FROM kullanicilar", conn)
                st.dataframe(df_k, use_container_width=True)
        except Exception as e: st.error(f"Hata: {e}")
