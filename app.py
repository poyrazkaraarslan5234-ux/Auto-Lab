import os
import sqlite3
from datetime import datetime
import pandas as pd
import qrcode
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
import streamlit as st

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Auto Lab Pro - Ultimate ECU & Car Studio", page_icon="🚗", layout="wide")

WHATSAPP_NUMARASI = "905510305139"

# --- SABİT WHATSAPP BUTONU ---
st.markdown(f"""
    <style>
    .fixed-whatsapp {{
        position: fixed;
        top: 15px;
        left: 20px;
        z-index: 999999;
        background-color: #25d366;
        color: white;
        padding: 8px 14px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 13px;
        text-decoration: none;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        gap: 5px;
    }}
    .fixed-whatsapp:hover {{
        background-color: #20ba5a;
        color: white;
    }}
    </style>
    <a href="https://wa.me/{WHATSAPP_NUMARASI}?text=Merhaba,%20Auto%20Lab%20Pro%20için%20şifremi%20almak%20istiyorum." target="_blank" class="fixed-whatsapp">
        💬 Şifre Al
    </a>
""", unsafe_allow_html=True)

# --- SQLITE VERİTABANI BAŞLATMA ---
def init_db():
    try:
        conn = sqlite3.connect("autolab_pro.db", timeout=10)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS raporlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tarih TEXT,
                plaka TEXT,
                model TEXT,
                yil INTEGER,
                km INTEGER,
                sonuc TEXT,
                tavsiye TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS islem_loglari (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modul_adi TEXT,
                detay TEXT,
                sonuc TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS galeri_stok (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plaka TEXT,
                model TEXT,
                alis_fiyati REAL,
                alis_tarihi TEXT,
                durum TEXT
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Veritabanı hatası: {e}")

init_db()

def rapor_kaydet(plaka, model, yil, km, sonuc, tavsiye):
    try:
        conn = sqlite3.connect("autolab_pro.db", timeout=10)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO raporlar (tarih, plaka, model, yil, km, sonuc, tavsiye)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (datetime.now().strftime('%d.%m.%Y %H:%M'), plaka, model, yil, km, sonuc, tavsiye))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Kayıt hatası: {e}")

def log_kaydet(modul, detay, sonuc):
    try:
        conn = sqlite3.connect("autolab_pro.db", timeout=10)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO islem_loglari (modul_adi, detay, sonuc) VALUES (?, ?, ?)", (modul, detay, sonuc))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Loglama hatası: {e}")

# --- OTURUM YÖNETİMİ VE LİMİTLER ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "islem_sayisi" not in st.session_state:
    st.session_state.islem_sayisi = 0

UCRETSIZ_HAK_SINIRI = 25  
PREMIUM_HAK_SAYISI = 250 

toplam_izin_verilen = PREMIUM_HAK_SAYISI if st.session_state.logged_in else UCRETSIZ_HAK_SINIRI

if st.session_state.islem_sayisi >= toplam_izin_verilen and not st.session_state.logged_in:
    st.markdown("""
        <div style="text-align: center; padding: 40px; background: #111827; border-radius: 20px; border: 1px solid #374151; margin-top: 40px;">
            <h1 style="color: #f87171; margin-bottom: 10px;">⚠️ 25 İşlem Hakkınız Doldu!</h1>
            <p style="color: #9ca3af;">Uygulamayı kesintisiz kullanmaya devam etmek için sol üstteki WhatsApp butonundan size özel şifreyi alıp yazabilirsiniz.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    girilen_sifre = st.text_input("🔑 Size Özel Erişim Şifresi:", type="password")
    
    if st.button("Sisteme Giriş Yap", type="primary", use_container_width=True):
        gecerli_sifreler = ["autolab2026", "pro9955", "vip-oto-sifre", "12345"]
        if girilen_sifre in gecerli_sifreler:
            st.session_state.logged_in = True
            st.session_state.islem_sayisi = 0  
            st.success("Giriş başarılı! Yönlendiriliyorsunuz...")
            st.rerun()
        else:
            st.error("Hatalı veya geçersiz şifre!")
    st.stop()

st.markdown("""
    <style>
    .main { background-color: #0b0f19; }
    .stApp { background-color: #0b0f19; color: #f3f4f6; }
    .hero-card {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        border: 1px solid #374151; padding: 30px; border-radius: 20px;
        text-align: center; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3); margin-bottom: 25px;
        margin-top: 20px;
    }
    .hero-title { color: #60a5fa; font-size: 38px; font-weight: 900; margin-bottom: 10px; }
    .info-box {
        background-color: #111827; border-left: 5px solid #3b82f6;
        padding: 20px; border-radius: 12px; margin-bottom: 15px; border: 1px solid #1f2937;
    }
    </style>
""", unsafe_allow_html=True)

def detayli_arac_analizi(arac_adi, yil, km, hasar_durumu):
    try:
        km_int = int(km)
        yil_int = int(yil)
    except:
        km_int = 0
        yil_int = 2020
        
    yas = 2026 - yil_int
    
    if "Hatasız" in hasar_durumu and km_int < 80000 and yas <= 5:
        tavsiye = "🔥 Kesinlikle Alınır! Düşük yaş, düşük kilometre ve hatasız kondisyonda."
        risk = "Çok Düşük. Periyodik bakımlar haricinde masraf açmaz."
    elif "Ağır Hasar" in hasar_durumu or "Şase" in hasar_durumu or "Podye" in hasar_durumu:
        tavsiye = "🚨 Riskli! Uzak Durun. Şase veya podye işlemleri sürüş güvenliğini doğrudan tehlikeli kılar."
        risk = "Yüksek. Kaporta esnemesi ve ağır kaza geçmişi riski."
    elif km_int > 200000 or yas > 12:
        tavsiye = "⚠️ Şartlı Alınır. Yüksek kilometre/yaş sebebiyle motor, turbo ve yürüyen aksam detaylı mekanik eksperden geçmeli."
        risk = "Orta-Yüksek (Masraf çıkarma olasılığı yüksek)."
    else:
        tavsiye = "✅ Değerlendirilebilir. Eksper raporu temiz çıkarsa fiyatta pazarlık yapılarak alınabilir."
        risk = "Orta seviye (Yaşına ve kilometresine uygun aşınmalar mevcut)."

    return {
        "model": f"{yil} {arac_adi.title()}",
        "yas": f"{yas} Yaşında",
        "km": f"{km_int:,} KM".replace(",", "."),
        "eksper": hasar_durumu,
        "risk": risk,
        "tavsiye": tavsiye
    }

def arac_analizi_uret(arac_adi):
    sorgu_kucuk = arac_adi.lower().strip()
    if "civic" in sorgu_kucuk:
        return {"baslik": "Honda Civic", "motor": "1.5 VTEC Turbo / 1.6", "hp": 182, "tork": 240, "guc_tork": "125 - 182 HP", "kronik": "Direksiyon kutusu tıkırtısı, boya hassasiyeti.", "avantaj": "Yüksek piyasa değeri ve ikinci el hızı.", "yag": "0W-20 veya 5W-30 Tam Sentetik", "antifriz": "Organik OAT (Kırmızı/Pembe)", "fren": "DOT 4"}
    elif "doblo" in sorgu_kucuk:
        return {"baslik": "Fiat Doblo", "motor": "1.6 Multijet", "hp": 120, "tork": 320, "guc_tork": "90 - 120 HP", "kronik": "Ön takım aşınmaları, baskı balata.", "avantaj": "Geniş hacim, ucuz ve bol yedek parça.", "yag": "5W-30 DPF Uyumlu (C2/C3)", "antifriz": "Organik (Mavi/Yeşil)", "fren": "DOT 4"}
    elif "passat" in sorgu_kucuk:
        return {"baslik": "VW Passat", "motor": "1.4/1.5 TSI - 2.0 TDI", "hp": 150, "tork": 250, "guc_tork": "150 - 240 HP", "kronik": "DSG kavrama hassasiyeti.", "avantaj": "Üstün konfor ve sessiz izolasyon.", "yag": "5W-30 Longlife (VW 504.00 / 507.00)", "antifriz": "G12++ / G13 (Mor/Pembe)", "fren": "DOT 4 ESP"}
    elif "mustang" in sorgu_kucuk:
        return {"baslik": "Ford Mustang", "motor": "2.3 EcoBoost / 5.0 V8", "hp": 315, "tork": 475, "guc_tork": "315 - 450 HP", "kronik": "Yüksek yakıt tüketimi, lastik aşınması.", "avantaj": "Muazzam performans ve ikonik tasarım.", "yag": "5W-20 / 5W-30 Tam Sentetik", "antifriz": "Ford WSS-M97B44-D (Turuncu)", "fren": "DOT 4 High Performance"}
    else:
        return {"baslik": arac_adi.upper(), "motor": "Standart Ünite", "hp": 110, "tork": 240, "guc_tork": "100 - 150 HP", "kronik": "Yaşlı hortum terletmeleri.", "avantaj": "Günlük kullanım uyumu.", "yag": "5W-30 Tam Sentetik", "antifriz": "Organik Standart (Genel)", "fren": "DOT 4"}

def arac_sorun_analizi_yap(sorun_metni):
    s_kucuk = sorun_metni.lower()
    if "hararet" in s_kucuk or "sicaklik" in s_kucuk or "isindi" in s_kucuk:
        return (
            "⚠️ **Kritik Durum:** Motor termostatı sıkışmış, radyatör tıkalı/delik, devridaim pompası arızalı veya fan müşürü çalışmıyor olabilir. "
            "Conta yanması riski bulunduğundan araç derhal güvenli bir yerde stop edilmeli ve soğuması beklenmelidir.",
            "1.500₺ - 35.000₺ (Arızanın kaynağına göre değişir)"
        )
    elif "turbo" in s_kucuk:
        return ("Turbonun içindeki mil boşluğu, türbin pervanesi aşınması veya intercooler hortumunda kaçak (delik) olabilir. Acil kontrol edilmelidir.", "7.500₺ - 25.000₺+")
    elif "çalışmıyor" in s_kucuk or "marş" in s_kucuk:
        return ("Akü zayıflamış veya marş motoru kömürleri bitmiş olabilir. Akü kutup başlarını kontrol edin.", "1.500₺ - 4.500₺")
    elif "duman" in s_kucuk:
        return ("Siyah duman: Hava filtresi tıkalı veya enjektör arızası. Mavi duman: Motor yağ yakıyor. Beyaz duman: Silindir kapak contası su veriyor olabilir.", "3.000₺ - 20.000₺+")
    elif "titreme" in s_kucuk or "silkeleme" in s_kucuk:
        return ("Buji veya ateşleme bobinlerinde kesinti olabilir yahut baskı balata (debriyaj) arızalıdır.", "1.200₺ - 6.000₺")
    elif "ses" in s_kucuk or "tıkırtı" in s_kucuk or "uğultu" in s_kucuk:
        return ("Ön takımdan (salıncak, rot başı) veya tekerlek bilyasından kaynaklanıyor olabilir.", "1.000₺ - 5.000₺")
    else:
        return ("Belirttiğiniz şikayet genel mekanik veya sensör kaynaklı olabilir. Detaylı ustaya gösterilmesi tavsiye edilir.", "Değişkendir")

def qr_olustur(veri_metni, dosya_adi="qr_temp.png"):
    try:
        qr = qrcode.QRCode(version=1, box_size=5, border=2)
        qr.add_data(veri_metni)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(dosya_adi)
        return dosya_adi
    except Exception as e:
        print(f"QR oluşturma hatası: {e}")
        return None

def pdf_eksper_raporu_olustur(dosya_adi, plaka, marka_model, yil, km, motor_durumu, sema_dict, sonuc, tavsiye, maliyet_hesabi):
    doc = SimpleDocTemplate(dosya_adi, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#1e3a8a'), alignment=1, spaceAfter=6)
    sub_title_style = ParagraphStyle('SubTitleStyle', parent=styles['Heading2'], fontSize=9, textColor=colors.HexColor('#4b5563'), alignment=1, spaceAfter=12)
    section_heading = ParagraphStyle('SectionHeading', parent=styles['Heading3'], fontSize=11, textColor=colors.HexColor('#1d4ed8'), spaceBefore=6, spaceAfter=4)
    normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontSize=8.5, textColor=colors.HexColor('#1f2937'), spaceAfter=4)

    qr_path = qr_olustur(f"Auto Lab Pro Verified Report - Plaka: {plaka} - Model: {marka_model}")

    elements.append(Paragraph("OTO EKSPERTİZ MERKEZİ - QR DOĞRULAMALI KURUMSAL RAPOR", title_style))
    elements.append(Paragraph(f"<b>Rapor Tarihi:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Plaka:</b> {plaka.upper()}", sub_title_style))
    
    elements.append(Paragraph("1. Araç Kimlik ve Genel Bilgileri", section_heading))
    data_arac = [
        ['Araç Marka / Model:', marka_model, 'Model Yılı:', str(yil)],
        ['Güncel Kilometre:', f"{int(km):,} KM".replace(',', '.'), 'Genel Sonuç:', sonuc]
    ]
    t_arac = Table(data_arac, colWidths=[110, 160, 90, 175])
    t_arac.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#e5edff')),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#e5edff')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 4),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
    ]))
    elements.append(t_arac)
    elements.append(Spacer(1, 6))

    elements.append(Paragraph("2. Kaporta Boya Lejantı (Renk Kodları)", section_heading))
    data_lejant = [
        ['Orijinal', 'Boyalı', 'Lokal Boyalı', 'Değişen', 'Sök-Tak / Ayar'],
        ['Beyaz', 'Mavi', 'Sarı', 'Kırmızı', 'Turuncu']
    ]
    t_lejant = Table(data_lejant, colWidths=[106, 106, 106, 106, 105])
    t_lejant.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,1), colors.HexColor('#f3f4f6')),
        ('BACKGROUND', (1,1), (1,1), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (1,1), (1,1), colors.white),
        ('BACKGROUND', (2,1), (2,1), colors.HexColor('#facc15')),
        ('BACKGROUND', (3,1), (3,1), colors.HexColor('#ef4444')),
        ('TEXTCOLOR', (3,1), (3,1), colors.white),
        ('BACKGROUND', (4,1), (4,1), colors.HexColor('#fb923c')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 4),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ]))
    elements.append(t_lejant)
    elements.append(Spacer(1, 6))
    
    elements.append(Paragraph("3. Kuş Bakışı Kaporta Durum Şeması", section_heading))
    data_sema = [
        ['ÖN BÖLÜM', f"Ön Kaput: {sema_dict.get('Ön Kaput', 'Orijinal')}", f"Tavan: {sema_dict.get('Tavan', 'Orijinal')}"],
        ['SOL TARAF', f"Sol Ön Çamurluk: {sema_dict.get('Sol Ön Çamurluk', 'Orijinal')}", f"Sağ Ön Çamurluk: {sema_dict.get('Sağ Ön Çamurluk', 'Orijinal')}"],
        ['YAN KISIM', f"Sol Ön Kapı: {sema_dict.get('Sol Ön Kapı', 'Orijinal')}", f"Sağ Ön Kapı: {sema_dict.get('Sağ Ön Kapı', 'Orijinal')}"],
        ['ORTA KISIM', f"Sol Arka Kapı: {sema_dict.get('Sol Arka Kapı', 'Orijinal')}", f"Sağ Arka Kapı: {sema_dict.get('Sağ Arka Kapı', 'Orijinal')}"],
        ['ARKA YAN', f"Sol Arka Çamurluk: {sema_dict.get('Sol Arka Çamurluk', 'Orijinal')}", f"Sağ Arka Çamurluk: {sema_dict.get('Sağ Arka Çamurluk', 'Orijinal')}"],
        ['ARKA BÖLÜM', f"Bagaj Kapağı: {sema_dict.get('Bagaj Kapağı', 'Orijinal')}", f"Şase/Podye: {sema_dict.get('Şase ve Podye', 'Orijinal')}"]
    ]
    t_sema = Table(data_sema, colWidths=[100, 217, 218])
    t_sema.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#e5edff')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 4),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
    ]))
    elements.append(t_sema)
    elements.append(Spacer(1, 6))

    elements.append(Paragraph("4. Tahmini Onarım ve Boya Maliyet Analizi", section_heading))
    data_maliyet = [
        ['Toplam Hasarlı/İşlemli Parça:', f"{maliyet_hesabi['adet']} Parça"],
        ['Tahmini Masraf Aralığı:', f"{maliyet_hesabi['tutar']:,} ₺".replace(',', '.')]
    ]
    t_mal = Table(data_maliyet, colWidths=[150, 385])
    t_mal.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#fef9c3')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 4),
        ('FONTSIZE', (0,0), (-1,-1), 8),
    ]))
    elements.append(t_mal)
    elements.append(Spacer(1, 6))

    elements.append(Paragraph("5. Mekanik Kontrol ve Yapay Zeka Tavsiyesi", section_heading))
    data_mekanik = [
        ['Motor Durumu:', motor_durumu],
        ['Uzman Tavsiyesi:', tavsiye]
    ]
    t_mek = Table(data_mekanik, colWidths=[110, 425])
    t_mek.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f3f4f6')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 4),
        ('FONTSIZE', (0,0), (-1,-1), 8),
    ]))
    elements.append(t_mek)
    elements.append(Spacer(1, 10))
    
    if qr_path and os.path.exists(qr_path):
        elements.append(RLImage(qr_path, width=70, height=70))
        
    elements.append(Paragraph("<b>Yasal Uyarı:</b> Bu rapor Auto Lab Pro dinamik sistemleri ile üretilmiştir.", normal_style))
    doc.build(elements)

with st.sidebar:
    st.markdown("### 📊 Kullanım Durumu")
    kalan_hak = (PREMIUM_HAK_SAYISI if st.session_state.logged_in else UCRETSIZ_HAK_SINIRI) - st.session_state.islem_sayisi
    st.write(f"Kalan İşlem Hakkı: {max(0, kalan_hak)}")

    if st.session_state.logged_in:
        st.success("🔓 VIP / Premium Üye Modu (250 Hak)")
        if st.button("Oturumu Kapat"):
            st.session_state.logged_in = False
            st.session_state.islem_sayisi = 0
            st.rerun()
    st.divider()

st.markdown("""
    <div class="hero-card">
        <div class="hero-title">🚗 AUTO LAB PRO - ULTIMATE EDITION</div>
        <div class="hero-title" style="font-size: 20px; color: #38bdf8; margin-top: 5px;">Mühendislik Odaklı Dinamik Araç & Ekspertiz Analiz Merkezi</div>
    </div>
""", unsafe_allow_html=True)

sekme = st.selectbox("Auto Lab Ana Menü:", [
    "🔍 Manuel Araç & Ekspertiz Analizi",
    "📄 PDF Eksper Raporu & Renkli Şema",
    "🚗 Model & Motor Veritabanı", 
    "⚖️ Serbest Araç Karşılaştırma", 
    "⚡ Gelişmiş ECU & Chip Tuning Simülatörü",
    "🛠️ Araç Sorunları & Çözüm Asistanı",
    "🔊 Araç İçi Ses & NVH Arıza Teşhisi",
    "🏷️ Yedek Parça Orijinal/Yan Sanayi Kıyas",
    "📋 Tramer & Parça Maliyet Simülatörü",
    "💰 Galeri Al-Sat & Kar Hesaplayıcı",
    "📜 Noter & Devir Masraf Hesaplayıcı",
    "🔧 OBD-II Arıza Kodu (DTC) Sözlüğü",
    "🏎️ Performans & 0-100 Simülatörü",
    "📂 Kayıtlı Arşiv & Raporlar",
    "🛠️ Yedek Parça & İşçilik Teklifi",
    "🅿️ Galeri Stok & Envanter",
    "⛽ Akaryakıt & Seyahat Maliyeti",
    "📝 Plaka & Hasar Not Defteri",
    "⏱️ Periyodik Bakım Takibi"
])

if sekme == "🔍 Manuel Araç & Ekspertiz Analizi":
    st.markdown("### 📋 Araç Bilgileri & Profesyonel Ekspertiz Analizi")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        arac_adi_input = st.text_input("Araç Marka ve Modeli:", placeholder="Örn: Ford Focus 1.5 TDCİ", key="man_arac")
        yil_input = st.number_input("Model / Çıkış Yılı:", min_value=1990, max_value=2026, value=2020, step=1, key="man_yil")
    with col_m2:
        km_input = st.number_input("Güncel Kilometre (KM):", min_value=0, max_value=800000, value=75000, step=1000, key="man_km")
        hasar_input = st.selectbox("Genel Kaporta / Hasar Durumu:", [
            "Hatasız / Boyasız / Değişensiz",
            "1-2 Parça Lokal Boyalı",
            "1-2 Parça Değişen, Boyalı Parçalar Var",
            "Komple Boyalı / Tavan Boyasız",
            "Ağır Hasar Kayıtlı / Şase veya Podye İşlemli"
        ], key="man_hasar")
    
    if st.button("🤖 Yapay Zeka Ekspertiz Raporunu Oluştur", key="btn_man"):
        if not arac_adi_input:
            st.warning("Lütfen araç marka ve modelini boş bırakmayın!")
        else:
            st.session_state.islem_sayisi += 1
            rapor = detayli_arac_analizi(arac_adi_input, yil_input, km_input, hasar_input)
            rapor_kaydet("34 PLK 99", rapor['model'], yil_input, km_input, rapor['risk'], rapor['tavsiye'])
            log_kaydet("Manuel Eksper", f"Araç: {rapor['model']}", rapor['risk'])
            st.success("✅ Ekspertiz ve Risk Analizi Başarıyla Tamamlandı & Arşivlendi!")
            st.markdown(f"""
                <div class="info-box">
                    <h3 style="color: #60a5fa; margin-top:0;">📌 Araç: {rapor['model']}</h3>
                    <p><b>⏳ Yaş Durumu:</b> {rapor['yas']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>📏 Kilometre:</b> <span style="color: #38bdf8; font-weight: bold;">{rapor['km']}</span></p>
                    <p><b>🛡️ Bildirilen Hasar / Ekspertiz:</b> {rapor['eksper']}</p>
                    <hr style="border-color: #374151;">
                    <p><b>⚠️ Detaylı Risk Analizi:</b> <span style="color: #f87171;">{rapor['risk']}</span></p>
                    <p><b>💰 Alınır mı?:</b> {rapor['tavsiye']}</p>
                </div>
            """, unsafe_allow_html=True)

elif sekme == "📄 PDF Eksper Raporu & Renkli Şema":
    st.markdown("### 🗺️ Kuş Bakışı Renkli Şema & Kurumsal PDF Eksper Raporu")
    st.markdown("<p style='color: #9ca3af;'>Parça durumlarına göre renk kodlarıyla profesyonel PDF oluşturun.</p>", unsafe_allow_html=True)
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        pdf_plaka = st.text_input("Araç Plakası:", placeholder="Örn: 34 ABC 123", key="pdf_plk")
        pdf_model = st.text_input("Araç Marka ve Modeli:", placeholder="Örn: Renault Megane 1.5 dCi", key="pdf_mdl")
        pdf_yil = st.number_input("Model Yılı:", min_value=1990, max_value=2026, value=2021, step=1, key="pdf_yl")
        pdf_km = st.number_input("Güncel Kilometre:", min_value=0, max_value=800000, value=65000, step=1000, key="pdf_k")
    with col_p2:
        pdf_motor = st.selectbox("Motor / Mekanik Durum:", [
            "Motor Performansı %90 - Kusursuz",
            "Motor Performansı %78 - Normal Aşınma",
            "Turbo Bakımı Gerekli",
            "Ağır Motor Arızalı"
        ], key="pdf_mtr")

    st.markdown("---")
    st.markdown("#### 🚗 Kuş Bakışı Şema Parça Renklendirmeleri")
    
    durum_secenekleri = ["Orijinal (Beyaz)", "Boyalı (Mavi)", "Lokal Boyalı (Sarı)", "Değişen (Kırmızı)", "Sök-Tak (Turuncu)"]
    
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        s_kaput = st.selectbox("Ön Kaput", durum_secenekleri, key="s_kaput")
        s_tavan = st.selectbox("Tavan", durum_secenekleri, key="s_tavan")
        s_bagaj = st.selectbox("Bagaj Kapağı", durum_secenekleri, key="s_bagaj")
        s_sol_on_camurluk = st.selectbox("Sol Ön Çamurluk", durum_secenekleri, key="s_soc")
    with col_s2:
        s_sol_on_kapi = st.selectbox("Sol Ön Kapı", durum_secenekleri, key="s_sok")
        s_sol_arka_kapi = st.selectbox("Sol Arka Kapı", durum_secenekleri, key="s_sak")
        s_sol_arka_camurluk = st.selectbox("Sol Arka Çamurluk", durum_secenekleri, key="s_sac")
        s_sag_on_camurluk = st.selectbox("Sağ Ön Çamurluk", durum_secenekleri, key="s_soc2")
    with col_s3:
        s_sag_on_kapi = st.selectbox("Sağ Ön Kapı", durum_secenekleri, key="s_sok2")
        s_sag_arka_kapi = st.selectbox("Sağ Arka Kapı", durum_secenekleri, key="s_sak2")
        s_sag_arka_camurluk = st.selectbox("Sağ Arka Çamurluk", durum_secenekleri, key="s_sac2")
        s_sase = st.selectbox("Şase / Podye Durumu", ["Orijinal (Beyaz)", "İşlemli (Kırmızı)"], key="s_sase")

    sema_sozlugu = {
        "Ön Kaput": s_kaput, "Tavan": s_tavan, "Bagaj Kapağı": s_bagaj,
        "Sol Ön Çamurluk": s_sol_on_camurluk, "Sol Ön Kapı": s_sol_on_kapi, "Sol Arka Kapı": s_sol_arka_kapi,
        "Sol Arka Çamurluk": s_sol_arka_camurluk, "Sağ Ön Çamurluk": s_sag_on_camurluk, "Sağ Ön Kapı": s_sag_on_kapi,
        "Sağ Arka Kapı": s_sag_arka_kapi, "Sağ Arka Çamurluk": s_sag_arka_camurluk, "Şase ve Podye": s_sase
    }

    hatali_parca_sayisi = sum(1 for v in sema_sozlugu.values() if "Orijinal" not in v)
    tahmini_onarim_maliyeti = hatali_parca_sayisi * 4500
    maliyet_verisi = {"adet": hatali_parca_sayisi, "tutar": tahmini_onarim_maliyeti}

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📥 Renkli Şemalı PDF Raporunu Oluştur ve İndir", type="primary", key="btn_pdf"):
        if not pdf_plaka or not pdf_model:
            st.warning("Lütfen plaka ve araç modelini boş bırakmayın!")
        else:
            st.session_state.islem_sayisi += 1
            genel_hasar_ozeti = "Şase İşlemli / Ağır" if "İşlemli" in s_sase else ("Parça Boyalı/Değişen Var" if hatali_parca_sayisi > 0 else "Temiz / Orijinal")
            gecici_analiz = detayli_arac_analizi(pdf_model, pdf_yil, pdf_km, genel_hasar_ozeti)
            
            rapor_kaydet(pdf_plaka, pdf_model, pdf_yil, pdf_km, gecici_analiz['risk'], gecici_analiz['tavsiye'])
            log_kaydet("PDF Eksper Raporu", f"Plaka: {pdf_plaka}, Model: {pdf_model}", "PDF Başarıyla Üretildi")

            dosya_adi = f"AutoLab_RenkliSema_Raporu_{pdf_plaka.replace(' ', '')}.pdf"
            pdf_eksper_raporu_olustur(
                dosya_adi, pdf_plaka, pdf_model, pdf_yil, pdf_km, pdf_motor, 
                sema_sozlugu, gecici_analiz['risk'], gecici_analiz['tavsiye'], maliyet_verisi
            )
            
            st.success("🎉 Renkli Şemalı & QR Doğrulamalı Eksper Raporu Hazır!")
            if os.path.exists(dosya_adi):
                with open(dosya_adi, "rb") as file:
                    st.download_button(
                        label="💾 Raporu İndir (PDF + QR + Maliyet)",
                        data=file, file_name=dosya_adi, mime="application/pdf",
                        type="primary", key="dl_pdf"
                    )

elif sekme == "🚗 Model & Motor Veritabanı":
    secilen_model = st.selectbox("🔍 Hazır Model Seçin:", ["Honda Civic", "Fiat Doblo", "Volkswagen Passat", "Ford Mustang"], key="db_model")
    veri = arac_analizi_uret(secilen_model)
    log_kaydet("Model DB", f"Seçilen: {secilen_model}", "Görüntülendi")
    st.markdown(f"""
        <div class="info-box">
            <h3 style="color: #60a5fa; margin-top:0;">📌 {veri['baslik']}</h3>
            <p><b>⚙️ Motor:</b> {veri['motor']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>🐎 Güç / Tork:</b> <span style="color: #38bdf8; font-weight: bold;">{veri['guc_tork']}</span></p>
            <hr style="border-color: #374151;">
            <p><b>⚠️ Kronik Sorunlar:</b> <span style="color: #f87171;">{veri['kronik']}</span></p>
            <p><b>🌟 Avantajlar:</b> <span style="color: #34d399;">{veri['avantaj']}</span></p>
        </div>
    """, unsafe_allow_html=True)

elif sekme == "⚖️ Serbest Araç Karşılaştırma":
    st.markdown("### ⚖️ Serbest Model & Motor Kıyaslama Modülü")
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        arac_input_1 = st.text_input("1. Aracı Yazın:", "Civic", key="cmp_1")
    with col_k2:
        arac_input_2 = st.text_input("2. Aracı Yazın:", "Passat", key="cmp_2")
        
    if arac_input_1 and arac_input_2:
        d1 = arac_analizi_uret(arac_input_1)
        d2 = arac_analizi_uret(arac_input_2)
        log_kaydet("Araç Karşılaştırma", f"{d1['baslik']} vs {d2['baslik']}", "Karşılaştırıldı")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
                <div class="info-box">
                    <h4 style="color: #60a5fa; margin-top:0;">🚗 {d1['baslik']}</h4>
                    <p><b>⚙️ Motor:</b> {d1['motor']}</p>
                    <p><b>🐎 Güç/Tork:</b> {d1['guc_tork']}</p>
                </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
                <div class="info-box">
                    <h4 style="color: #60a5fa; margin-top:0;">🚗 {d2['baslik']}</h4>
                    <p><b>⚙️ Motor:</b> {d2['motor']}</p>
                    <p><b>🐎 Güç/Tork:</b> {d2['guc_tork']}</p>
                </div>
            """, unsafe_allow_html=True)

elif sekme == "⚡ Gelişmiş ECU & Chip Tuning Simülatörü":
    st.markdown("### ⚡ Güncellenmiş Dinamik ECU & Chip Tuning Simülatörü")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st_arac_adi = st.text_input("Araç Model / Motor Adı (örn: Ford Mustang 2.3 EcoBoost / Passat 2.0 TDI):", "Ford Mustang", key="ecu_arac")
        motor_tipi = st.selectbox("Motor Besleme Türü:", ["Turbo Benzinli (Turbocharged Petrol)", "Turbo Dizel (Turbodiesel)", "Atmosferik (Naturally Aspirated)"], key="ecu_tip")
        otomatik_veri = arac_analizi_uret(st_arac_adi)
        st_hp = otomatik_veri.get("hp", 150)
        st_tork = otomatik_veri.get("tork", 250)
        st.info(f"✨ **Otomatik Algılanan Stok Değerler:**\n- **Güç:** {st_hp} HP\n- **Tork:** {st_tork} Nm")
    with col_t2:
        secilen_stage = st.selectbox("Yazılım Seviyesi Seçin:", [
            "Stage 1 (Güvenli / Orijinal Donanım)", 
            "Stage 2 (Downpipe + Performans Filtre/Intercooler)", 
            "Stage 3 (Büyük Turbo + Enjektör + Komple Egzoz)"
        ], key="ecu_stage")
        yakit_kalitesi = st.selectbox("Yakıt Kalitesi / Oktan:", ["95 Oktan Normal Benzin / Standart Mazot", "97/98 Oktan Yüksek Kaliteli Yakıt"], key="ecu_yakit")

    if st.button("🚀 Gerçekçi ECU Haritası Hesapla ve Uygula", key="btn_ecu"):
        st.session_state.islem_sayisi += 1
        
        if "Atmosferik" in motor_tipi:
            carpban_hp = 1.06 if "Stage 1" in secilen_stage else (1.09 if "Stage 2" in secilen_stage else 1.12)
            carpban_tork = 1.05 if "Stage 1" in secilen_stage else (1.08 if "Stage 2" in secilen_stage else 1.10)
        elif "Dizel" in motor_tipi:
            carpban_hp = 1.20 if "Stage 1" in secilen_stage else (1.32 if "Stage 2" in secilen_stage else 1.48)
            carpban_tork = 1.28 if "Stage 1" in secilen_stage else (1.42 if "Stage 2" in secilen_stage else 1.60)
        else:
            carpban_hp = 1.22 if "Stage 1" in secilen_stage else (1.38 if "Stage 2" in secilen_stage else 1.65)
            carpban_tork = 1.20 if "Stage 1" in secilen_stage else (1.35 if "Stage 2" in secilen_stage else 1.55)
            
        if "Yüksek Kaliteli" in yakit_kalitesi:
            carpban_hp += 0.03
            carpban_tork += 0.03

        hesaplanmis_hp = int(st_hp * carpban_hp)
        hesaplanmis_tork = int(st_tork * carpban_tork)

        log_kaydet("ECU Simülatörü", f"Araç: {st_arac_adi}, {secilen_stage}", f"Yeni HP: {hesaplanmis_hp}")
        st.success("✅ Profesyonel ECU Kalibrasyon Haritası Başarıyla Güncellendi!")
        c1, c2 = st.columns(2)
        c1.metric("Güncel Güç (HP)", f"{hesaplanmis_hp} HP", f"+{hesaplanmis_hp - st_hp} HP")
        c2.metric("Güncel Tork", f"{hesaplanmis_tork} Nm", f"+{hesaplanmis_tork - st_tork} Nm")
        
        if "Atmosferik" in motor_tipi and "Stage 3" in secilen_stage:
            st.warning("⚠️ **Mühendislik Notu:** Atmosferik motorlarda turbo olmadığı için Stage 3 yazılımlar mekanik modifikasyon gerektirir.")

elif sekme == "🛠️ Araç Sorunları & Çözüm Asistanı":
    st.markdown("### 🛠️ Araç Sorunları & Arıza Çözüm Asistanı")
    arac_sorun_metni = st.text_area("Araçtaki Şikayetiniz / Belirti:", placeholder="Örn: Araç trafikte hararet yaptı...", key="sorun_metin")
    
    if st.button("🔍 Sorunu Analiz Et ve Çözüm Öner", key="btn_sorun"):
        if not arac_sorun_metni:
            st.warning("Lütfen bir şikayet veya sorun belirtin.")
        else:
            st.session_state.islem_sayisi += 1
            cozum_aciklamasi, tahmini_maliyet = arac_sorun_analizi_yap(arac_sorun_metni)
            log_kaydet("Sorun Asistanı", f"Şikayet: {arac_sorun_metni}", "Analiz Edildi")
            st.success("✅ Sorun Analizi Tamamlandı!")
            st.markdown(f"""
                <div class="info-box">
                    <h3 style="color: #60a5fa; margin-top:0;">💡 Olası Neden & Çözüm Önerisi</h3>
                    <p>{cozum_aciklamasi}</p>
                    <hr style="border-color: #374151;">
                    <p><b>🛠️ Tahmini Tamir/Parça Maliyeti:</b> <span style="color: #f87171; font-weight: bold;">{tahmini_maliyet}</span></p>
                </div>
            """, unsafe_allow_html=True)

elif sekme == "🔊 Araç İçi Ses & NVH Arıza Teşhisi":
    st.markdown("### 🔊 Araç İçi Ses & NVH (Gürültü, Titreşim, Sertlik) Arıza Teşhisi")
    ses_tipi = st.selectbox("Gelen Sesin Karakteristiği:", [
        "Tekerlek bilyasından gelen uğultu (hızlandıkça artan)",
        "Ön takımdan gelen tıkırtı / boşluk sesi (çukurlarda)",
        "Direksiyonu çevirince gelenurtlama / sürtünme sesi",
        "Frene basınca gelen balata ıslığı / metal sürtünme sesi",
        "Kasislerden geçerken 'gıcırtı' (salıncak burçları)"
    ])
    if st.button("🔊 Ses Kaynağını Teşhis Et"):
        st.session_state.islem_sayisi += 1
        st.success("NVH Teşhisi Tamamlandı!")
        st.info(f"Seçilen belirti ('{ses_tipi}') genellikle ilgili mekanik parça aşınmasına işaret eder. Servis kontrolü önerilir.")

elif sekme == "🏷️ Yedek Parça Orijinal/Yan Sanayi Kıyas":
    st.markdown("### 🏷️ Yedek Parça Orijinal vs Yan Sanayi Maliyet/Kalite Kıyası")
    parca_adi = st.text_input("Parça Adı:", "Örn: Ön Fren Balatası ve Diski")
    if st.button("Kıyasla"):
        st.session_state.islem_sayisi += 1
        st.markdown("""
        - **Orijinal (OEM):** Yüksek maliyet, kusursuz uyum ve uzun garanti süresi.
        - **Kaliteli Yan Sanayi (Aftermarket):** Fiyat/performans odaklı, genellikle OEM üreticisi tarafından üretilir.
        """)

elif sekme == "📋 Tramer & Parça Maliyet Simülatörü":
    st.markdown("### 📋 Tramer Hasar Kaydı ve Parça Maliyet Simülatörü")
    tramer_parca = st.multiselect("Hasar Gören Parçaları Seçin:", ["Ön Tampon", "Sol Çamurluk", "Kaput", "Far Grubu", "Radyatör"])
    if st.button("Maliyet Hesabını Gör"):
        st.session_state.islem_sayisi += 1
        tutar = len(tramer_parca) * 8500
        st.success(f"Tahmini Parça ve İşçilik Tramer Toplamı: {tutar:,} ₺".replace(",", "."))

elif sekme == "💰 Galeri Al-Sat & Kar Hesaplayıcı":
    st.markdown("### 💰 Galeri Alım-Satım ve Net Kar Hesaplayıcı")
    alis_fiyat = st.number_input("Aracın Alış Fiyatı (₺):", min_value=0.0, value=500000.0, step=10000.0)
    masraf_fiyat = st.number_input("Yapılan Masraflar (Boya, Bakım, Kuaför) (₺):", min_value=0.0, value=15000.0, step=1000.0)
    satis_fiyat = st.number_input("Planlanan Satış Fiyatı (₺):", min_value=0.0, value=580000.0, step=10000.0)
    if st.button("Kar Hesapla"):
        st.session_state.islem_sayisi += 1
        net_kar = satis_fiyat - (alis_fiyat + masraf_fiyat)
        st.metric("Net Kar", f"{net_kar:,.2f} ₺".replace(",", "."))

elif sekme == "📜 Noter & Devir Masraf Hesaplayıcı":
    st.markdown("### 📜 Noter Araç Satış ve Devir Masrafı Hesaplayıcı")
    noter_yil = st.number_input("Araç Yaşı:", min_value=0, max_value=50, value=5)
    if st.button("Noter Masrafını Hesapla"):
        st.session_state.islem_sayisi += 1
        st.success("2026 yılı güncel noter araç devir ve tescil masrafı ortalama 3.500₺ - 4.500₺ aralığındadır.")

elif sekme == "🔧 OBD-II Arıza Kodu (DTC) Sözlüğü":
    st.markdown("### 🔧 OBD-II Arıza Kodu (DTC) Sözlüğü")
    dtc_kod = st.text_input("Arıza Kodunu Girin (örn: P0300):", "P0300")
    if st.button("Kodu Sorgula"):
        st.session_state.islem_sayisi += 1
        st.info(f"**{dtc_kod.upper()}:** Rastgele / Çoklu silindir ateşleme hatası (Random/Multiple Cylinder Misfire Detected). Buji ve bobinlerinizi kontrol edin.")

elif sekme == "🏎️ Performans & 0-100 Simülatörü":
    st.markdown("### 🏎️ Araç Performans & 0-100 KM/h Simülatörü")
    p_hp = st.number_input("Araç Beygir Gücü (HP):", min_value=50, max_value=1500, value=150)
    p_agirlik = st.number_input("Araç Ağırlığı (kg):", min_value=600, max_value=3000, value=1350)
    if st.button("0-100 Hızlanma Tahmini Yap"):
        st.session_state.islem_sayisi += 1
        tahmini_sure = round(float(p_agirlik) / float(p_hp) * 0.065, 2)
        st.success(f"Tahmini 0-100 km/s Hızlanma Süresi: **{tahmini_sure} Saniye**")

elif sekme == "📂 Kayıtlı Arşiv & Raporlar":
    st.markdown("### 📂 Kayıtlı Raporlar ve Veritabanı Arşivi")
    try:
        conn = sqlite3.connect("autolab_pro.db", timeout=10)
        df_raporlar = pd.read_sql_query("SELECT * FROM raporlar ORDER BY id DESC", conn)
        conn.close()
        if not df_raporlar.empty:
            st.dataframe(df_raporlar, use_container_width=True)
        else:
            st.info("Henüz veritabanında kayıtlı rapor bulunmuyor.")
    except Exception as e:
        st.error(f"Arşiv yüklenirken hata oluştu: {e}")

elif sekme == "🛠️ Yedek Parça & İşçilik Teklifi":
    st.markdown("### 🛠️ Servis Yedek Parça & İşçilik Teklif Formu")
    st.text_input("Müşteri Adı Soyadı:")
    st.text_area("Yapılacak İşlemler / Parçalar:")
    if st.button("Teklif Oluştur"):
        st.session_state.islem_sayisi += 1
        st.success("Servis teklif formu başarıyla hazırlandı.")

elif sekme == "🅿️ Galeri Stok & Envanter":
    st.markdown("### 🅿️ Galeri Stok ve Envanter Yönetimi")
    st_plaka = st.text_input("Araç Plakası (Stok):")
    st_model = st.text_input("Model Bilgisi (Stok):")
    st_alis = st.number_input("Alış Fiyatı (₺):", min_value=0.0, value=400000.0)
    if st.button("Stoğa Ekle"):
        try:
            conn = sqlite3.connect("autolab_pro.db", timeout=10)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO galeri_stok (plaka, model, alis_fiyati, alis_tarihi, durum) VALUES (?, ?, ?, ?, ?)", 
                           (st_plaka, st_model, st_alis, datetime.now().strftime('%d.%m.%Y'), "Aktif Stok"))
            conn.commit()
            conn.close()
            st.success("Araç başarıyla galeri stoğuna eklendi!")
        except Exception as e:
            st.error(f"Hata: {e}")

elif sekme == "⛽ Akaryakıt & Seyahat Maliyeti":
    st.markdown("### ⛽ Akaryakıt & Seyahat Maliyeti Hesaplayıcı")
    mesafe = st.number_input("Mesafe (Kilometre):", min_value=1, value=450)
    tuketim = st.number_input("100 KM'de Ortalama Tüketim (Litre):", min_value=1.0, value=6.5)
    benzin_fiyat = st.number_input("Litre Fiyatı (₺):", min_value=1.0, value=43.50)
    if st.button("Seyahat Maliyetini Hesapla"):
        st.session_state.islem_sayisi += 1
        toplam_tutar = (mesafe / 100.0) * tuketim * benzin_fiyat
        st.success(f"Tahmini Toplam Seyahat Maliyeti: **{toplam_tutar:,.2f} ₺**".replace(",", "."))

elif sekme == "📝 Plaka & Hasar Not Defteri":
    st.markdown("### 📝 Plaka & Hasar Not Defteri")
    not_plaka = st.text_input("Not Alınacak Plaka:")
    not_detay = st.text_area("Hasar / Eksper Notları:")
    if st.button("Notu Kaydet"):
        st.session_state.islem_sayisi += 1
        log_kaydet("Not Defteri", f"Plaka: {not_plaka}", not_detay)
        st.success("Not başarıyla kaydedildi!")

elif sekme == "⏱️ Periyodik Bakım Takibi":
    st.markdown("### ⏱️ Periyodik Bakım Takibi")
    son_bakim_km = st.number_input("Son Bakım Kilometresi:", min_value=0, value=60000)
    guncel_km_takip = st.number_input("Aracın Şu Anki Kilometresi:", min_value=0, value=68000)
    if st.button("Bakım Durumunu Hesapla"):
        st.session_state.islem_sayisi += 1
        kalan_km = (son_bakim_km + 10000) - guncel_km_takip
        if kalan_km > 0:
            st.info(f"Sonraki bakıma kalan mesafe: **{kalan_km:,} KM**. Durum Normal.")
        else:
            st.warning(f"⚠️ Bakım kilometresini **{abs(kalan_km):,} KM** geçmiş bulunuyorsunuz! Acil bakım önerilir.")
