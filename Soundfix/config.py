# -*- coding: utf-8 -*-
# =============================================================================
# config.py  -  Genel ayarlar ve notch (çentik) filtre konfigürasyonu
# -----------------------------------------------------------------------------
# Buradaki değerleri değiştirerek programın davranışını ayarlayabilirsin.
# GUI'den de çoğu ayar değiştirilebilir; bu dosya "başlangıç değerleri"dir.
# =============================================================================

# Örnekleme frekansı (Hz). VB-Audio Cable'ın varsayılanı 48000'dir.
# Hem mikrofonun hem de sanal kablonun bu değeri desteklediğinden emin ol.
SAMPLE_RATE = 48000

# Blok (buffer / block) boyutu = bir seferde işlenen örnek (frame) sayısı.
#   Küçük değer -> düşük gecikme, ama daha fazla CPU ve olası ses çıtırtısı.
#   Büyük değer -> daha stabil, ama gecikme artar.
#   @48kHz:  256 ~ 5 ms,  512 ~ 11 ms,  1024 ~ 21 ms
BLOCK_SIZE = 512

# Çıkış kanal sayısı. Sanal kablolar genelde stereo (2) ister.
# Mono sinyal her iki kanala kopyalanır.
OUTPUT_CHANNELS = 2

# PortAudio gecikme tercihi: 'low' | 'high' veya saniye cinsinden float (örn. 0.02)
LATENCY = 'low'

# -----------------------------------------------------------------------------
# Notch (çentik) filtreleri
#   freq    -> bastırılacak merkez frekans (Hz)
#   q       -> Q faktörü. Yüksek Q = daha DAR bant = sese daha az zarar,
#              ama frekansı tam tutturman gerekir. Düşük Q = geniş bant.
#   enabled -> filtre aktif mi?
#
# Türkiye şebeke frekansı 50 Hz'dir; "ground loop hum" 50 Hz ve katlarında
# (100/150/200 Hz) ortaya çıkar. Önce analyzer ile gerçek tepe frekansı ölç,
# sonra gerekirse buradaki 'freq' değerlerini düzelt.
# -----------------------------------------------------------------------------
NOTCHES = [
    {"freq": 50.0,  "q": 30.0, "enabled": True},
    {"freq": 100.0, "q": 30.0, "enabled": True},
    {"freq": 150.0, "q": 30.0, "enabled": True},
    {"freq": 200.0, "q": 30.0, "enabled": True},
]

# Q faktörü için GUI slider sınırları
Q_MIN = 2.0
Q_MAX = 100.0

# -----------------------------------------------------------------------------
# Analiz (tespit) modu ayarları
# -----------------------------------------------------------------------------
ANALYZE_DURATION = 3.0    # saniye - test kaydı süresi
ANALYZE_MAX_FREQ = 1000   # Hz - grafikte ve tepe (peak) aramada üst sınır
