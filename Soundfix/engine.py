# -*- coding: utf-8 -*-
# =============================================================================
# engine.py  -  Gerçek zamanlı ses motoru (giriş -> filtre -> çıkış)
# -----------------------------------------------------------------------------
# sounddevice.Stream ile mikrofondan ses alır, NotchFilterBank ile temizler,
# sanal çıkış cihazına (VB-Cable) yazar. Ses callback'i ayrı bir thread'de
# çalışır; GUI ile paylaşılan seviye (level) değerleri burada güncellenir.
# =============================================================================

import threading
import numpy as np
import sounddevice as sd

from dsp import NotchFilterBank


class AudioEngine:
    def __init__(self, config):
        self.config = config
        self.stream = None
        self.running = False

        # Filtre bankası callback ve GUI arasında paylaşıldığı için kilit kullanıyoruz.
        self._lock = threading.Lock()
        self.filterbank = NotchFilterBank(config.SAMPLE_RATE, config.NOTCHES)

        # VU metre için anlık RMS seviyeleri (callback yazar, GUI okur)
        self.input_level = 0.0
        self.output_level = 0.0

    # ---- Ayar güncelleme -----------------------------------------------------
    def update_filters(self, notches):
        """GUI'den filtre ayarları değişince çağrılır (thread-güvenli)."""
        with self._lock:
            self.filterbank.set_notches(notches)

    # ---- Ses callback'i ------------------------------------------------------
    def _callback(self, indata, outdata, frames, time, status):
        if status:
            # XRun (buffer dolma/boşalma) gibi durumlar burada görünür
            print("Stream durumu:", status)

        # Mikrofonu mono olarak işliyoruz: ilk kanalı al
        x = indata[:, 0].astype(np.float64)

        # Giriş seviyesi (RMS)
        self.input_level = float(np.sqrt(np.mean(x * x)) + 1e-12)

        # Filtreleri uygula (durum korunur)
        with self._lock:
            y = self.filterbank.process(x)

        # Çıkış seviyesi (RMS)
        self.output_level = float(np.sqrt(np.mean(y * y)) + 1e-12)

        # Çıkışa yaz: mono sinyali tüm çıkış kanallarına kopyala
        yf = y.astype(np.float32)
        for ch in range(outdata.shape[1]):
            outdata[:, ch] = yf

    # ---- Başlat / Durdur -----------------------------------------------------
    def start(self, input_device, output_device, block_size=None, samplerate=None):
        """Akışı başlat. input_device / output_device = cihaz index'leri."""
        if self.running:
            return

        block_size = block_size or self.config.BLOCK_SIZE
        samplerate = samplerate or self.config.SAMPLE_RATE

        # Durumu temizle ki eski filtre artıkları kalmasın
        with self._lock:
            self.filterbank.reset_state()

        self.stream = sd.Stream(
            samplerate=samplerate,
            blocksize=block_size,
            device=(input_device, output_device),   # (giriş, çıkış) cihazları
            channels=(1, self.config.OUTPUT_CHANNELS),
            dtype="float32",
            latency=self.config.LATENCY,
            callback=self._callback,
        )
        self.stream.start()
        self.running = True

    def stop(self):
        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
            finally:
                self.stream = None
        self.running = False
        self.input_level = 0.0
        self.output_level = 0.0
