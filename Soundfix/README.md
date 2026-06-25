# SoundFix — Gerçek Zamanlı Mikrofon Hum / Şebeke Gürültüsü Filtresi

Windows'ta mikrofonundan gelen sesi alır, **50 Hz ve harmonikleri (100/150/200 Hz)**
için dar bant (narrow-band) IIR **notch (çentik)** filtreleriyle temizler ve temizlenmiş
sesi bir **sanal mikrofona** (VB-Audio Virtual Cable) yönlendirir. Böylece
Discord / OBS / Zoom gibi programlar temiz sesi kullanabilir.

```
[Gerçek Mikrofon] → [SoundFix: notch filtreler] → [CABLE Input] ⇒ [CABLE Output] → [Discord/OBS/Zoom]
```

> Bu döküman **iki ayrı senaryoyu** kapsar:
> - **Mikrofon (giriş) hum'ı** → bu Python uygulaması (`gui.py`). Aşağıdaki bölümler.
> - **Hoparlör (çıkış) cızırtısı / ground loop** → **Equalizer APO** önerilir.
>   Bkz. **[EqualizerAPO_KULLANIM.md](EqualizerAPO_KULLANIM.md)** ve [hızlı özet aşağıda](#çıkış-hoparlör-tarafını-temizlemek).

---

## Çıkış (hoparlör) tarafını temizlemek

Jack çıkışına takılı hoparlörde cızırtı/uğultu varsa (ground loop), **en doğru yazılım
çözümü Equalizer APO'dur** — sistem geneli çalışır ve neredeyse gecikmesizdir.
Adım adım kurulum ve hazır filtre dosyası: **[EqualizerAPO_KULLANIM.md](EqualizerAPO_KULLANIM.md)**
+ **[EqualizerAPO_config.txt](EqualizerAPO_config.txt)**.

> ⚠️ **Dürüst sınır:** Hiçbir yazılım (EAPO dahil), sesi DAC'tan sonra kabloda eklenen
> *saf analog* ground loop hum'ını silemez — yazılım yalnızca dijital sinyale dokunur.
> **Test:** Filtreyi açıp hiçbir şey çalmadan sesi yükselt; cızırtı hâlâ varsa analogtur,
> ₺150–400'lük bir **ground loop isolator** kesin çözümdür. Azaldıysa gürültünün dijital
> kısmı varmış, yazılım işe yaramıştır.

**Bu Python uygulamasıyla çıkış tarafını denemek (alternatif, gecikmeli):**
Uygulama genel bir `giriş → filtre → çıkış` hattı olduğu için cihaz rollerini ters çevir:
1. Windows'ta **varsayılan oynatma cihazını "CABLE Input"** yap (tüm sistem sesi kabloya gider).
2. `gui.py`'de **Giriş = "CABLE Output"**, **Çıkış = gerçek hoparlörün (jack)** seç.
3. Notch filtreler artık sistem sesine uygulanır. (VB-Cable round-trip gecikme ekler;
   video izliyorsan EAPO'yu tercih et.)

---

## 1) Kurulum

### a) Python kütüphaneleri

```powershell
pip install sounddevice numpy scipy matplotlib
```

> `tkinter` Python ile birlikte gelir (python.org kurulumunda dahildir), ayrıca kurmana gerek yok.

Hepsini tek seferde:

```powershell
pip install -r requirements.txt
```

### b) VB-Audio Virtual Cable (sanal ses cihazı)

Temizlenmiş sesi başka programlara "mikrofon" olarak verebilmek için bir sanal ses
kablosu gerekir.

1. https://vb-audio.com/Cable/ adresine git, **VBCABLE_Driver_Pack** ZIP'ini indir.
2. ZIP'i çıkar, **`VBCABLE_Setup_x64.exe`** dosyasına **sağ tık → Yönetici olarak çalıştır**.
3. **Install Driver**'a bas ve **bilgisayarı yeniden başlat**.

Kurulumdan sonra iki yeni cihaz görürsün — **bu ikisini karıştırma**:

| Cihaz | Türü | SoundFix'te ne için |
|---|---|---|
| **CABLE Input** (VB-Audio Virtual Cable) | Çalma (playback / hoparlör) | **SoundFix'in ÇIKIŞI** — temiz sesi buraya yazarız |
| **CABLE Output** (VB-Audio Virtual Cable) | Kayıt (recording / mikrofon) | **Discord/OBS** bunu **mikrofon** olarak seçer |

Yani veri akışı: SoundFix → **CABLE Input** → (kablo) → **CABLE Output** → Discord.

> İsteğe bağlı: VB-Cable'ın örnekleme frekansını Windows ses ayarlarından 48000 Hz
> yapman, `config.py` içindeki `SAMPLE_RATE = 48000` ile uyumlu olur.

---

## 2) Kullanım

### Adım 1 — Önce parazit frekansını ölç (Analiz / Tespit modu)

Gerçek hum frekansını ölçmek için (Türkiye'de 50 Hz beklenir ama doğrulamak iyidir):

**GUI'den:** `python gui.py` → giriş cihazını seç → **🔬 Analiz Et** butonuna bas.
Spektrum grafiği çizilir; en güçlü tepe frekanslar grafikte ve konsolda gösterilir.

**Komut satırından (ayrı script):**

```powershell
python analyzer.py            # sistem varsayılan mikrofon
python analyzer.py 3          # cihaz index'i 3 olan mikrofon
```

Cihaz index'lerini görmek için:

```powershell
python -m sounddevice
```

En güçlü tepe 50'nin katı değilse (örn. 60 Hz çıktıysa), `config.py` içindeki notch
`freq` değerlerini ölçülen değere göre güncelle.

### Adım 2 — Gerçek zamanlı filtreyi çalıştır

```powershell
python gui.py
```

Arayüzde:

1. **Giriş (Mikrofon):** gerçek mikrofonunu seç.
2. **Çıkış (Sanal Kablo):** **CABLE Input (VB-Audio Virtual Cable)** seç
   (program bunu otomatik bulup seçmeye çalışır).
3. **Blok boyutu:** gecikme/stabilite dengesi (256 düşük gecikme, 1024 daha stabil).
4. İstediğin notch filtrelerini **aç/kapat**, **Q** slider'ı ile bant darlığını ayarla.
5. **▶ Başlat**'a bas. Giriş/çıkış **VU metrelerinden** sesin aktığını görürsün.

### Adım 3 — Hedef programı ayarla

Discord / OBS / Zoom içinde **mikrofon** olarak
**CABLE Output (VB-Audio Virtual Cable)** seç. Artık temizlenmiş sesi duyarlar.

---

## 3) Ayarlar (`config.py`)

| Ayar | Açıklama |
|---|---|
| `SAMPLE_RATE` | Örnekleme frekansı (VB-Cable ile uyumlu: 48000) |
| `BLOCK_SIZE` | Blok boyutu — küçük = düşük gecikme, büyük = stabil |
| `OUTPUT_CHANNELS` | Çıkış kanal sayısı (sanal kablo için genelde 2) |
| `LATENCY` | `'low'` / `'high'` veya saniye (örn. `0.02`) |
| `NOTCHES` | Her filtre için `freq`, `q`, `enabled` |
| `Q_MIN` / `Q_MAX` | GUI'deki Q slider sınırları |

**Q faktörü:** Yüksek Q = daha **dar** bant = sese daha az zarar, ama frekansı tam
tutturman gerekir. Frekans kayıyorsa veya tam emin değilsen Q'yu düşür (daha geniş bant).

---

## 4) Dosya yapısı

| Dosya | Görev |
|---|---|
| `config.py` | Tüm ayarlar ve notch tanımları |
| `dsp.py` | Notch filtre bankası (IIR / SOS, bloklar arası durum korumalı) |
| `engine.py` | Gerçek zamanlı ses motoru (sounddevice akışı + seviye ölçümü) |
| `analyzer.py` | Tespit/analiz modu (FFT spektrum + tepe bulma) — ayrıca tek başına çalışır |
| `gui.py` | tkinter arayüzü — **uygulamanın giriş noktası** |
| `requirements.txt` | Python bağımlılıkları |

---

## 5) Sorun giderme

- **Ses çıtırdıyor / kesiliyor:** Blok boyutunu büyüt (512 → 1024), `LATENCY='high'` dene.
  Farklı giriş/çıkış cihazlarının saatleri (clock) farklı olduğundan çok küçük bloklarda
  ufak çatlamalar olabilir.
- **"Analiz hatası" / cihaz açılamadı:** Akış çalışıyorken analiz yaparsan bazı cihazlar
  aynı anda iki kez açılamayabilir — önce **■ Durdur**'a bas, sonra analiz et.
- **Çıkış cihazı listede yok:** VB-Cable kurulumundan sonra bilgisayarı yeniden başlattığından
  emin ol.
- **Örnekleme frekansı hatası:** Mikrofon veya kablo 48000 Hz desteklemiyorsa
  `config.py` içindeki `SAMPLE_RATE` değerini cihazın desteklediği değere çek
  (örn. 44100).
- **Hum hâlâ var:** Önce `analyzer.py` ile gerçek tepe frekansını ölç; 50 Hz yerine
  başka bir değerse (örn. 49.9 / 60 Hz) `config.py`'deki `freq`'i düzelt. Tepe tam
  oturmuyorsa Q'yu biraz düşür.

> Not: Notch filtreler **sabit tonlu** (50 Hz hum gibi) parazitler için idealdir.
> Geniş bant "tıss" (hiss) gürültüsünü azaltmaz; onun için ayrıca spektral gürültü
> azaltma (noise gate / RNNoise vb.) gerekir.
