# -*- coding: utf-8 -*-
# =============================================================================
# gui.py  -  Basit tkinter arayüzü (uygulamanın giriş noktası)
# -----------------------------------------------------------------------------
# Çalıştırma:   python gui.py
#
# Özellikler:
#   * Başlat / Durdur butonu
#   * Giriş (mikrofon) ve çıkış (sanal cihaz) için dropdown seçimi
#   * Blok (buffer) boyutu seçimi -> gecikme ayarı
#   * Her notch (50/100/150/200 Hz) için aç/kapa checkbox + Q slider
#   * Giriş ve çıkış için gerçek zamanlı VU metre
#   * "Analiz Et" butonu: kısa kayıt alıp spektrumu matplotlib grafikte gösterir
# =============================================================================

import threading
import numpy as np
import sounddevice as sd

import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import config
from engine import AudioEngine
import analyzer


# -----------------------------------------------------------------------------
# Yardımcı: ses cihazlarını listele
# -----------------------------------------------------------------------------
def list_devices(kind):
    """kind='input' veya 'output' -> [(index, "i: isim"), ...]"""
    result = []
    for i, d in enumerate(sd.query_devices()):
        if kind == "input" and d["max_input_channels"] > 0:
            result.append((i, f"{i}: {d['name']}"))
        elif kind == "output" and d["max_output_channels"] > 0:
            result.append((i, f"{i}: {d['name']}"))
    return result


def rms_to_pct(rms):
    """RMS -> 0..100 (dBFS tabanlı). -60 dB = 0, 0 dB = 100."""
    db = 20.0 * np.log10(rms + 1e-12)
    pct = (db + 60.0) / 60.0 * 100.0
    return float(max(0.0, min(100.0, pct)))


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("SoundFix - Gerçek Zamanlı Hum / Şebeke Gürültüsü Filtresi")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.engine = AudioEngine(config)

        # Cihaz listeleri ve "label -> index" eşlemeleri
        self.input_devices = list_devices("input")
        self.output_devices = list_devices("output")
        self.in_map = {lbl: idx for idx, lbl in self.input_devices}
        self.out_map = {lbl: idx for idx, lbl in self.output_devices}

        # Notch kontrolleri için değişkenler (checkbox + Q)
        self.enabled_vars = []
        self.q_vars = []

        self._build_ui()
        self._schedule_meter_update()

    # ---------------------------------------------------------------- UI kurulum
    def _build_ui(self):
        pad = {"padx": 6, "pady": 4}

        # ---- Üst: Cihaz seçimi ----
        dev_frame = ttk.LabelFrame(self.root, text="1) Ses Cihazları")
        dev_frame.grid(row=0, column=0, sticky="ew", **pad)

        ttk.Label(dev_frame, text="Giriş (Mikrofon):").grid(row=0, column=0, sticky="w", **pad)
        self.in_combo = ttk.Combobox(dev_frame, width=48, state="readonly",
                                     values=[lbl for _, lbl in self.input_devices])
        self.in_combo.grid(row=0, column=1, **pad)

        ttk.Label(dev_frame, text="Çıkış (Sanal Kablo):").grid(row=1, column=0, sticky="w", **pad)
        self.out_combo = ttk.Combobox(dev_frame, width=48, state="readonly",
                                      values=[lbl for _, lbl in self.output_devices])
        self.out_combo.grid(row=1, column=1, **pad)

        ttk.Label(dev_frame, text="Blok boyutu (gecikme):").grid(row=2, column=0, sticky="w", **pad)
        self.block_combo = ttk.Combobox(dev_frame, width=12, state="readonly",
                                        values=["128", "256", "512", "1024", "2048"])
        self.block_combo.set(str(config.BLOCK_SIZE))
        self.block_combo.grid(row=2, column=1, sticky="w", **pad)

        # Varsayılan seçimleri akıllıca yap
        self._select_default_devices()

        # ---- Orta: Notch filtreleri ----
        filt_frame = ttk.LabelFrame(self.root, text="2) Çentik (Notch) Filtreleri")
        filt_frame.grid(row=1, column=0, sticky="ew", **pad)

        ttk.Label(filt_frame, text="Aktif").grid(row=0, column=0, **pad)
        ttk.Label(filt_frame, text="Frekans").grid(row=0, column=1, **pad)
        ttk.Label(filt_frame, text="Q (bant darlığı)").grid(row=0, column=2, **pad)
        ttk.Label(filt_frame, text="Q değeri").grid(row=0, column=3, **pad)

        for i, n in enumerate(config.NOTCHES):
            row = i + 1
            en_var = tk.BooleanVar(value=n["enabled"])
            q_var = tk.DoubleVar(value=n["q"])
            self.enabled_vars.append(en_var)
            self.q_vars.append(q_var)

            ttk.Checkbutton(filt_frame, variable=en_var,
                            command=self._apply_filters).grid(row=row, column=0, **pad)
            ttk.Label(filt_frame, text=f"{n['freq']:.0f} Hz").grid(row=row, column=1, **pad)

            scale = ttk.Scale(filt_frame, from_=config.Q_MIN, to=config.Q_MAX,
                              variable=q_var, orient="horizontal", length=200,
                              command=lambda val, idx=i: self._on_q_change(idx))
            scale.grid(row=row, column=2, **pad)

            qlbl = ttk.Label(filt_frame, text=f"{n['q']:.0f}")
            qlbl.grid(row=row, column=3, **pad)
            # Etiketi sonradan güncelleyebilmek için sakla
            q_var.trace_add("write",
                            lambda *a, lbl=qlbl, v=q_var: lbl.config(text=f"{v.get():.0f}"))

        # ---- VU metreler ----
        vu_frame = ttk.LabelFrame(self.root, text="3) Seviye Göstergeleri (VU)")
        vu_frame.grid(row=2, column=0, sticky="ew", **pad)

        ttk.Label(vu_frame, text="Giriş:").grid(row=0, column=0, sticky="w", **pad)
        self.in_meter = ttk.Progressbar(vu_frame, length=380, maximum=100)
        self.in_meter.grid(row=0, column=1, **pad)

        ttk.Label(vu_frame, text="Çıkış:").grid(row=1, column=0, sticky="w", **pad)
        self.out_meter = ttk.Progressbar(vu_frame, length=380, maximum=100)
        self.out_meter.grid(row=1, column=1, **pad)

        # ---- Kontrol butonları ----
        ctrl_frame = ttk.Frame(self.root)
        ctrl_frame.grid(row=3, column=0, sticky="ew", **pad)

        self.start_btn = ttk.Button(ctrl_frame, text="▶ Başlat", command=self._toggle)
        self.start_btn.grid(row=0, column=0, **pad)

        self.analyze_btn = ttk.Button(ctrl_frame, text="🔬 Analiz Et (spektrum)",
                                      command=self._analyze)
        self.analyze_btn.grid(row=0, column=1, **pad)

        self.status_lbl = ttk.Label(ctrl_frame, text="Durum: Durdu", foreground="gray")
        self.status_lbl.grid(row=0, column=2, **pad)

        # ---- Spektrum grafiği (matplotlib embed) ----
        plot_frame = ttk.LabelFrame(self.root, text="4) Spektrum Analizi")
        plot_frame.grid(row=4, column=0, sticky="nsew", **pad)

        self.fig = Figure(figsize=(6.2, 2.6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("Frekans (Hz)")
        self.ax.set_ylabel("Genlik (dB)")
        self.ax.set_title("Analiz için 'Analiz Et' butonuna bas")
        self.ax.grid(True, alpha=0.3)
        self.fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def _select_default_devices(self):
        """Varsayılan giriş = sistem varsayılan mik; çıkış = VB-Cable (varsa)."""
        try:
            default_in = sd.default.device[0]
        except Exception:
            default_in = None

        # Giriş: sistem varsayılanı, yoksa ilk eleman
        if self.input_devices:
            chosen = self.input_devices[0][1]
            for idx, lbl in self.input_devices:
                if default_in is not None and idx == default_in:
                    chosen = lbl
                    break
            self.in_combo.set(chosen)

        # Çıkış: ismi "CABLE Input" içeren cihazı tercih et (VB-Audio Virtual Cable)
        if self.output_devices:
            chosen = self.output_devices[0][1]
            for _, lbl in self.output_devices:
                if "cable input" in lbl.lower():
                    chosen = lbl
                    break
            self.out_combo.set(chosen)

    # ------------------------------------------------------------- Filtre olayları
    def _current_notches(self):
        """GUI'deki güncel değerlerden notch listesi üret."""
        notches = []
        for i, n in enumerate(config.NOTCHES):
            notches.append({
                "freq": n["freq"],
                "q": float(self.q_vars[i].get()),
                "enabled": bool(self.enabled_vars[i].get()),
            })
        return notches

    def _apply_filters(self):
        self.engine.update_filters(self._current_notches())

    def _on_q_change(self, idx):
        # Slider hareket ederken filtreleri canlı güncelle (iirnotch ucuzdur)
        self._apply_filters()

    # ------------------------------------------------------------- Başlat / Durdur
    def _toggle(self):
        if self.engine.running:
            self.engine.stop()
            self.start_btn.config(text="▶ Başlat")
            self.status_lbl.config(text="Durum: Durdu", foreground="gray")
            return

        in_lbl = self.in_combo.get()
        out_lbl = self.out_combo.get()
        if in_lbl not in self.in_map or out_lbl not in self.out_map:
            messagebox.showerror("Hata", "Lütfen geçerli giriş ve çıkış cihazı seç.")
            return

        in_idx = self.in_map[in_lbl]
        out_idx = self.out_map[out_lbl]
        block = int(self.block_combo.get())

        # Başlamadan önce güncel filtreleri yükle
        self.engine.update_filters(self._current_notches())

        try:
            self.engine.start(in_idx, out_idx, block_size=block)
        except Exception as e:
            messagebox.showerror("Akış başlatılamadı", str(e))
            return

        self.start_btn.config(text="■ Durdur")
        self.status_lbl.config(text="Durum: Çalışıyor", foreground="green")

    # ------------------------------------------------------------- Analiz
    def _analyze(self):
        """Kısa kayıt al ve spektrumu çiz (kayıt arka planda, çizim ana thread'de)."""
        in_lbl = self.in_combo.get()
        if in_lbl not in self.in_map:
            messagebox.showerror("Hata", "Lütfen geçerli bir giriş cihazı seç.")
            return
        in_idx = self.in_map[in_lbl]

        self.analyze_btn.config(state="disabled")
        self.status_lbl.config(text="Durum: Analiz için kayıt alınıyor...", foreground="blue")

        def worker():
            try:
                freqs, magdb, peaks = analyzer.analyze(device=in_idx, verbose=True)
            except Exception as e:
                self.root.after(0, lambda: self._analyze_error(e))
                return
            self.root.after(0, lambda: self._plot_spectrum(freqs, magdb, peaks))

        threading.Thread(target=worker, daemon=True).start()

    def _analyze_error(self, e):
        self.analyze_btn.config(state="normal")
        self.status_lbl.config(text="Durum: Analiz hatası", foreground="red")
        messagebox.showerror("Analiz hatası",
                             f"{e}\n\nİpucu: Akış çalışıyorsa önce 'Durdur'a bas; "
                             f"bazı cihazlar aynı anda iki kez açılamaz.")

    def _plot_spectrum(self, freqs, magdb, peaks):
        fmax = config.ANALYZE_MAX_FREQ
        mask = freqs <= fmax
        self.ax.clear()
        self.ax.plot(freqs[mask], magdb[mask], lw=0.8)
        self.ax.set_xlabel("Frekans (Hz)")
        self.ax.set_ylabel("Genlik (dB)")
        self.ax.set_title("Ölçülen Spektrum (düşük frekans bölgesi)")
        self.ax.grid(True, alpha=0.3)

        # 50 Hz harmoniklerini dikey çizgiyle işaretle
        for h in (50, 100, 150, 200):
            if h <= fmax:
                self.ax.axvline(h, color="red", ls="--", lw=0.6, alpha=0.5)

        # En belirgin birkaç tepeyi etiketle
        for fr, mg in peaks[:5]:
            if fr <= fmax:
                self.ax.annotate(f"{fr:.0f}Hz", xy=(fr, mg),
                                 xytext=(0, 6), textcoords="offset points",
                                 fontsize=8, ha="center", color="darkred")

        self.fig.tight_layout()
        self.canvas.draw()

        self.analyze_btn.config(state="normal")
        top = ", ".join(f"{fr:.0f}Hz" for fr, _ in peaks[:3]) or "yok"
        self.status_lbl.config(text=f"Durum: Analiz tamam (en güçlü: {top})",
                               foreground="black")

    # ------------------------------------------------------------- VU metre döngüsü
    def _schedule_meter_update(self):
        self.in_meter["value"] = rms_to_pct(self.engine.input_level)
        self.out_meter["value"] = rms_to_pct(self.engine.output_level)
        # ~50 ms'de bir güncelle
        self.root.after(50, self._schedule_meter_update)

    # ------------------------------------------------------------- Kapanış
    def _on_close(self):
        try:
            self.engine.stop()
        finally:
            self.root.destroy()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
