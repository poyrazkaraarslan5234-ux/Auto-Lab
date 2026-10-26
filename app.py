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
    zaman_dagmasi = datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
    formatli_mesaj = f"🕒 `[{zaman_dagmasi}]`\n{mesaj}"
    requests.post(
        DISCORD_WEBHOOK_URL, json={"content": formatli_mesaj}, timeout=5
    )
  except Exception:
    pass

# --- GENİŞLETİLMİŞ KRONİK SORUNLAR VE BİLGİ BANKASI ---
def internetten_arac_ve_veri_arastir(arama_sorgusu):
  sorgu_kucuk = arama_sorgusu.lower().strip()

  if "honda" in sorgu_kucuk or "civic" in sorgu_kucuk or "ies" in sorgu_kucuk:
    return (
        "[AUTO-LAB KRONİK ANALİZ: HONDA]\n- **Motor ve Mekanik:** Yüksek devir"
        " sevdası nedeniyle subap ayarı sıkılaşması görülebilir. VTEC"
        " motorlarda üst kapak contası ve müşirinde terleme sık rastlanır.\n-"
        " **Şanzıman:** Manuel şanzımanları sağlamdır. Otomatik modellerde yağ"
        " değişimi aksatıldı
