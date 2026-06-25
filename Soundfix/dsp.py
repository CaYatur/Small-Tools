# -*- coding: utf-8 -*-
# =============================================================================
# dsp.py  -  Sayısal sinyal işleme (DSP): Notch filtre bankası
# -----------------------------------------------------------------------------
# Her bir notch filtresi ikinci dereceden (biquad) bir IIR filtresidir.
# scipy.signal.iirnotch ile (b, a) katsayıları üretilir, bunları tek bir
# SOS (second-order sections) matrisinde birleştirip sosfilt ile uygularız.
#
# ÖNEMLİ: Gerçek zamanlı (bloklar halinde) ses işlerken filtre "durumunu" (zi)
# bloklar arasında taşımamız gerekir; aksi halde her blok başında çıtırtı olur.
# =============================================================================

import numpy as np
from scipy.signal import iirnotch, sosfilt


class NotchFilterBank:
    """Birden fazla notch filtresini bir kaskat (cascade) halinde uygular."""

    def __init__(self, fs, notches):
        self.fs = float(fs)
        self.sos = None            # aktif filtrelerin SOS matrisi
        self.zi = None             # filtre durumu (state) - bloklar arası taşınır
        self.set_notches(notches)

    def set_notches(self, notches):
        """Notch listesine göre filtreleri (yeniden) kur.

        notches: [{"freq": float, "q": float, "enabled": bool}, ...]
        """
        sections = []
        for n in notches:
            if not n.get("enabled", False):
                continue
            freq = float(n["freq"])
            q = float(n["q"])
            # Nyquist sınırı içinde ve geçerli mi kontrol et
            if freq <= 0 or freq >= self.fs / 2.0 or q <= 0:
                continue
            # iirnotch -> biquad (b, a). fs verilince freq doğrudan Hz cinsindendir.
            b, a = iirnotch(w0=freq, Q=q, fs=self.fs)
            # Tek bir SOS satırı: [b0, b1, b2, a0, a1, a2]
            sections.append(np.concatenate([b, a]))

        if sections:
            self.sos = np.array(sections, dtype=np.float64)
            # Durumu sıfırdan başlat (ses ~0'dan başladığı için temiz)
            self.zi = np.zeros((self.sos.shape[0], 2), dtype=np.float64)
        else:
            # Hiç aktif filtre yoksa sinyali olduğu gibi geçir (bypass)
            self.sos = None
            self.zi = None

    def reset_state(self):
        """Filtre durumunu sıfırla (örn. stream yeniden başlarken)."""
        if self.sos is not None:
            self.zi = np.zeros((self.sos.shape[0], 2), dtype=np.float64)

    def process(self, x):
        """1 boyutlu (mono) float dizi 'x' üzerine filtreleri uygula.

        Durum (zi) korunarak çalışır; ardışık bloklarda sürekli çağrılmalıdır.
        """
        if self.sos is None:
            return x
        y, self.zi = sosfilt(self.sos, x, zi=self.zi)
        return y
