# CY Snake Game

WearOS cihazları için yuvarlak ekran desteği olan basit bir yılan oyunu.

## Özellikler

- **Yuvarlak ekran desteği**: Ekran boyutuna göre ızgara oluşturur
- **Yeşil pixel yılan** ve **kırmızı pixel elma**
- **Siyah arka plan**
- **Duvar yok**: Karşıya ışınlanma
- **Kendine değdiğinde ölüm**
- **Puan ve süre gösterimi**
- **Tıklayınca başlatma**
- **Sağa/sola kaydırma engellendi** (sadece düğme ile çıkış)
- **Responsive tasarım** küçük ekranlar için

## Derleme

1. Gradle wrapper jar'ı indirin:
   ```
   cd gradle/wrapper
   # Bu URL'den indirin: https://github.com/gradle/gradle/raw/v8.2.0/gradle/wrapper/gradle-wrapper.jar
   ```

2. Projeyi build edin:
   ```bash
   .\gradlew build
   ```

## Dağıtım

Cihazı bağlayın ve yükleyin:
```bash
adb connect 192.168.1.112:38281
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

## Oyun Kontrolleri

- **Başlatma**: Ekrana dokunun
- **Yön değiştirme**: Ekrana dokunarak yönü değiştir (merkezden uzaklaştıkça yön değişir)
- **Yeniden başlatma**: Game over olduğunda ekrana dokun
- **Çıkış**: Sadece cihaz düğmesi ile çıkılabilir

## Teknik Detaylar

- Kotlin + Android Compose
- WearOS optimize edilmiş
- Yuvarlak ekran uyumlu
- Daha iyi oyun deneyimi için kaydırma hareketleri devre dışı
