import os
import sqlite3
from datetime import datetime
import requests
import pandas as pd
import qrcode
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
import streamlit as st

st.set_page_config(
    page_title='Auto Lab Pro - Ultimate Engineering & Expertise Studio',
    page_icon='🚗',
    layout='wide',
)

WHATSAPP_NUMARASI = '905510305139'
DISCORD_WEBHOOK_URL = 'BURAYA_DISCORD_WEBHOOK_LINKINI_YAPISTIR'


def discord_bildirim_gonder(mesaj_baslik, detay_icerik):
  if (
      not DISCORD_WEBHOOK_URL
      or 'BURAYA_DISCORD' in DISCORD_WEBHOOK_URL
      or not DISCORD_WEBHOOK_URL.startswith('https://')
  ):
    return
  embed_data = {
      'username': 'Auto Lab Pro Bot',
      'embeds': [{
          'title': f'🚨 {mesaj_baslik}',
          'description': detay_icerik,
          'color': 3447003,
          'timestamp': datetime.utcnow().isoformat(),
          'footer': {'text': 'Auto Lab Pro Ekspertiz ve Güvenlik Modülü'},
      }],
  }
  try:
    requests.post(DISCORD_WEBHOOK_URL, json=embed_data, timeout=3)
  except Exception as e:
    print(f'Discord bildirim hatası: {e}')


st.markdown(
    f"""
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
""",
    unsafe_allow_html=True,
)


def init_db():
  try:
    conn = sqlite3.connect('autolab_pro.db', timeout=10)
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
    conn.commit()
    conn.close()
  except Exception as e:
    print(f'Veritabanı hatası: {e}')


init_db()


def qr_olustur(veri_metni, dosya_adi='qr_temp.png'):
  try:
    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr.add_data(veri_metni)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    img.save(dosya_adi)
    return dosya_adi
  except Exception as e:
    print(f'QR oluşturma hatası: {e}')
    return None


def pdf_ekspertiz_raporu_olustur(
    dosya_adi, plaka, marka_model, yil, km, sema_dict, sonuc, tavsiye
):
  doc = SimpleDocTemplate(
      dosya_adi,
      pagesize=A4,
      rightMargin=30,
      leftMargin=30,
      topMargin=30,
      bottomMargin=30,
  )
  elements = []
  styles = getSampleStyleSheet()

  title_style = ParagraphStyle(
      'TitleStyle',
      parent=styles['Heading1'],
      fontSize=15,
      textColor=colors.HexColor('#1e3a8a'),
      alignment=1,
      spaceAfter=6,
  )
  sub_title_style = ParagraphStyle(
      'SubTitleStyle',
      parent=styles['Heading2'],
      fontSize=8.5,
      textColor=colors.HexColor('#4b5563'),
      alignment=1,
      spaceAfter=10,
  )
  section_heading = ParagraphStyle(
      'SectionHeading',
      parent=styles['Heading3'],
      fontSize=10,
      textColor=colors.HexColor('#1d4ed8'),
      spaceBefore=6,
      spaceAfter=4,
  )

  qr_path = qr_olustur(
      f'Auto Lab Pro Doğrulanmış Rapor - Plaka: {plaka} - Model: {marka_model}'
  )

  elements.append(
      Paragraph(
          '🚗 AUTO LAB PRO - KURUMSAL DİNAMİK EKSPERTİZ RAPORU', title_style
      )
  )
  elements.append(
      Paragraph(
          f'<b>Rapor Tarihi:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}'
          f' &nbsp;&nbsp;|&nbsp;&nbsp; <b>Plaka:</b> {plaka.upper()}',
          sub_title_style,
      )
  )

  elements.append(Paragraph('1. Araç Kimlik ve Genel Bilgileri', section_heading))
  data_arac = [
      ['Araç Marka / Model:', marka_model, 'Model Yılı:', str(yil)],
      [
          'Güncel Kilometre:',
          f'{int(km):,} KM'.replace(',', '.'),
          'Genel Sonuç:',
          sonuc,
      ],
  ]
  t_arac = Table(data_arac, colWidths=[110, 160, 90, 175])
  t_arac.setStyle(
      TableStyle([
          ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e5edff')),
          ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#e5edff')),
          ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
          ('PADDING', (0, 0), (-1, -1), 4),
          ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
          ('FONTSIZE', (0, 0), (-1, -1), 8),
      ])
  )
  elements.append(t_arac)
  elements.append(Spacer(1, 6))

  elements.append(
      Paragraph('2. Kuş Bakışı Kaporta Durum Şeması', section_heading)
  )
  data_sema = [
      [
          'ÖN BÖLÜM',
          f"Ön Kaput: {sema_dict.get('Ön Kaput', 'Orijinal')}",
          f"Tavan: {sema_dict.get('Tavan', 'Orijinal')}",
      ],
      [
          'YAN KISIM 1',
          f"Sol Ön Çamurluk: {sema_dict.get('Sol Ön Çamurluk', 'Orijinal')}",
          f"Sağ Ön Çamurluk: {sema_dict.get('Sağ Ön Çamurluk', 'Orijinal')}",
      ],
      [
          'YAN KISIM 2',
          f"Sol Ön Kapı: {sema_dict.get('Sol Ön Kapı', 'Orijinal')}",
          f"Sağ Ön Kapı: {sema_dict.get('Sağ Ön Kapı', 'Orijinal')}",
      ],
      [
          'ARKALAR',
          f"Sol Arka Çamurluk: {sema_dict.get('Sol Arka Çamurluk', 'Orijinal')}",
          f"Sağ Arka Çamurluk: {sema_dict.get('Sağ Arka Çamurluk', 'Orijinal')}",
      ],
      [
          'ARKA BÖLÜM',
          f"Bagaj Kapağı: {sema_dict.get('Bagaj Kapağı', 'Orijinal')}",
          f"Şase/Podye: {sema_dict.get('Şase ve Podye', 'Orijinal')}",
      ],
  ]
  t_sema = Table(data_sema, colWidths=[100, 217, 218])
  t_sema.setStyle(
      TableStyle([
          ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e5edff')),
          ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
          ('PADDING', (0, 0), (-1, -1), 4),
          ('FONTSIZE', (0, 0), (-1, -1), 8),
          ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
      ])
  )
  elements.append(t_sema)
  elements.append(Spacer(1, 6))

  elements.append(
      Paragraph('3. Yapay Zeka Uzman Tavsiyesi ve Risk Analizi', section_heading)
  )
  data_mekanik = [['Uzman Tavsiyesi & Risk:', tavsiye]]
  t_mek = Table(data_mekanik, colWidths=[135, 400])
  t_mek.setStyle(
      TableStyle([
          ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
          ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
          ('PADDING', (0, 0), (-1, -1), 5),
          ('FONTSIZE', (0, 0), (-1, -1), 8),
      ])
  )
  elements.append(t_mek)
  elements.append(Spacer(1, 10))

  if qr_path and os.path.exists(qr_path):
    elements.append(RLImage(qr_path, width=60, height=60))

  doc.build(elements)
  return dosya_adi


if 'logged_in' not in st.session_state:
  st.session_state.logged_in = False
if 'islem_sayisi' not in st.session_state:
  st.session_state.islem_sayisi = 0

UCRETSIZ_HAK_SINIRI = 25
PREMIUM_HAK_SAYISI = 250

toplam_izin_verilen = (
    PREMIUM_HAK_SAYISI if st.session_state.logged_in else UCRETSIZ_HAK_SINIRI
)
if (
    st.session_state.islem_sayisi >= toplam_izin_verilen
    and not st.session_state.logged_in
):
  st.markdown(
      """
        <div style="text-align: center; padding: 40px; background: #111827; border-radius: 20px; border: 1px solid #374151; margin-top: 40px;">
            <h1 style="color: #f87171; margin-bottom: 10px;">⚠️ 25 İşlem Hakkınız Doldu!</h1>
            <p style="color: #9ca3af;">Uygulamayı kesintisiz kullanmaya devam etmek için sol üstteki WhatsApp butonundan şifrenizi alabilirsiniz.</p>
        </div>
    """,
      unsafe_allow_html=True,
  )
  girilen_sifre = st.text_input(
      '🔑 Size Özel Erişim Şifresi:', type='password'
  )
  if st.button('Sisteme Giriş Yap', type='primary', use_container_width=True):
    if girilen_sifre in ['autolab2026', 'pro9955', 'vip-oto-sifre']:
      st.session_state.logged_in = True
      st.session_state.islem_sayisi = 0
      st.success('Giriş başarılı!')
      discord_bildirim_gonder(
          'VIP Giriş Yapıldı',
          'Bir kullanıcı VIP şifre ile sisteme giriş sağladı.',
      )
      st.rerun()
    else:
      st.error('Hatalı şifre!')
  st.stop()

st.markdown(
    """
    <style>
    .main { background-color: #0b0f19; }
    .stApp { background-color: #0b0f19; color: #f3f4f6; }
    .hero-card {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        border: 1px solid #374151; padding: 25px; border-radius: 20px;
        text-align: center; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3); margin-bottom: 20px;
    }
    .hero-title { color: #60a5fa; font-size: 32px; font-weight: 900; margin-bottom: 5px; }
    </style>
    <div class="hero-card">
        <div class="hero-title">🚗 AUTO LAB PRO - ULTIMATE EDITION</div>
        <div style="color: #38bdf8; font-size: 16px;">Kurumsal Ekspertiz, Şema Analizi ve Discord Bildirim Merkezi</div>
    </div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
  st.markdown('### 📊 Kullanım Durumu')
  kalan_hak = (
      PREMIUM_HAK_SAYISI if st.session_state.logged_in else UCRETSIZ_HAK_SINIRI
  ) - st.session_state.islem_sayisi
  st.write(f'Kalan İşlem Hakkı: {max(0, kalan_hak)}')
  if st.session_state.logged_in:
    st.success('🔓 VIP Üye Modu')
    if st.button('Oturumu Kapat'):
      st.session_state.logged_in = False
      st.session_state.islem_sayisi = 0
      st.rerun()
  st.divider()

sekme = st.selectbox(
    'Auto Lab Ana Menü:',
    [
        '🔍 Ekspertiz Şeması & PDF Rapor Oluştur',
        '📋 Kayıtlı Raporlar Arşivi',
    ],
)

if 'Ekspertiz Şeması' in sekme:
  st.subheader('🔍 İnteraktif Kaporta Ekspertiz ve PDF Rapor Stüdyosu')

  col1, col2 = st.columns(2)
  with col1:
    plaka = st.text_input('Araç Plakası:', '34ABC34')
    marka_model = st.text_input('Marka / Model:', 'Honda Civic 1.5 VTEC')
  with col2:
    yil = st.number_input('Model Yılı:', 1995, 2026, 2022)
    km = st.number_input('Kilometre:', 0, 500000, 35000)

  st.markdown('---')
  st.markdown('### 🛠️ Parça Bazlı Kaporta / Boya Durumları')

  parcalar = [
      'Ön Kaput',
      'Tavan',
      'Sol Ön Çamurluk',
      'Sağ Ön Çamurluk',
      'Sol Ön Kapı',
      'Sağ Ön Kapı',
      'Sol Arka Kapı',
      'Sağ Arka Kapı',
      'Sol Arka Çamurluk',
      'Sağ Arka Çamurluk',
      'Bagaj Kapağı',
      'Şase ve Podye',
  ]
  secenekler = [
      'Orijinal',
      'Boyalı',
      'Lokal Boyalı',
      'Değişen',
      'Sök-Tak / Ayar',
  ]

  sema_dict = {}
  cols = st.columns(3)
  for i, parca in enumerate(parcalar):
    with cols[i % 3]:
      sema_dict[parca] = st.selectbox(f'{parca}:', secenekler, key=f'p_{i}')

  st.markdown('---')
  if st.button(
      '🚀 Ekspertiz Analizini Tamamla ve PDF Rapor Üret',
      type='primary',
      use_container_width=True,
  ):
    st.session_state.islem_sayisi += 1

    # Basit risk değerlendirmesi
    risk_durumu = (
        '⚠️ Şase/Podye İşlemli veya Değişen Parça Var!'
        if 'Değişen' in list(sema_dict.values())
        or 'Şase ve Podye İşlemli' in sema_dict.values()
        else '🔥 Hatasız / Temiz Kondisyon. Alınabilir.'
    )

    pdf_dosya = f'Ekspertiz_Raporu_{plaka}.pdf'
    pdf_ekspertiz_raporu_olustur(
        pdf_dosya,
        plaka,
        marka_model,
        yil,
        km,
        sema_dict,
        'Onaylandı',
        risk_durumu,
    )

    # Veritabanına kaydet
    try:
      conn = sqlite3.connect('autolab_pro.db', timeout=10)
      cursor = conn.cursor()
      cursor.execute(
          """
                INSERT INTO raporlar (tarih, plaka, model, yil, km, sonuc, tavsiye)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
          (
              datetime.now().strftime('%d.%m.%Y %H:%M'),
              plaka,
              marka_model,
              yil,
              km,
              'Onaylandı',
              risk_durumu,
          ),
      )
      conn.commit()
      conn.close()
    except Exception as e:
      print(f'DB kayıt hatası: {e}')

    # Discord bildirimi gönder
    discord_bildirim_gonder(
        'Yeni Kurumsal Ekspertiz Raporu Hazırlandı!',
        f'**Plaka:** {plaka}\n**Model:** {marka_model}\n**Analiz Sonucu:**'
        f' {risk_durumu}',
    )

    st.success(
        'Rapor başarıyla oluşturuldu ve veritabanına işlendi! Discord'
        ' bildirimi gönderildi.'
    )

    with open(pdf_dosya, 'rb') as f:
      st.download_button(
          label='📥 Resmi PDF Ekspertiz Raporunu İndir',
          data=f,
          file_name=pdf_dosya,
          mime='application/pdf',
      )

else:
  st.subheader('📋 Kayıtlı Raporlar Arşivi')
  try:
    conn = sqlite3.connect('autolab_pro.db')
    df = pd.read_sql_query('SELECT * FROM raporlar', conn)
    conn.close()
    if not df.empty:
      st.dataframe(df, use_container_width=True)
    else:
      st.info('Henüz kayıtlı rapor bulunmuyor.')
  except Exception as e:
    st.error(f'Arşiv yüklenirken hata oluştu: {e}')
