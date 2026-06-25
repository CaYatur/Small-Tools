# -*- coding: utf-8 -*-
# =============================================================================
# analyzer.py  -  Tespit / Analiz modu (FFT spektrum + tepe bulma)
# -----------------------------------------------------------------------------
# Kısa bir test kaydı alır, FFT ile spektrumu çıkarır ve hangi frekanslarda
# anormal tepe (peak) olduğunu bulur. Böylece gerçek hum frekansını ölçüp
# config.py'deki notch frekanslarını ona göre ayarlayabilirsin.
#
# İki şekilde kullanılabilir:
#   1) Komut satırından tek başına:   python analyzer.py            (varsayılan mik)
#                                      python analyzer.py 3          (cihaz index 3)
#   2) GUI içinden import edilerek (analyze fonksiyonu spektrumu döndürür).
# =============================================================================

import sys
import numpy as np
import sounddevice as sd
from scipy.signal import find_peaks

import config


def record(device, duration, fs):
    """Belirtilen cihazdan 'duration' saniye mono kayıt al."""
    rec = sd.rec(int(duration * fs), samplerate=fs, channels=1,
                 device=device, dtype="float64")
    sd.wait()
    return rec[:, 0]


def compute_spectrum(x, fs):
    """Tek taraflı genlik spektrumunu (dB) hesapla. Hann penceresi kullanılır."""
    n = len(x)
    win = np.hanning(n)
    xw = x * win
    X = np.fft.rfft(xw)
    freqs = np.fft.rfftfreq(n, 1.0 / fs)
    # Pencere kazancına göre normalize edilmiş genlik
    mag = np.abs(X) * 2.0 / np.sum(win)
    magdb = 20.0 * np.log10(mag + 1e-12)
    return freqs, magdb


def find_spectrum_peaks(freqs, magdb, fmax):
    """fmax altındaki belirgin tepe frekanslarını (Hz, dB) listele."""
    mask = freqs <= fmax
    f = freqs[mask]
    m = magdb[mask]
    # Gürültü tabanına göre "belirginlik" eşiği
    prominence = max(6.0, float(np.std(m)))
    idx, _ = find_peaks(m, prominence=prominence, distance=3)
    # Genliğe göre büyükten küçüğe sırala
    order = np.argsort(m[idx])[::-1]
    return [(float(f[idx[i]]), float(m[idx[i]])) for i in order]


def analyze(device=None, duration=None, fs=None, verbose=True):
    """Kaydı al, spektrumu ve tepe listesini döndür. (freqs, magdb, peaks)"""
    duration = duration or config.ANALYZE_DURATION
    fs = fs or config.SAMPLE_RATE

    if verbose:
        print(f"[Analiz] {duration:.1f} sn kayıt alınıyor... (cihaz={device}, fs={fs})")
        print("Lütfen normal ortam sesini bırak (konuşma yapmadan hum'u ölçmek daha iyi).")

    x = record(device, duration, fs)
    freqs, magdb = compute_spectrum(x, fs)
    peaks = find_spectrum_peaks(freqs, magdb, config.ANALYZE_MAX_FREQ)

    if verbose:
        print("\n=== En belirgin tepe (peak) frekanslar ===")
        if not peaks:
            print("  (Belirgin tepe bulunamadı - ortam sessiz olabilir.)")
        for fr, mg in peaks[:10]:
            mark = "  <-- 50 Hz'in katı" if abs((fr % 50.0)) < 2.0 or abs((fr % 50.0) - 50.0) < 2.0 else ""
            print(f"  {fr:8.1f} Hz   {mg:8.1f} dB{mark}")

        print("\n=== 50 Hz harmonik seviyeleri ===")
        for h in (50, 100, 150, 200, 250, 300):
            i = int(np.argmin(np.abs(freqs - h)))
            print(f"  {h:4d} Hz -> {magdb[i]:8.1f} dB")

        print("\nİpucu: En yüksek tepe 50'nin katı değilse (örn. 60 Hz),")
        print("config.py içindeki notch 'freq' değerlerini ölçülen değere göre güncelle.")

    return freqs, magdb, peaks


if __name__ == "__main__":
    dev = None
    if len(sys.argv) > 1:
        dev = int(sys.argv[1])   # cihaz index'i (python -m sounddevice ile listelenebilir)
    analyze(device=dev)
