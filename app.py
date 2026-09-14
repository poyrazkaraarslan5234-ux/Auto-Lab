class AutoLabProEngine:
  def __init__(self, vehicle_data):
    self.vehicle = vehicle_data  # { 'hp': 150, 'weight': 1400, 'drag_coeff': 0.32, 'engine_type': 'turbo', ... }

  def calculate_aerodynamics(self, speed_kmh, roof_box=False, windows_open=False):
    cd = self.vehicle.get('drag_coeff', 0.32)
    if roof_box:
      cd += 0.08
    if windows_open:
      cd += 0.04
    extra_fuel_pct = (cd - 0.32) * 50 + (speed_kmh / 100) * 8
    return {
        'new_cd': round(cd, 2),
        'extra_fuel_consumption_pct': round(extra_fuel_pct, 2),
    }

  def calculate_aquaplaning_risk(
      self, tread_depth_mm, water_depth_mm, speed_kmh
  ):
    critical_speed = (
        6.3 * (tread_depth_mm**0.5) * (10 / max(water_depth_mm, 1)) + 40
    )
    risk_status = (
        'YÜKSEK RİSK' if speed_kmh > critical_speed else 'GÜVENLİ'
    )
    return {
        'critical_speed_kmh': round(critical_speed, 1),
        'status': risk_status,
    }

  def calculate_altitude_loss(self, altitude_meters, is_turbo):
    loss_pct = (altitude_meters / 1000) * (3 if is_turbo else 10)
    current_hp = self.vehicle['hp'] * (1 - loss_pct / 100)
    return {
        'altitude_m': altitude_meters,
        'power_loss_pct': round(loss_pct, 1),
        'effective_hp': round(current_hp, 1),
    }

  def calculate_emission_prediction(
      self, engine_age_years, mileage_km, spark_plug_status
  ):
    co_score = (
        0.5 + (engine_age_years * 0.05) + (mileage_km / 100000 * 0.1)
    )
    if not spark_plug_status:
      co_score += 0.8
    pass_inspection = co_score < 3.5
    return {
        'estimated_co_level': round(co_score, 2),
        'inspection_pass': pass_inspection,
    }

  def calculate_sound_isolation(self, added_butyl_layers):
    base_db = 72
    reduction = added_butyl_layers * 2.5
    return {
        'cabin_db': max(base_db - reduction, 50),
        'noise_reduction_db': reduction,
    }

  def simulate_lsd_traction(
      self, surface_friction_coeff, lsd_active=True
  ):
    if lsd_active:
      torque_transfer_pct = 80 if surface_friction_coeff < 0.4 else 50
    else:
      torque_transfer_pct = 50 if surface_friction_coeff < 0.4 else 50
    return {'traction_efficiency': f'{torque_transfer_pct}% güç aktarımı'}

  def calculate_alternative_fuel(self, fuel_type='CNG'):
    efficiency_map = {'CNG': 1.15, 'Hydrogen': 1.25, 'LPG': 1.05}
    valve_wear_risk = (
        'Yüksek (Kuruma/Kuruluk)'
        if fuel_type in ['CNG', 'LPG']
        else 'Normal'
    )
    return {
        'efficiency_multiplier': efficiency_map.get(fuel_type, 1.0),
        'valve_wear_risk': valve_wear_risk,
    }

  def calculate_backpressure(
      self, catalyst_removed=False, pipe_diameter_inch=2.25
  ):
    hp_gain = 8 if catalyst_removed else 0
    low_end_torque_loss = 5 if catalyst_removed else 0
    return {
        'estimated_hp_gain': hp_gain,
        'low_end_torque_loss_pct': low_end_torque_loss,
    }

  def simulate_chassis_flex(self, chassis_age_years, has_strut_bar=False):
    rigidity_score = max(100 - (chassis_age_years * 1.5), 60)
    if has_strut_bar:
      rigidity_score += 10
    return {'chassis_rigidity_score': min(rigidity_score, 100)}

  def calculate_friction_reduction(self, ceramic_additive_used=True):
    saved_hp = 3.5 if ceramic_additive_used else 0.0
    return {
        'recovered_hp': saved_hp,
        'friction_coefficient_reduction_pct': 12
        if ceramic_additive_used
        else 0,
    }

  def calculate_registration_costs(self, plate_type='Special'):
    base_fee = 5000 if plate_type == 'Special' else 1500
    return {'total_estimated_cost_tl': base_fee + 1200}

  def calculate_ac_load(self, fan_level=3, target_temp=20, ambient_temp=35):
    load_hp = (ambient_temp - target_temp) * 0.1 + (fan_level * 0.3)
    return {'engine_power_stolen_hp': round(load_hp, 1)}

  def calculate_blind_spot_score(
      self, vehicle_length_m, has_blind_spot_assist=False
  ):
    base_score = 70 if vehicle_length_m > 4.5 else 90
    if has_blind_spot_assist:
      base_score += 15
    return {'safety_score': min(base_score, 100)}

  def calculate_turbo_timer(
      self, last_boost_bar=1.2, driving_intensity='Aggressive'
  ):
    cool_down_seconds = int(
        30 + (last_boost_bar * 40)
        if driving_intensity == 'Aggressive'
        else 20
    )
    return {'idle_cool_down_seconds': cool_down_seconds}

  def check_window_tint(self, front_vlt_pct=70, side_vlt_pct=30):
    front_pass = front_vlt_pct >= 70
    side_pass = side_vlt_pct >= 20
    return {
        'front_glass_legal': front_pass,
        'side_glass_legal': side_pass,
    }

  def calculate_brake_fluid_status(self, water_content_pct=2.5):
    boiling_point = 230 - (water_content_pct * 35)
    fade_risk = 'RİSKLİ' if boiling_point < 160 else 'GÜVENLİ'
    return {
        'current_boiling_point_c': round(boiling_point, 1),
        'fade_risk': fade_risk,
    }

  def simulate_panoramic_roof(self, mileage_km, chassis_age_years):
    seal_wear_pct = min(
        (mileage_km / 50000) * 15 + (chassis_age_years * 5), 100
    )
    water_leak_risk = seal_wear_pct > 70
    return {
        'seal_wear_pct': round(seal_wear_pct, 1),
        'water_leak_risk': water_leak_risk,
    }

  def calculate_cca_performance(
      self, ambient_temp_c=-15, battery_health_pct=80
  ):
    available_cca_pct = battery_health_pct * (1 + (ambient_temp_c / 50))
    starting_success = available_cca_pct > 50
    return {
        'available_cca_efficiency_pct': round(
            max(available_cca_pct, 0), 1
        ),
        'will_start': starting_success,
    }

  def calculate_parking_brake_hold(
      self, slope_degrees=15, brake_tension_status='Good'
  ):
    max_safe_slope = 22 if brake_tension_status == 'Good' else 12
    will_hold = slope_degrees <= max_safe_slope
    return {
        'max_safe_slope_deg': max_safe_slope,
        'safe_to_park': will_hold,
    }

  # --- YENİ EKLENEN 10 NUMARA MODÜL (METOTLAR) ---

  def calculate_ev_battery_health(self, cycle_count, calendar_age_years, average_soh_pct=95.0):
      # Lityum-iyon batarya SoH ve hücre balans simülasyonu
      degradation = (cycle_count * 0.015) + (calendar_age_years * 1.2)
      real_soh = max(average_soh_pct - degradation, 50.0)
      range_loss_pct = round((100 - real_soh) * 1.1, 1)
      cell_imbalance_mv = round(cycle_count * 0.12 + calendar_age_years * 1.5, 1)
      return {
          "estimated_soh_pct": round(real_soh, 1),
          "cell_imbalance_mv": cell_imbalance_mv,
          "range_loss_pct": range_loss_pct,
          "bms_health_status": "Kritik Balans" if cell_imbalance_mv > 50 else "Normal"
      }

  def calculate_hidden_features_coding(self, vehicle_brand="VAG"):
      # Gizli özellik ve kodlama asistanı
      features = {
          "VAG": ["Amerikan Park", "Kadran Selamlama", "Ek Yakıt Miktarı", "Kornalı Kilit Onayı"],
          "BMW": ["Dijital Hız Göstergesi", "Katlanır Ayna (Uzaktan)", "Start-Stop Hafıza", "Sport+ Modu"],
          "Ford": ["Lastik Basınç Sıfırlama", "Kilitlenince Korna", "Geri Viteste Otomatik Silecek"]
      }
      list_feat = features.get(vehicle_brand.upper(), ["Genel Tanılama Menüleri"])
      return {
          "supported_brand": vehicle_brand.upper(),
          "codable_features": list_feat,
          "bcm_risk_level": "Düşük (Doğru OBD Dongle İle)"
      }

  def calculate_turbo_intercooler_efficiency(self, boost_bar=1.5, ambient_temp_c=25, charge_air_temp_c=65):
      # Turboşarj ve intercooler verimlilik hesaplayıcı
      ideal_temp = ambient_temp_c + (boost_bar * 15)
      efficiency_pct = max(100 - ((charge_air_temp_c - ideal_temp) * 1.5), 45.0)
      turbo_lag_status = "Hızlı Tepki" if boost_bar < 1.4 else "Yüksek Basınç / Hafif Lag"
      return {
          "intercooler_efficiency_pct": round(efficiency_pct, 1),
          "turbo_lag_status": turbo_lag_status,
          "thermal_stress_risk": "Yüksek" if charge_air_temp_c > 75 else "Güvenli"
      }

  def calculate_paint_thickness_map(self, hood_micron=130, roof_micron=120, door_micron=140):
      # Detaylı restorasyon ve boya kalınlık haritası
      def parse_status(mic):
          if mic < 90: return "İnce Boya / Zımpara"
          elif 90 <= mic <= 160: return "Orijinal"
          elif 160 < mic <= 300: return "Boyalı"
          else: return "Macunlu / Kalın İşlem"
      return {
          "hood_status": parse_status(hood_micron),
          "roof_status": parse_status(roof_micron),
          "door_status": parse_status(door_micron),
          "overall_restoration_grade": "Kusursuz" if all(90 <= x <= 160 for x in [hood_micron, roof_micron, door_micron]) else "Müdahaleli"
      }

  def calculate_insurance_risk_score(self, vehicle_value=750000, driver_age=30, accident_history_count=0):
      # Kasko ve trafik sigortası hasar risk analizi
      base_score = 30 + (accident_history_count * 25)
      if driver_age < 25: base_score += 20
      elif driver_age > 60: base_score += 10
      estimated_premium_tl = int(vehicle_value * 0.03 + (base_score * 150))
      return {
          "risk_score": min(base_score, 100),
          "estimated_annual_insurance_tl": estimated_premium_tl,
          "risk_category": "Yüksek Risk" if base_score > 60 else "Normal Risk"
      }

  def calculate_fuel_injector_trim(self, stft_pct=1.5, ltft_pct=-2.0):
      # Yakıt enjektör püskürtme ve trim analizörü
      total_trim = abs(stft_pct) + abs(ltft_pct)
      clogging_risk = "Tıkalı Enjektör Riski" if total_trim > 8.0 else "Normal Besleme"
      return {
          "total_fuel_trim_pct": round(total_trim, 2),
          "injector_status": clogging_risk
      }

  def calculate_transmission_clutch_life(self, transmission_type="DCT", traffic_density="High", gearbox_temp_c=105):
      # Şanzıman kavrama sıcaklık ve ömür simülatörü
      wear_rate = 1.5 if traffic_density == "High" else 0.8
      if gearbox_temp_c > 115: wear_rate *= 2.0
      remaining_life_pct = max(100 - (gearbox_temp_c * 0.5 * wear_rate / 10), 10.0)
      return {
          "transmission_type": transmission_type,
          "estimated_clutch_life_pct": round(remaining_life_pct, 1),
          "mekatronik_risk": "Yüksek Isınma" if gearbox_temp_c > 110 else "Stabil"
      }

  def calculate_bargain_assistant(self, market_price=800000, expert_cost_total=25000, heavy_damage=False):
      # 2. el araç alım satım ekspertiz fiyat pazarlık botu
      discount = expert_cost_total + (75000 if heavy_damage else 15000)
      ideal_offer = market_price - discount
      return {
          "market_price_tl": market_price,
          "suggested_bargain_offer_tl": ideal_offer,
          "recommended_discount_tl": discount
      }

  def calculate_exhaust_db_simulator(self, pipe_diameter_inch=2.5, muffler_removed=False, rpm=4000):
      # Egzoz ses frekansı ve modifiye simülatörü
      base_db = 75 + (rpm / 1000) * 2
      if muffler_removed: base_db += 12
      if pipe_diameter_inch > 2.75: base_db += 4
      tuv_pass = base_db <= 92
      return {
          "estimated_db": round(base_db, 1),
          "tuv_inspection_pass": tuv_pass
      }

  def calculate_lighting_lux_test(self, lens_yellowing_pct=20, bulb_type="LED"):
      # Far aydınlatma gücü ve LED/Xenon muayene uygunluk testi
      base_lux = 800 if bulb_type == "LED" else 550
      effective_lux = base_lux * (1 - (lens_yellowing_pct / 100))
      inspection_pass = effective_lux >= 450 and lens_yellowing_pct < 40
      return {
          "effective_lux": round(effective_lux, 1),
          "inspection_pass": inspection_pass,
          "cut_off_line_status": "Düzgün Odak" if lens_yellowing_pct < 30 else "Dağınık Işık / Kusurlu"
      }


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

st.set_page_config(
    page_title='Auto Lab Pro - Ultimate Engineering Studio',
    page_icon='🚗',
    layout='wide',
)

WHATSAPP_NUMARASI = '905510305139'

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
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS randevular (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad_soyad TEXT,
                telefon TEXT,
                plaka TEXT,
                servis_turu TEXT,
                tarih_saat TEXT,
                durum TEXT
            )
        """)
    conn.commit()
    conn.close()
  except Exception as e:
    print(f'Veritabanı hatası: {e}')


init_db()


def rapor_kaydet(plaka, model, yil, km, sonuc, tavsiye):
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
            model,
            yil,
            km,
            sonuc,
            tavsiye,
        ),
    )
    conn.commit()
    conn.close()
  except Exception as e:
    print(f'Kayıt hatası: {e}')


def log_kaydet(modul, detay, sonuc):
  try:
    conn = sqlite3.connect('autolab_pro.db', timeout=10)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO islem_loglari (modul_adi, detay, sonuc) VALUES (?, ?, ?)',
        (modul, detay, sonuc),
    )
    conn.commit()
    conn.close()
  except Exception as e:
    print(f'Loglama hatası: {e}')


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
            <p style="color: #9ca3af;">Uygulamayı kesintisiz kullanmaya devam etmek için sol üstteki WhatsApp butonundan size özel şifreyi alıp yazabilirsiniz.</p>
        </div>
    """,
      unsafe_allow_html=True,
  )

  st.markdown('<br>', unsafe_allow_html=True)
  girilen_sifre = st.text_input(
      '🔑 Size Özel Erişim Şifresi:', type='password'
  )

  if st.button('Sisteme Giriş Yap', type='primary', use_container_width=True):
    gecerli_sifreler = [
        'autolab2026',
        'pro9955',
        'vip-oto-sifre',
        'AutoLab5234',
    ]
    if girilen_sifre in gecerli_sifreler:
      st.session_state.logged_in = True
      st.session_state.islem_sayisi = 0
      st.success('Giriş başarılı! Yönlendiriliyorsunuz...')
      st.rerun()
    else:
      st.error('Hatalı veya geçersiz şifre!')
  st.stop()

st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)


def detayli_arac_analizi(arac_adi, yil, km, hasar_durumu):
  try:
    km_int = int(km)
    yil_int = int(yil)
  except:
    km_int = 0
    yil_int = 2020

  yas = 2026 - yil_int

  if 'Hatasız' in hasar_durumu and km_int < 80000 and yas <= 5:
    tavsiye = (
        '🔥 Kesinlikle Alınır! Düşük yaş, düşük kilometre ve hatasız'
        ' kondisyonda.'
    )
    risk = 'Çok Düşük. Periyodik bakımlar haricinde masraf açmaz.'
  elif (
      'Ağır Hasar' in hasar_durumu
      or 'Şase' in hasar_durumu
      or 'Podye' in hasar_durumu
  ):
    tavsiye = (
        '🚨 Riskli! Uzak Durun. Şase veya podye işlemleri sürüş güvenliğini'
        ' doğrudan tehlikeli kılar.'
    )
    risk = 'Yüksek. Kaporta esnemesi ve ağır kaza geçmişi riski.'
  elif km_int > 200000 or yas > 12:
    tavsiye = (
        '⚠️ Şartlı Alınır. Yüksek kilometre/yaş sebebiyle motor, turbo ve'
        ' yürüyen aksam detaylı mekanik eksperden geçmeli.'
    )
    risk = 'Orta-Yüksek (Masraf çıkarma olasılığı yüksek).'
  else:
    tavsiye = (
        '✅ Değerlendirilebilir. Eksper raporu temiz çıkarsa fiyatta pazarlık'
        ' yapılarak alınabilir.'
    )
    risk = 'Orta seviye (Yaşına ve kilometresine uygun aşınmalar mevcut).'

  return {
      'model': f'{yil} {arac_adi.title()}',
      'yas': f'{yas} Yaşında',
      'km': f'{km_int:,} KM'.replace(',', '.'),
      'eksper': hasar_durumu,
      'risk': risk,
      'tavsiye': tavsiye,
  }


def arac_analizi_uret(arac_adi):
  sorgu_kucuk = arac_adi.lower().strip()
  if 'civic' in sorgu_kucuk:
    return {
        'baslik': 'Honda Civic',
        'motor': '1.5 VTEC Turbo / 1.6',
        'hp': 182,
        'tork': 240,
        'guc_tork': '125 - 182 HP',
        'kronik': 'Direksiyon kutusu tıkırtısı, boya hassasiyeti.',
        'avantaj': 'Yüksek piyasa değeri ve ikinci el hızı.',
        'yag': '0W-20 veya 5W-30 Tam Sentetik',
        'antifriz': 'Organik OAT (Kırmızı/Pembe)',
        'fren': 'DOT 4',
    }
  elif 'doblo' in sorgu_kucuk:
    return {
        'baslik': 'Fiat Doblo',
        'motor': '1.6 Multijet',
        'hp': 120,
        'tork': 320,
        'guc_tork': '90 - 120 HP',
        'kronik': 'Ön takım aşınmaları, baskı balata.',
        'avantaj': 'Geniş hacim, ucuz ve bol yedek parça.',
        'yag': '5W-30 DPF Uyumlu (C2/C3)',
        'antifriz': 'Organik (Mavi/Yeşil)',
        'fren': 'DOT 4',
    }
  elif 'passat' in sorgu_kucuk:
    return {
        'baslik': 'VW Passat',
        'motor': '1.4/1.5 TSI - 2.0 TDI',
        'hp': 150,
        'tork': 250,
        'guc_tork': '150 - 240 HP',
        'kronik': 'DSG kavrama hassasiyeti.',
        'avantaj': 'Üstün konfor ve sessiz izolasyon.',
        'yag': '5W-30 Longlife (VW 504.00 / 507.00)',
        'antifriz': 'G12++ / G13 (Mor/Pembe)',
        'fren': 'DOT 4 ESP',
    }
  elif 'mustang' in sorgu_kucuk:
    return {
        'baslik': 'Ford Mustang',
        'motor': '2.3 EcoBoost / 5.0 V8',
        'hp': 315,
        'tork': 475,
        'guc_tork': '315 - 450 HP',
        'kronik': 'Yüksek yakıt tüketimi, lastik aşınması.',
        'avantaj': 'Muazzam performans ve ikonik tasarım.',
        'yag': '5W-20 / 5W-30 Tam Sentetik',
        'antifriz': 'Ford WSS-M97B44-D (Turuncu)',
        'fren': 'DOT 4 High Performance',
    }
  else:
    return {
        'baslik': arac_adi.upper(),
        'motor': 'Standart Ünite',
        'hp': 110,
        'tork': 240,
        'guc_tork': '100 - 150 HP',
        'kronik': 'Yaşlı hortum terletmeleri.',
        'avantaj': 'Günlük kullanım uyumu.',
        'yag': '5W-30 Tam Sentetik',
        'antifriz': 'Organik Standart (Genel)',
        'fren': 'DOT 4',
    }


def arac_sorun_analizi_yap(sorun_metni):
  s_kucuk = sorun_metni.lower()
  if (
      'hararet' in s_kucuk
      or 'sicaklik' in s_kucuk
      or 'isindi' in s_kucuk
  ):
    return (
        '⚠️ **Kritik Durum:** Motor termostatı sıkışmış, radyatör'
        ' tıkalı/delik, devridaim pompası arızalı veya fan müşürü çalışmıyor'
        ' olabilir. Conta yanması riski bulunduğundan araç derhal güvenli'
        ' bir yerde stop edilmeli ve soğuması beklenmelidir.',
        '1.500₺ - 35.000₺ (Arızanın kaynağına göre değişir)',
    )
  elif 'turbo' in s_kucuk:
    return (
        'Turbonun içindeki mil boşluğu, türbin pervanesi aşınması veya'
        ' intercooler hortumunda kaçak (delik) olabilir. Acil kontrol'
        ' edilmelidir.',
        '7.500₺ - 25.000₺+',
    )
  elif 'çalışmıyor' in s_kucuk or 'marş' in s_kucuk:
    return (
        'Akü zayıflamış veya marş motoru kömürleri bitmiş olabilir. Akü'
        ' kutup başlarını kontrol edin.',
        '1.500₺ - 4.500₺',
    )
  elif 'duman' in s_kucuk:
    return (
        'Siyah duman: Hava filtresi tıkalı veya enjektör arızası. Mavi duman:'
        ' Motor yağ yakıyor. Beyaz duman: Silindir kapak contası su veriyor'
        ' olabilir.',
        '3.000₺ - 20.000₺+',
    )
  elif 'titreme' in s_kucuk or 'silkeleme' in s_kucuk:
    return (
        'Buji veya ateşleme bobinlerinde kesinti olabilir yahut baskı balata'
        ' (debriyaj) arızalıdır.',
        '1.200₺ - 6.000₺',
    )
  elif 'ses' in s_kucuk or 'tıkırtı' in s_kucuk or 'uğultu' in s_kucuk:
    return (
        'Ön takımdan (salıncak, rot başı) veya tekerlek bilyasından'
        ' kaynaklanıyor olabilir.',
        '1.000₺ - 5.000₺',
    )
  else:
    return (
        'Belirttiğiniz şikayet genel mekanik veya sensör kaynaklı olabilir.'
        ' Detaylı ustaya gösterilmesi tavsiye edilir.',
        'Değişkendir',
    )


def sigorta_kasko_hesapla(
    arac_degeri, arac_yasi, surucu_basamagi, hasar_gecmisi
):
  temel_kasko = arac_degeri * 0.035
  yas_katsayisi = 1 + (arac_yasi * 0.02)

  basamak_carpanlari = {
      1: 1.50,
      2: 1.30,
      3: 1.15,
      4: 1.00,
      5: 0.85,
      6: 0.75,
      7: 0.60,
      8: 0.50,
  }
  b_carpan = basamak_carpanlari.get(surucu_basamagi, 1.00)
  hasar_farki = 1.25 if 'Hasarlı' in hasar_gecmisi else 0.90

  kasko_tutar = temel_kasko * yas_katsayisi * b_carpan
  trafik_sigortasi = 4500 * b_carpan * hasar_farki

  return int(kasko_tutar), int(trafik_sigortasi)


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


def pdf_eksper_raporu_olustur(
    dosya_adi,
    plaka,
    marka_model,
    yil,
    km,
    motor_durumu,
    sema_dict,
    sonuc,
    tavsiye,
    maliyet_hesabi,
):
  doc = SimpleDocTemplate(
      dosya_adi,
      pagesize=A4,
      rightMargin=40,
      leftMargin=40,
      topMargin=40,
      bottomMargin=40,
  )
  elements = []
  styles = getSampleStyleSheet()

  title_style = ParagraphStyle(
      'TitleStyle',
      parent=styles['Heading1'],
      fontSize=16,
      textColor=colors.HexColor('#1e3a8a'),
      alignment=1,
      spaceAfter=6,
  )
  sub_title_style = ParagraphStyle(
      'SubTitleStyle',
      parent=styles['Heading2'],
      fontSize=9,
      textColor=colors.HexColor('#4b5563'),
      alignment=1,
      spaceAfter=12,
  )
  section_heading = ParagraphStyle(
      'SectionHeading',
      parent=styles['Heading3'],
      fontSize=11,
      textColor=colors.HexColor('#1d4ed8'),
      spaceBefore=6,
      spaceAfter=4,
  )
  normal_style = ParagraphStyle(
      'NormalStyle',
      parent=styles['Normal'],
      fontSize=8.5,
      textColor=colors.HexColor('#1f2937'),
      spaceAfter=4,
  )

  qr_path = qr_olustur(
      f'Auto Lab Pro Verified Report - Plaka: {plaka} - Model: {marka_model}'
  )

  elements.append(
      Paragraph(
          'OTO EKSPERTİZ MERKEZİ - QR DOĞRULAMALI KURUMSAL RAPOR', title_style
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
      Paragraph('2. Kaporta Boya Lejantı (Renk Kodları)', section_heading)
  )
  data_lejant = [
      ['Orijinal', 'Boyalı', 'Lokal Boyalı', 'Değişen', 'Sök-Tak / Ayar'],
      ['Beyaz', 'Mavi', 'Sarı', 'Kırmızı', 'Turuncu'],
  ]
  t_lejant = Table(data_lejant, colWidths=[106, 106, 106, 106, 105])
  t_lejant.setStyle(
      TableStyle([
          ('BACKGROUND', (0, 0), (0, 1), colors.HexColor('#f3f4f6')),
          ('BACKGROUND', (1, 1), (1, 1), colors.HexColor('#3b82f6')),
          ('TEXTCOLOR', (1, 1), (1, 1), colors.white),
          ('BACKGROUND', (2, 1), (2, 1), colors.HexColor('#facc15')),
          ('BACKGROUND', (3, 1), (3, 1), colors.HexColor('#ef4444')),
          ('TEXTCOLOR', (3, 1), (3, 1), colors.white),
          ('BACKGROUND', (4, 1), (4, 1), colors.HexColor('#fb923c')),
          ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
          ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
          ('PADDING', (0, 0), (-1, -1), 4),
          ('FONTSIZE', (0, 0), (-1, -1), 8),
          ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
      ])
  )
  elements.append(t_lejant)
  elements.append(Spacer(1, 6))

  elements.append(
      Paragraph('3. Kuş Bakışı Kaporta Durum Şeması', section_heading)
  )
  data_sema = [
      [
          'ÖN BÖLÜM',
          f"Ön Kaput: {sema_dict.get('Ön Kaput', 'Orijinal')}",
          f"Tavan: {sema_dict.get('Tavan', 'Orijinal')}",
      ],
      [
          'SOL TARAF',
          f"Sol Ön Çamurluk: {sema_dict.get('Sol Ön Çamurluk', 'Orijinal')}",
          f"Sağ Ön Çamurluk: {sema_dict.get('Sağ Ön Çamurluk', 'Orijinal')}",
      ],
      [
          'YAN KISIM',
          f"Sol Ön Kapı: {sema_dict.get('Sol Ön Kapı', 'Orijinal')}",
          f"Sağ Ön Kapı: {sema_dict.get('Sağ Ön Kapı', 'Orijinal')}",
      ],
      [
          'ORTA KISIM',
          f"Sol Arka Kapı: {sema_dict.get('Sol Arka Kapı', 'Orijinal')}",
          f"Sağ Arka Kapı: {sema_dict.get('Sağ Arka Kapı', 'Orijinal')}",
      ],
      [
          'ARKA YAN',
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
      Paragraph(
          '4. Tahmini Onarım ve Boya Maliyet Analizi', section_heading
      )
  )
  data_maliyet = [
      ['Toplam Hasarlı/İşlemli Parça:', f"{maliyet_hesabi['adet']} Parça"],
      [
          'Tahmini Masraf Aralığı:',
          f"{maliyet_hesabi['tutar']:,} ₺".replace(',', '.'),
      ],
  ]
  t_mal = Table(data_maliyet, colWidths=[150, 385])
  t_mal.setStyle(
      TableStyle([
          ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fef9c3')),
          ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
          ('PADDING', (0, 0), (-1, -1), 4),
          ('FONTSIZE', (0, 0), (-1, -1), 8),
      ])
  )
  elements.append(t_mal)
  elements.append(Spacer(1, 6))

  elements.append(
      Paragraph(
          '5. Mekanik Kontrol ve Yapay Zeka Tavsiyesi', section_heading
      )
  )
  data_mekanik = [
      ['Motor Durumu:', motor_durumu],
      ['Uzman Tavsiyesi:', tavsiye],
  ]
  t_mek = Table(data_mekanik, colWidths=[110, 425])
  t_mek.setStyle(
      TableStyle([
          ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
          ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
          ('PADDING', (0, 0), (-1, -1), 4),
          ('FONTSIZE', (0, 0), (-1, -1), 8),
      ])
  )
  elements.append(t_mek)
  elements.append(Spacer(1, 10))

  if qr_path and os.path.exists(qr_path):
    elements.append(RLImage(qr_path, width=70, height=70))

  elements.append(
      Paragraph(
          '<b>Yasal Uyarı:</b> Bu rapor Auto Lab Pro dinamik sistemleri ile'
          ' üretilmiştir.',
          normal_style,
      )
  )
  doc.build(elements)


with st.sidebar:
  st.markdown('### 📊 Kullanım Durumu')
  kalan_hak = (
      PREMIUM_HAK_SAYISI if st.session_state.logged_in else UCRETSIZ_HAK_SINIRI
  ) - st.session_state.islem_sayisi
  st.write(f'Kalan İşlem Hakkı: {max(0, kalan_hak)}')

  if st.session_state.logged_in:
    st.success('🔓 VIP / Premium Üye Modu (250 Hak)')
    if st.button('Oturumu Kapat'):
      st.session_state.logged_in = False
      st.session_state.islem_sayisi = 0
      st.rerun()
  st.divider()

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">🚗 AUTO LAB PRO - ULTIMATE EDITION</div>
        <div class="hero-title" style="font-size: 20px; color: #38bdf8; margin-top: 5px;">Mühendislik Odaklı Dinamik Araç & Ekspertiz Analiz Merkezi</div>
    </div>
""",
    unsafe_allow_html=True,
)

sekme = st.selectbox(
    'Auto Lab Ana Menü:',
    [
        '🔍 Manuel Araç & Ekspertiz Analizi',
        '📄 PDF Eksper Raporu & Renkli Şema',
        '🛡️ Sigorta & Kasko Hesaplayıcı',
        '📅 Servis Randevu & Müşteri CRM',
        '🚗 Model & Motor Veritabanı',
        '⚖️ Serbest Araç Karşılaştırma',
        '⚡ Gelişmiş ECU & Chip Tuning Simülatörü',
        '🛠️ Araç Sorunları & Çözüm Asistanı',
        '🛞 Lastik & Jant Optimizasyonu',
        '🌡️ Soğutma & Antifriz Donma Analizi',
        '🔋 Akü & Alternatör Test Simülatörü',
        '⛽ Yakıt Amortisman & LPG Hesaplayıcı',
        '🏎️ 0-400m Drag Kalkış Simülatörü',
        '🛑 Fren & G-Kuvveti Simülatörü',
        '🧯 DPF & Rejenerasyon Asistanı',
        '🔌 EV Batarya Sağlığı (SoH) Simülatörü',
        '💨 Aerodinamik Sürtünme & Yakıt Tasarrufu',
        '🌊 Aquaplaning & Lastik Basınç Analizörü',
        '🏔️ Rota İrtifa & Turbo Basınç Kaybı',
        '🧪 TÜVTÜRK Egzoz Emisyon Tahmincisi',
        '🎧 Kabin İçi Desibel & İzolasyon Analizörü',
        '⚙️ LSD Diferansiyel & Tork Aktarımı',
        '🌱 Alternatif Yakıt / CNG-Hidrojen Verimliliği',
        '🛠️ Egzoz Geri Basıncı & Downpipe Optimizasyonu',
        '🔩 Şasi Burulma Rijitliği ve Yol Tutuş Eğrisi',
        '🧪 Motor İçi Sürtünme & Seramik Yağ Katkısı',
        '🏷️ Özel Plaka & Trafik Tescil Maliyeti',
        '❄️ Klima Kompresörü & Motor Yükü Verimliliği',
        '👀 Ayna Kör Nokta Sürüş Güvenlik Skoru',
        '⏱️ Turbo EGT & Koruma Asistanı',
        '🕶️ Cam Filmi VLT & TÜVTÜRK Uygunluğu',
        '💧 Fren Hidroliği Nem Oranı & Kaynama Noktası',
        '☀️ Panoramik Cam Tavan Burulma Simülatörü',
        '⚡ Marş Basma Akımı (CCA) & Soğuk Hava Testi',
        '🅿️ Otopark Eğim ve El Freni Tutunma Gücü',
        '⛽ Yakıt Enjektör Püskürtme ve Trim Analizörü',
        '🕹️ Şanzıman Kavrama Sıcaklık ve Ömür Simülatörü',
        '🤖 2. El Araç Alım Satım Ekspertiz Fiyat Pazarlık Botu',
        '🔊 Egzoz Ses Frekansı (dB) ve Modifiye Simülatörü',
        '💡 Far Aydınlatma Gücü (Lux) ve LED/Xenon Testi',
        '📂 Kayıtlı Arşiv & Raporlar',
    ],
)

if sekme == '🔍 Manuel Araç & Ekspertiz Analizi':
  st.markdown('### 📋 Araç Bilgileri & Profesyonel Ekspertiz Analizi')
  col_m1, col_m2 = st.columns(2)
  with col_m1:
    arac_adi_input = st.text_input(
        'Araç Marka ve Modeli:',
        placeholder='Örn: Ford Focus 1.5 TDCİ',
        key='man_arac',
    )
    yil_input = st.number_input(
        'Model / Çıkış Yılı:',
        min_value=1990,
        max_value=2026,
        value=2020,
        step=1,
        key='man_yil',
    )
  with col_m2:
    km_input = st.number_input(
        'Güncel Kilometre (KM):',
        min_value=0,
        max_value=800000,
        value=75000,
        step=1000,
        key='man_km',
    )
    hasar_input = st.selectbox(
        'Genel Kaporta / Hasar Durumu:',
        [
            'Hatasız / Boyasız / Değişensiz',
            '1-2 Parça Lokal Boyalı',
            '1-2 Parça Değişen, Boyalı Parçalar Var',
            'Komple Boyalı / Tavan Boyasız',
            'Ağır Hasar Kayıtlı / Şase veya Podye İşlemli',
        ],
        key='man_hasar',
    )

  if st.button('🤖 Yapay Zeka Ekspertiz Raporunu Oluştur', key='btn_man'):
    if not arac_adi_input:
      st.warning('Lütfen araç marka ve modelini boş bırakmayın!')
    else:
      st.session_state.islem_sayisi += 1
      rapor = detayli_arac_analizi(
          arac_adi_input, yil_input, km_input, hasar_input
      )
      rapor_kaydet(
          '34 PLK 99',
          rapor['model'],
          yil_input,
          km_input,
          rapor['risk'],
          rapor['tavsiye'],
      )
      log_kaydet('Manuel Eksper', f"Araç: {rapor['model']}", rapor['risk'])
      st.success(
          '✅ Ekspertiz ve Risk Analizi Başarıyla Tamamlandı & Arşivlendi!'
      )
      st.markdown(
          f"""
                <div class="info-box">
                    <h3 style="color: #60a5fa; margin-top:0;">📌 Araç: {rapor['model']}</h3>
                    <p><b>⏳ Yaş Durumu:</b> {rapor['yas']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>📏 Kilometre:</b> <span style="color: #38bdf8; font-weight: bold;">{rapor['km']}</span></p>
                    <p><b>🛡️ Bildirilen Hasar / Ekspertiz:</b> {rapor['eksper']}</p>
                    <hr style="border-color: #374151;">
                    <p><b>⚠️ Detaylı Risk Analizi:</b> <span style="color: #f87171;">{rapor['risk']}</span></p>
                    <p><b>💰 Alınır mı?:</b> {rapor['tavsiye']}</p>
                </div>
            """,
          unsafe_allow_html=True,
      )

elif sekme == '📄 PDF Eksper Raporu & Renkli Şema':
  st.markdown('### 🗺️ Kuş Bakışı Renkli Şema & Kurumsal PDF Eksper Raporu')
  col_p1, col_p2 = st.columns(2)
  with col_p1:
    pdf_plaka = st.text_input(
        'Araç Plakası:', placeholder='Örn: 34 ABC 123', key='pdf_plk'
    )
    pdf_model = st.text_input(
        'Araç Marka ve Modeli:',
        placeholder='Örn: Renault Megane 1.5 dCi',
        key='pdf_mdl',
    )
    pdf_yil = st.number_input(
        'Model Yılı:',
        min_value=1990,
        max_value=2026,
        value=2021,
        step=1,
        key='pdf_yl',
    )
    pdf_km = st.number_input(
        'Güncel Kilometre:',
        min_value=0,
        max_value=800000,
        value=65000,
        step=1000,
        key='pdf_k',
    )
  with col_p2:
    pdf_motor = st.selectbox(
        'Motor / Mekanik Durum:',
        [
            'Motor Performansı %90 - Kusursuz',
            'Motor Performansı %78 - Normal Aşınma',
            'Turbo Bakımı Gerekli',
            'Ağır Motor Arızalı',
        ],
        key='pdf_mtr',
    )

  st.markdown('---')
  st.markdown('#### 🚗 Kuş Bakışı Şema Parça Renklendirmeleri')
  durum_secenekleri = [
      'Orijinal (Beyaz)',
      'Boyalı (Mavi)',
      'Lokal Boyalı (Sarı)',
      'Değişen (Kırmızı)',
      'Sök-Tak (Turuncu)',
  ]

  col_s1, col_s2, col_s3 = st.columns(3)
  with col_s1:
    s_kaput = st.selectbox('Ön Kaput', durum_secenekleri, key='s_kaput')
    s_tavan = st.selectbox('Tavan', durum_secenekleri, key='s_tavan')
    s_bagaj = st.selectbox('Bagaj Kapağı', durum_secenekleri, key='s_bagaj')
    s_sol_on_camurluk = st.selectbox(
        'Sol Ön Çamurluk', durum_secenekleri, key='s_soc'
    )
  with col_s2:
    s_sol_on_kapi = st.selectbox('Sol Ön Kapı', durum_secenekleri, key='s_sok')
    s_sol_arka_kapi = st.selectbox(
        'Sol Arka Kapı', durum_secenekleri, key='s_sak'
    )
    s_sol_arka_camurluk = st.selectbox(
        'Sol Arka Çamurluk', durum_secenekleri, key='s_sac'
    )
    s_sag_on_camurluk = st.selectbox(
        'Sağ Ön Çamurluk', durum_secenekleri, key='s_soc2'
    )
  with col_s3:
    s_sag_on_kapi = st.selectbox('Sağ Ön Kapı', durum_secenekleri, key='s_sok2')
    s_sag_arka_kapi = st.selectbox(
        'Sağ Arka Kapı', durum_secenekleri, key='s_sak2'
    )
    s_sag_arka_camurluk = st.selectbox(
        'Sağ Arka Çamurluk', durum_secenekleri, key='s_sac2'
    )
    s_sase = st.selectbox(
        'Şase / Podye Durumu',
        ['Orijinal (Beyaz)', 'İşlemli (Kırmızı)'],
        key='s_sase',
    )

  sema_sozlugu = {
      'Ön Kaput': s_kaput,
      'Tavan': s_tavan,
      'Bagaj Kapağı': s_bagaj,
      'Sol Ön Çamurluk': s_sol_on_camurluk,
      'Sol Ön Kapı': s_sol_on_kapi,
      'Sol Arka Kapı': s_sol_arka_kapi,
      'Sol Arka Çamurluk': s_sol_arka_camurluk,
      'Sağ Ön Çamurluk': s_sag_on_camurluk,
      'Sağ Ön Kapı': s_sag_on_kapi,
      'Sağ Arka Kapı': s_sag_arka_kapi,
      'Sağ Arka Çamurluk': s_sag_arka_camurluk,
      'Şase ve Podye': s_sase,
  }

  hatali_parca_sayisi = sum(
      1 for v in sema_sozlugu.values() if 'Orijinal' not in v
  )
  tahmini_onarim_maliyeti = hatali_parca_sayisi * 4500
  maliyet_verisi = {'adet': hatali_parca_sayisi, 'tutar': tahmini_onarim_maliyeti}

  st.markdown('<br>', unsafe_allow_html=True)
  if st.button(
      '📥 Renkli Şemalı PDF Raporunu Oluştur ve İndir',
      type='primary',
      key='btn_pdf',
  ):
    if not pdf_plaka or not pdf_model:
      st.warning('Lütfen plaka ve araç modelini boş bırakmayın!')
    else:
      st.session_state.islem_sayisi += 1
      genel_hasar_ozeti = (
          'Şase İşlemli / Ağır'
          if 'İşlemli' in s_sase
          else (
              'Parça Boyalı/Değişen Var'
              if hatali_parca_sayisi > 0
              else 'Temiz / Orijinal'
          )
      )
      gecici_analiz = detayli_arac_analizi(
          pdf_model, pdf_yil, pdf_km, genel_hasar_ozeti
      )

      rapor_kaydet(
          pdf_plaka,
          pdf_model,
          pdf_yil,
          pdf_km,
          gecici_analiz['risk'],
          gecici_analiz['tavsiye'],
      )
      log_kaydet(
          'PDF Eksper Raporu',
          f'Plaka: {pdf_plaka}, Model: {pdf_model}',
          'PDF Başarıyla Üretildi',
      )

elif sekme == '⛽ Yakıt Enjektör Püskürtme ve Trim Analizörü':
    st.markdown('### ⛽ Yakıt Enjektör Püskürtme ve Trim Analizörü')
    st_ft = st.number_input('Kısa Vadeli Yakıt Trim (STFT %):', value=1.5, step=0.1)
    lt_ft = st.number_input('Uzun Vadeli Yakıt Trim (LTFT %):', value=-2.0, step=0.1)
    engine = AutoLabProEngine({})
    if st.button('Enjektör Trim Analizi Yap'):
        st.session_state.islem_sayisi += 1
        res = engine.calculate_fuel_injector_trim(st_ft, lt_ft)
        st.json(res)

elif sekme == '🕹️ Şanzıman Kavrama Sıcaklık ve Ömür Simülatörü':
    st.markdown('### 🕹️ Şanzıman Kavrama Sıcaklık ve Ömür Simülatörü')
    t_type = st.selectbox('Şanzıman Tipi:', ['DCT', 'DSG', 'CVT', 'Torque Converter'])
    traffic = st.selectbox('Trafik Yoğunluğu:', ['High', 'Normal', 'Low'])
    temp_c = st.slider('Şanzıman Yağ Sıcaklığı (°C):', 60, 140, 105)
    engine = AutoLabProEngine({})
    if st.button('Şanzıman Ömür Analizini Başlat'):
        st.session_state.islem_sayisi += 1
        res = engine.calculate_transmission_clutch_life(t_type, traffic, temp_c)
        st.json(res)

elif sekme == '🤖 2. El Araç Alım Satım Ekspertiz Fiyat Pazarlık Botu':
    st.markdown('### 🤖 2. El Araç Alım Satım Ekspertiz Fiyat Pazarlık Botu')
    m_price = st.number_input('Araç Piyasası Fiyatı (TL):', value=850000, step=10000)
    exp_cost = st.number_input('Tespit Edilen Masraf Toplamı (TL):', value=30000, step=1000)
    h_damage = st.checkbox('Ağır Hasar / Şase İşlemi Var mı?')
    engine = AutoLabProEngine({})
    if st.button('İdeal Pazarlık Teklifini Hesapla'):
        st.session_state.islem_sayisi += 1
        res = engine.calculate_bargain_assistant(m_price, exp_cost, h_damage)
        st.json(res)

elif sekme == '🔊 Egzoz Ses Frekansı (dB) ve Modifiye Simülatörü':
    st.markdown('### 🔊 Egzoz Ses Frekansı (dB) ve Modifiye Simülatörü')
    pipe_d = st.slider('Boru Çapı (İnç):', 2.0, 3.5, 2.5, 0.25)
    m_rem = st.checkbox('Katalitik / Susturucu İptal mi?')
    rpm_val = st.slider('Test Devri (RPM):', 1000, 7000, 4000, 500)
    engine = AutoLabProEngine({})
    if st.button('Egzoz Ses & Muayene Simülasyonu'):
        st.session_state.islem_sayisi += 1
        res = engine.calculate_exhaust_db_simulator(pipe_d, m_rem, rpm_val)
        st.json(res)

elif sekme == '💡 Far Aydınlatma Gücü (Lux) ve LED/Xenon Testi':
    st.markdown('### 💡 Far Aydınlatma Gücü (Lux) ve LED/Xenon Muayene Uygunluk Testi')
    lens_y = st.slider('Far Camı Sararması / Yıpranması (%):', 0, 100, 20)
    b_type = st.selectbox('Ampul Tipi:', ['LED', 'Halojen', 'Xenon'])
    engine = AutoLabProEngine({})
    if st.button('Optik Far Analizini Çalıştır'):
        st.session_state.islem_sayisi += 1
        res = engine.calculate_lighting_lux_test(lens_y, b_type)
        st.json(res)

elif sekme == '🔌 EV Batarya Sağlığı (SoH) Simülatörü':
    st.markdown('### 🔌 Elektrikli Araç (EV) Batarya Sağlığı (SoH) ve Hücre Balans Simülatörü')
    cycles = st.number_input('Toplam Şarj Döngüsü:', min_value=0, value=450)
    age_y = st.number_input('Batarya Yaşı (Yıl):', min_value=0, value=3)
    soh_init = st.slider('Başlangıç SoH (%):', 80.0, 100.0, 95.0)
    engine = AutoLabProEngine({})
    if st.button('Batarya ve Hücre Analizini Çalıştır'):
        st.session_state.islem_sayisi += 1
        res = engine.calculate_ev_battery_health(cycles, age_y, soh_init)
        st.json(res)

elif sekme == '🕶️ Gizli Özellik ve Kodlama Asistanı':
    st.markdown('### 🕶️ Gizli Özellik ve Kodlama Asistanı (VAG / BMW / Ford)')
    brand = st.selectbox('Araç Grubu:', ['VAG', 'BMW', 'Ford'])
    engine = AutoLabProEngine({})
    if st.button('Kodlanabilir Özellikleri Listele'):
        st.session_state.islem_sayisi += 1
        res = engine.calculate_hidden_features_coding(brand)
        st.json(res)

elif sekme == '💨 Turboşarj ve Intercooler Verimlilik Hesaplayıcı':
    st.markdown('### 💨 Turboşarj ve Intercooler Verimlilik Hesaplayıcı')
    boost = st.slider('Turbo Basıncı (Bar):', 0.6, 2.5, 1.5)
    amb_t = st.number_input('Ortam Sıcaklığı (°C):', value=25)
    charge_t = st.number_input('Şarj Hava Sıcaklığı (°C):', value=65)
    engine = AutoLabProEngine({})
    if st.button('Intercooler Verimliliğini Hesapla'):
        st.session_state.islem_sayisi += 1
        res = engine.calculate_turbo_intercooler_efficiency(boost, amb_t, charge_t)
        st.json(res)

elif sekme == '🏷️ Detaylı Restorasyon ve Boya Kalınlık Haritası':
    st.markdown('### 🏷️ Detaylı Restorasyon ve Boya Kalınlık Haritası (Mikron)')
    h_m = st.number_input('Kaput Mikron:', value=130)
    r_m = st.number_input('Tavan Mikron:', value=120)
    d_m = st.number_input('Ön Kapı Mikron:', value=140)
    engine = AutoLabProEngine({})
    if st.button('Boya Kalınlık Haritasını Çıkar'):
        st.session_state.islem_sayisi += 1
        res = engine.calculate_paint_thickness_map(h_m, r_m, d_m)
        st.json(res)

elif sekme == '🛡️ Kasko ve Sigorta Risk Analizörü':
    st.markdown('### 🛡️ Oto Kasko ve Trafik Sigortası Hasar Risk Analizörü')
    v_val = st.number_input('Piyasa Araç Değeri (TL):', value=950000)
    d_age = st.number_input('Sürücü Yaşı:', value=32)
    acc_c = st.number_input('Geçmiş Kaza Sayısı:', value=0)
    engine = AutoLabProEngine({})
    if st.button('Sigorta Prim Risk Analizi Yap'):
        st.session_state.islem_sayisi += 1
        res = engine.calculate_insurance_risk_score(v_val, d_age, acc_c)
        st.json(res)
