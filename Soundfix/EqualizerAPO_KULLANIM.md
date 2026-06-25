# Çıkış (Hoparlör) Tarafını Yazılımla Temizleme — Equalizer APO

Bu, **ses çıkışını** (jack'e taktığın hoparlörün cızırtısını) yazılımla bastırmak için
**en doğru araçtır**. Çünkü:

- **Sistem geneli** çalışır (her programın sesine uygulanır, ayrı yönlendirme gerekmez).
- **Gecikme yok denecek kadar azdır** (Windows ses motorunun içine APO olarak girer) →
  film/video/oyun ses-görüntü senkronu bozulmaz. (Bizim Python aracı VB-Cable üzerinden
  gittiği için gecikme ekler; çıkış için EAPO daha iyidir.)
- Ücretsiz ve açık kaynaktır.

---

## ⚠️ Önce şunu bil (dürüst sınır)

Equalizer APO dahil **hiçbir yazılım**, sesi bilgisayardan çıkıp **DAC'tan sonra**
kabloda eklenen saf analog ground loop hum'ını silemez — çünkü yazılım sadece
**DAC'tan önceki dijital sinyale** dokunabilir.

**Belirleyici test:** EAPO'yu kurup filtreleri ekledikten sonra **hiçbir şey çalmadan**
hoparlör sesini aç.
- Cızırtı **hâlâ varsa** → %100 analog, yazılım çözmez → **ground loop isolator** (₺150–400) tek gerçek çözüm.
- Cızırtı **azaldıysa** → gürültünün bir kısmı dijitalmiş, EAPO işe yaradı, ayarı koru.

Yani: EAPO'yu denemek 5 dakika ve bedava; test sana kesin cevabı verir.

---

## Kurulum (adım adım)

1. **İndir:** https://sourceforge.net/projects/equalizerapo/ → en güncel sürüm.
2. Kurulumu çalıştır. Kurulum sonunda **Configurator** açılır:
   - **Playback** sekmesinde, hoparlörünün bağlı olduğu **çıkış cihazını** (jack /
     Realtek Speakers) **işaretle**. (Mikrofon değil! Bu sefer çıkış.)
3. **Bilgisayarı yeniden başlat** (APO'nun yüklenmesi için şart).

## Filtreleri uygula

**Kolay yol (dosyayı kopyala):**
1. Bu klasördeki `EqualizerAPO_config.txt` dosyasını şuraya kopyala:
   `C:\Program Files\EqualizerAPO\config\`
2. `C:\Program Files\EqualizerAPO\config\config.txt` dosyasını Not Defteri ile aç
   (yönetici olarak), en alta şu satırı ekle ve kaydet:
   ```
   Include: EqualizerAPO_config.txt
   ```
   Değişiklik anında etkilidir (yeniden başlatmaya gerek yok).

**Grafik yol (Editor.exe):**
1. `C:\Program Files\EqualizerAPO\Editor.exe` aç.
2. Üstte doğru **çıkış cihazını** seç.
3. `+` → **Filters → Notch filter** ekle, `Frequency = 50`, `Q = 30` yap.
4. Aynısını 100 / 150 / 200 Hz için tekrarla.
5. Anlık duyarak Q'yu ayarla (hum tam gitmiyorsa Q'yu düşür = daha geniş bant).

---

## Geniş bant cızırtı / "tıss" da varsa (sadece 50 Hz değil)

Notch filtreler yalnızca **sabit tonlu** hum'u (50/100/150 Hz) keser. Genel bir
"cızzz/tıss" varsa, gürültü profilini öğrenip çıkaran **ReaFIR** (Reaper'ın ücretsiz
ReaPlugins paketinde, "Subtract" modu) EAPO içine VST olarak eklenebilir:

1. Reaper ReaPlugins'i kur (ReaFIR ücretsizdir).
2. EAPO config'e: `Plugin: ReaFIR_standalone ...` yerine Editor'de `+ → Plugins → VST plugin`
   ile **ReaFIR**'i ekle, **Mode: Subtract**, **Automatically build noise profile** işaretli
   iken birkaç saniye sadece gürültüyü "dinlet", sonra işareti kaldır → o profil çıkarılır.

> Not: ReaFIR de DAC'tan önce çalışır; analog ground loop'a yine dokunamaz, ama
> dijital zincirdeki geniş bant gürültüyü gerçekten azaltır.

---

## Kaldırmak istersen

`config.txt` içindeki eklediğin satırı sil veya Configurator'dan cihazın işaretini kaldır.
