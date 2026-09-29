import hashlib
import csv
import datetime
import io
import pandas as pd
import requests
import sqlite3
import streamlit as st

# Streamlit Sayfa Yapılandırması
st.set_page_config(
    page_title="AUTO-LAB Pro",
    page_icon="🚗",
    layout="wide",
)

# --- ÖZEL MODERN CSS VE KAYAN DUYURU ANİMASYONU ---
st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        border-color: #ff4b4b;
        color: #ff4b4b;
    }
    
    @keyframes slideDown {
        0% {
            transform: translateY(-50px);
            opacity: 0;
        }
        100% {
            transform: translateY(0);
            opacity: 1;
        }
    }

    .announcement-banner {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color: white;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 15px;
        animation: slideDown 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        border-left: 6px solid #60a5fa;
        font-size: 16px;
    }
    
    .announcement-icon {
        font-size: 24px;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- ARKAPLAN AYARLARI (Güvenli st.secrets Kontrolü) ---
DEFAULT_WEBHOOK = "https://discord.com/api/webhooks/1548444040037662790/Yo7pYhJbWfSqzjWPVuwGrpQpuGlUYJO4uVIcA3ZRI4zSupvYNsu6m62BIZwDxFaRyDXl"
try:
  DISCORD_WEBHOOK_URL = st.secrets.get("DISCORD_WEBHOOK_URL", DEFAULT_WEBHOOK)
except Exception:
  DISCORD_WEBHOOK_URL = DEFAULT_WEBHOOK

WHATSAPP_NUMARASI = "905510305139"


def sifre_hashle(sifre):
  """Şifreyi SHA-256 algoritması ile güvenli bir şekilde hash'ler."""
  return hashlib.sha256(sifre.encode("utf-8")).hexdigest()


def discorda_mesaj_gonder(mesaj):
  """Arka planda Discord kanalına webhook ile gizli bildirim gönderir."""
  if not DISCORD_WEBHOOK_URL or not DISCORD_WEBHOOK_URL.startswith("http"):
    return
  try:
    payload = {"content": mesaj}
    requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
  except Exception as e:
    print(f"Discord mesajı gönderilemedi: {e}")


def giris_kaydi_ekle(kullanici_adi, islem_tipi):
  """Kullanıcının giriş/işlem zamanını veritabanına kaydeder."""
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


# Session State Tanımlamaları
if "aktif_kullanici" not in st.session_state:
  st.session_state.aktif_kullanici = None
if "giris_yapildi" not in st.session_state:
  st.session_state.giris_yapildi = False
if "sifre_goster" not in st.session_state:
  st.session_state.sifre_goster = False
if "is_admin" not in st.session_state:
  st.session_state.is_admin = False
if "islem_hakki" not in st.session_state:
  st.session_state.islem_hakki = 20
if "kilitli_mi" not in st.session_state:
  st.session_state.kilitli_mi = False

# Veritabanı ve Tabloları Güvenceye Alma
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

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND"
        " name='kullanicilar'"
    )
    tablo_varmi = cursor.fetchone()

    if not tablo_varmi:
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
    else:
      cursor.execute("PRAGMA table_info(kullanicilar)")
      sutunlar = [sutun[1] for sutun in cursor.fetchall()]
      if "is_banned" not in sutunlar:
        cursor.execute(
            "ALTER TABLE kullanicilar ADD COLUMN is_banned INTEGER DEFAULT 0"
        )
      if "islem_hakki" not in sutunlar:
        cursor.execute(
            "ALTER TABLE kullanicilar ADD COLUMN islem_hakki INTEGER DEFAULT 20"
        )

    conn.commit()
except Exception:
  pass

# -------------------------------------------------------------
# SIDEBAR - DESTEK
# -------------------------------------------------------------
st.sidebar.title("🛠️ Destek & İletişim")
wa_mesaj = (
    "Selam, AUTO-LAB Pro uygulaması şifremi unuttum. Yardımcı olur musun?"
)
wa_link = f"https://wa.me/{WHATSAPP_NUMARASI}?text={requests.utils.quote(wa_mesaj)}"
st.sidebar.markdown(
    f'<a href="{wa_link}" target="_blank"><button'
    ' style="background-color:#25D366; color:white; border:none;'
    " padding:10px 15px; border-radius:8px; font-weight:bold; cursor:pointer;"
    ' width:100%;">💬 WhatsApp ile Şifre İste</button></a>',
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")

# -------------------------------------------------------------
# GİRİŞ / KAYIT EKRANI
# -------------------------------------------------------------
if not st.session_state.giris_yapildi:
  st.title("🚗 AUTO-LAB Pro - Giriş / Kayıt Paneli")
  tab_giris, tab_kayit = st.tabs(["🔑 Giriş Yap", "📝 Yeni Hesap Oluştur"])

  with tab_giris:
    st.subheader("Hesabınıza Giriş Yapın")
    g_kullanici = st.text_input("Kullanıcı Adı:", key="giris_kadi")

    col_sifre_input, col_sifre_btn = st.columns([4, 1])
    with col_sifre_input:
      g_sifre = st.text_input(
          "Şifre:",
          type="password" if not st.session_state.sifre_goster else "default",
          key="giris_sifre",
      )
    with col_sifre_btn:
      st.write("")
      st.write("")
      if st.button(
          "👁 Göster / Gizle", key="btn_toggle_giris", use_container_width=True
      ):
        st.session_state.sifre_goster = not st.session_state.sifre_goster
        st.rerun()

    if st.button("Giriş Yap", use_container_width=True):
      girilen_kadi = g_kullanici.strip()
      girilen_sifre = g_sifre.strip()

      if not girilen_kadi:
        st.error("Lütfen kullanıcı adı alanını doldurun!")
      elif girilen_kadi.upper() in ["ADMIN", "ADMİN"] and girilen_sifre in [
          "ADMİN",
          "ADMIN",
      ]:
        st.session_state.aktif_kullanici = "ADMIN"
        st.session_state.is_admin = True
        st.session_state.giris_yapildi = True
        st.session_state.islem_hakki = 999999
        giris_kaydi_ekle("ADMIN", "Admin Girişi Yaptı")
        discorda_mesaj_gonder(
            "🛡 **Admin (ADMİN)** sisteme başarılı bir şekilde giriş yaptı!"
        )
        st.success("Admin olarak giriş yapıldı!")
        st.rerun()
      else:
        if not girilen_sifre:
          st.error("Lütfen şifre alanını doldurun!")
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
                (
                    db_ad,
                    db_soyad,
                    db_eposta,
                    db_eposta_sifre,
                    db_sifre,
                    is_banned,
                    db_hak,
                ) = row

                if is_banned == 1:
                  st.error("⚠️ Bu hesap yönetici tarafından yasaklanmıştır!")
                else:
                  st.session_state.aktif_kullanici = girilen_kadi
                  st.session_state.is_admin = False
                  st.session_state.giris_yapildi = True
                  st.session_state.islem_hakki = (
                      db_hak if db_hak is not None else 20
                  )
                  st.session_state.kilitli_mi = False

                  giris_kaydi_ekle(girilen_kadi, "Sisteme Giriş Yaptı")
                  discorda_mesaj_gonder(
                      f"🔑 **Kullanıcı Sisteme Giriş Yaptı!**\n• **Ad Soyad:**"
                      f" {db_ad} {db_soyad}\n• **Kullanıcı Adı:**"
                      f" `{girilen_kadi}`"
                  )

                  st.success("Giriş başarılı!")
                  st.rerun()
              else:
                discorda_mesaj_gonder(
                    f"⚠️ **Hatalı Giriş Denemesi!**\n• Kullanıcı Adı:"
                    f" `{girilen_kadi}`"
                )
                st.error("Kullanıcı adı veya şifre hatalı!")
          except Exception as e:
            st.error(f"Hata: {e}")

  with tab_kayit:
    st.subheader("📝 Yeni Kullanıcı Kaydı")
    k_ad = st.text_input("Ad:")
    k_soyad = st.text_input("Soyad:")
    k_eposta = st.text_input("E-posta Adresi:")
    k_eposta_sifre = st.text_input("E-posta Şifresi:", type="password")
    k_kadi = st.text_input("Kullanıcı Adı:")
    k_sifre = st.text_input("Uygulama Giriş Şifresi:", type="password")

    if st.button("Kayıt Ol", use_container_width=True):
      if not k_kadi.strip() or not k_sifre.strip():
        st.error("Kullanıcı adı ve şifre zorunludur!")
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

          giris_kaydi_ekle(k_kadi.strip(), "Yeni Kayıt Oldu")
          discorda_mesaj_gonder(
              f"📝 **Yeni Kullanıcı Kaydı Oluşturuldu!**\n• Kullanıcı Adı:"
              f" `{k_kadi.strip()}`"
          )

          st.success("Kayıt başarılı! Giriş yapabilirsiniz.")
        except sqlite3.IntegrityError:
          st.error("Bu kullanıcı adı zaten alınmış.")
        except Exception as e:
          st.error(f"Hata: {e}")

# -------------------------------------------------------------
# ANA UYGULAMA
# -------------------------------------------------------------
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
                    <div class="announcement-icon">📢</div>
                    <div>
                        <strong>Yeni Yönetici Bildirimi:</strong><br>
                        {son_duyuru[0]}
                    </div>
                </div>
            """,
            unsafe_allow_html=True,
        )
  except Exception:
    pass

  if not st.session_state.is_admin:
    try:
      with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT islem_hakki FROM kullanicilar WHERE kullanici_adi = ?",
            (st.session_state.aktif_kullanici,),
        )
        hak_row = cursor.fetchone()
        if hak_row:
          st.session_state.islem_hakki = hak_row[0]
    except Exception:
      pass

  col_baslik1, col_baslik2 = st.columns([4, 1])
  with col_baslik1:
    st.title("🚗 AUTO-LAB Pro")
    st.markdown(f"Hoş geldin, **{st.session_state.aktif_kullanici}**!")
    if not st.session_state.is_admin:
      st.info(f"⚡ Kalan İşlem Hakkınız: **{st.session_state.islem_hakki}**")
  with col_baslik2:
    st.write("")
    if st.button("🚪 Çıkış Yap", use_container_width=True):
      giris_kaydi_ekle(st.session_state.aktif_kullanici, "Çıkış Yaptı")
      st.session_state.giris_yapildi = False
      st.session_state.aktif_kullanici = None
      st.session_state.is_admin = False
      st.session_state.islem_hakki = 20
      st.session_state.kilitli_mi = False
      st.rerun()

  if (
      not st.session_state.is_admin and st.session_state.islem_hakki <= 0
  ) or st.session_state.kilitli_mi:
    st.session_state.kilitli_mi = True

    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #b91c1c, #7f1d1d); color: white; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 20px; box-shadow: 0 10px 25px rgba(185, 28, 28, 0.4);">
            <h2 style="margin: 0; color: white;">🔒 AUTO-LAB GÜVENLİK KİLİDİ AKTİF</h2>
            <p style="margin-top: 8px; font-size: 16px;">Sistem işlem sınırına ulaşıldı. Laboratuvara devam etmek için şifreyi gir ve haklarını yenile!</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_kilit1, col_kilit2, col_kilit3 = st.columns([1, 2, 1])
    with col_kilit2:
      kilit_sifre = st.text_input(
          "AUTO-LAB Kilit Şifresi:",
          type="password",
          key="autolab_kilit_input",
      )
      if st.button(
          "🚀 AUTO-LAB Kilidini Aç ve +200 Hak Al", use_container_width=True
      ):
        if kilit_sifre.strip() == "AUTOLAB":
          st.session_state.islem_hakki = 200
          st.session_state.kilitli_mi = False
          try:
            with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
              cursor = conn.cursor()
              cursor.execute(
                  "UPDATE kullanicilar SET islem_hakki = ? WHERE"
                  " kullanici_adi = ?",
                  (200, st.session_state.aktif_kullanici),
              )
              conn.commit()
          except Exception:
            pass

          giris_kaydi_ekle(
              st.session_state.aktif_kullanici,
              "AUTO-LAB Kilidini Açtı (+200 Hak)",
          )
          discorda_mesaj_gonder(
              f"🔓 **AUTO-LAB Kilidi Açıldı!**\n• Kullanıcı:"
              f" `{st.session_state.aktif_kullanici}` sistemi devam ettirdi."
          )
          st.success(
              "Doğrulama başarılı! AUTO-LAB ana sistemine tekrar hoş geldin."
          )
          st.rerun()
        else:
          discorda_mesaj_gonder(
              f"⚠️ **AUTO-LAB Hatalı Kilit Açma Denemesi!**\n• Kullanıcı:"
              f" `{st.session_state.aktif_kullanici}`"
          )
          st.error("Hatalı şifre! Laboratuvar kilidi açılamadı.")

  else:
    st.sidebar.title("📌 Menü")
    menu_listesi = [
        "🔍 Arama Motoru",
        "Şifremi Güncelle (Parola Değiştir)",
        "🛡️ Admin Sayfası",
    ]

    sekme = st.sidebar.radio("Gitmek İstediğiniz Bölüm:", menu_listesi)

    if sekme == "🔍 Arama Motoru":
      st.subheader("🔍 Sistem İçi Arama Motoru")
      arama_terimi = st.text_input(
          "Aranacak kelimeyi veya ifadeyi girin:",
          placeholder="Örn: Honda, Sistem...",
      )

      if st.button("Ara", use_container_width=True):
        if not arama_terimi.strip():
          st.warning("Lütfen aramak için bir şeyler yazın.")
        else:
          if not st.session_state.is_admin:
            st.session_state.islem_hakki -= 1
            try:
              with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE kullanicilar SET islem_hakki = islem_hakki - 1 WHERE"
                    " kullanici_adi = ?",
                    (st.session_state.aktif_kullanici,),
                )
                conn.commit()
            except Exception:
              pass

          st.info(f'"{arama_terimi}" için arama yapıldı.')
          arama_sorgusu = f"%{arama_terimi.strip()}%"
          toplam_sonuc = 0
          try:
            with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
              df_sonuc = pd.read_sql_query(
                  "SELECT ad, soyad, eposta, kullanici_adi FROM kullanicilar"
                  " WHERE ad LIKE ? OR soyad LIKE ? OR eposta LIKE ? OR"
                  " kullanici_adi LIKE ?",
                  conn,
                  params=(
                      arama_sorgusu,
                      arama_sorgusu,
                      arama_sorgusu,
                      arama_sorgusu,
                  ),
              )
              toplam_sonuc = len(df_sonuc)

              st.markdown("### 📊 Arama Sonuçları")
              if not df_sonuc.empty:
                st.dataframe(df_sonuc, use_container_width=True)
              else:
                st.write("Eşleşen kayıt bulunamadı.")

              cursor = conn.cursor()
              cursor.execute(
                  """
                        INSERT INTO arama_gecmisi (kullanici, aranan_kelime, bulunan_sonuc_sayisi)
                        VALUES (?, ?, ?)
                    """,
                  (
                      st.session_state.aktif_kullanici,
                      arama_terimi.strip(),
                      toplam_sonuc,
                  ),
              )
              conn.commit()
          except Exception as e:
            st.error(f"Arama hatası: {e}")

          if not st.session_state.is_admin and st.session_state.islem_hakki <= 0:
            st.rerun()

    elif sekme == "Şifremi Güncelle (Parola Değiştir)":
      st.subheader("⚙ Hesap Şifresini Güncelle")
      eski_sifre = st.text_input("Mevcut Şifreniz:", type="password")
      yeni_sifre_1 = st.text_input("Yeni Şifreniz:", type="password")
      yeni_sifre_2 = st.text_input("Yeni Şifreniz (Tekrar):", type="password")

      if st.button("Şifreyi Güncelle", use_container_width=True):
        if not eski_sifre or not yeni_sifre_1 or not yeni_sifre_2:
          st.error("Tüm alanları doldurun!")
        elif yeni_sifre_1 != yeni_sifre_2:
          st.error("Şifreler uyuşmuyor!")
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
                yeni_hashli_sifre = sifre_hashle(yeni_sifre_1)
                cursor.execute(
                    "UPDATE kullanicilar SET sifre = ? WHERE kullanici_adi ="
                    " ?",
                    (yeni_hashli_sifre, st.session_state.aktif_kullanici),
                )
                conn.commit()

                if not st.session_state.is_admin:
                  st.session_state.islem_hakki -= 1
                  cursor.execute(
                      "UPDATE kullanicilar SET islem_hakki = islem_hakki - 1 WHERE"
                      " kullanici_adi = ?",
                      (st.session_state.aktif_kullanici,),
                  )
                  conn.commit()

                giris_kaydi_ekle(
                    st.session_state.aktif_kullanici, "Şifresini Güncelledi"
                )
                st.success("Şifreniz güncellendi!")
              else:
                st.error("Mevcut şifre hatalı!")
          except Exception as e:
            st.error(f"Hata: {e}")

    elif sekme == "🛡️ Admin Sayfası":
      if not st.session_state.is_admin:
        st.warning(
            "⚠️ Bu alana sadece ADMIN yetkisi olan hesaplar erişebilir."
        )
        admin_giris_kodu = st.text_input(
            "Admin yetki kodu / şifresi:", type="password"
        )
        if st.button("Admin Olmaya Çalış", use_container_width=True):
          if admin_giris_kodu.strip() in ["ADMİN", "ADMIN"]:
            st.session_state.is_admin = True
            st.session_state.aktif_kullanici = "ADMIN"
            st.session_state.islem_hakki = 999999
            st.success("Admin yetkisi başarıyla alındı!")
            st.rerun()
          else:
            st.error("Geçersiz admin şifresi!")
      else:
        st.subheader("🛡️ Gelişmiş Admin Yönetim Paneli")
        if st.button("Admin Yetkisini Kapat", use_container_width=True):
          st.session_state.is_admin = False
          st.session_state.islem_hakki = 20
          st.rerun()

        tab_yonetim1, tab_yonetim2, tab_yonetim3 = st.tabs(
            ["👥 Kullanıcı Yönetimi & CSV", "📢 Duyurular", "🕒 Log Kayıtları"]
        )

        with tab_yonetim1:
          st.markdown("### 👥 Kayıtlı Kullanıcılar & İşlem Hakkı Yönetimi")
          try:
            with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
              df_kullanicilar = pd.read_sql_query(
                  "SELECT id, ad, soyad, eposta, kullanici_adi, is_banned,"
                  " islem_hakki, kayit_tarihi FROM kullanicilar",
                  conn,
              )
              if not df_kullanicilar.empty:
                st.dataframe(df_kullanicilar, use_container_width=True)

                csv_buffer = io.StringIO()
                df_kullanicilar.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="📥 Kullanıcı Listesini CSV Olarak İndir",
                    data=csv_buffer.getvalue(),
                    file_name="kullanici_listesi.csv",
                    mime="text/csv",
                )

                st.markdown("---")
                secilen_kadi = st.selectbox(
                    "İşlem Yapılacak Kullanıcı:",
                    df_kullanicilar["kullanici_adi"].tolist(),
                )

                st.markdown("#### ⚡ Kullanıcıya İşlem Hakkı Ver")
                eklenecek_hak = st.number_input(
                    "Eklenecek İşlem Hakkı Miktarı:",
                    min_value=1,
                    value=20,
                    step=1,
                )
                if st.button(
                    "Seçilen Kullanıcıya Hak Ver", use_container_width=True
                ):
                  cursor = conn.cursor()
                  cursor.execute(
                      "UPDATE kullanicilar SET islem_hakki = islem_hakki + ?"
                      " WHERE kullanici_adi = ?",
                      (eklenecek_hak, secilen_kadi),
                  )
                  conn.commit()
                  st.toast(
                      f"✅ '{secilen_kadi}' adlı kullanıcıya {eklenecek_hak} işlem"
                      " hakkı eklendi!",
                      icon="🚀",
                  )
                  st.rerun()

                st.markdown("---")
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                  if st.button(
                      "🔒 Seçilen Kullanıcıyı Banla / Aktif Yap",
                      use_container_width=True,
                  ):
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT is_banned FROM kullanicilar WHERE"
                        " kullanici_adi = ?",
                        (secilen_kadi,),
                    )
                    durum = cursor.fetchone()[0]
                    yeni_durum = 0 if durum == 1 else 1
                    cursor.execute(
                        "UPDATE kullanicilar SET is_banned = ? WHERE"
                        " kullanici_adi = ?",
                        (yeni_durum, secilen_kadi),
                    )
                    conn.commit()
                    st.toast(
                        f"🔒 '{secilen_kadi}' kullanıcısının ban durumu"
                        " değiştirildi!",
                        icon="⚠️",
                    )
                    st.rerun()

                with col_b2:
                  if (
                      st.button(
                          "🗑️ Seçilen Kullanıcıyı Sil",
                          type="primary",
                          use_container_width=True,
                      )
                      and secilen_kadi != "ADMIN"
                  ):
                    cursor = conn.cursor()
                    cursor.execute(
                        "DELETE FROM kullanicilar WHERE kullanici_adi = ?",
                        (secilen_kadi,),
                    )
                    conn.commit()
                    st.toast(
                        f"🗑️ '{secilen_kadi}' adlı kullanıcı silindi!",
                        icon="❌",
                    )
                    st.rerun()
              else:
                st.info("Kayıtlı başka kullanıcı yok.")
          except Exception as e:
            st.error(f"Hata: {e}")

        with tab_yonetim2:
          st.markdown("### 📢 Tüm Kullanıcılara Duyuru Gönder")
          yeni_duyuru_metni = st.text_input("Duyuru Mesajı:")
          if st.button("Duyuruyu Yayınla", use_container_width=True):
            if yeni_duyuru_metni.strip():
              try:
                with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
                  cursor = conn.cursor()
                  cursor.execute(
                      "INSERT INTO announcements (message) VALUES (?)",
                      (yeni_duyuru_metni.strip(),),
                  )
                  conn.commit()
                  st.success(
                      "Duyuru başarıyla yayınlandı! Kullanıcı ekranına kayarak"
                      " düşecektir."
                  )
              except Exception as e:
                st.error(f"Hata: {e}")
            else:
              st.warning("Lütfen bir duyuru metni yazın.")

        with tab_yonetim3:
          st.markdown("### 🕒 Sistem Giriş ve İşlem Logları")
          try:
            with sqlite3.connect("autolab_pro.db", timeout=10) as conn:
              df_loglar = pd.read_sql_query(
                  "SELECT id, kullanici_adi, islem_tipi, tarih FROM"
                  " giris_loglari ORDER BY id DESC",
                  conn,
              )
              if not df_loglar.empty:
                st.dataframe(df_loglar, use_container_width=True)

                log_buffer = io.StringIO()
                df_loglar.to_csv(log_buffer, index=False)
                st.download_button(
                    label="📥 Logları CSV Olarak İndir",
                    data=log_buffer.getvalue(),
                    file_name="sistem_loglari.csv",
                    mime="text/csv",
                )
              else:
                st.info("Henüz log kaydı bulunmuyor.")
          except Exception as e:
            st.error(f"Hata: {e}")
