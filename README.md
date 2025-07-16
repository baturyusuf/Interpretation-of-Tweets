# 🐦 Interpretation of Tweets

Bu proje, afet anlarında (örneğin depremler) paylaşılan tweetlerin içeriğini anlamlandırmak, sınıflamak ve etiketlemek amacıyla geliştirilmiştir. Amaç; **afetzedeler, kurtarma ekipleri, siviller ve görevli personel** gibi farklı gruplardan gelen bilgileri ayrıştırmak ve karar vericilere anlamlı veri sunmaktır.

## 🎯 Amaç

- Afet sırasında sosyal medya verilerini analiz etmek
- Tweet içeriklerini tematik, olay bazlı ve işlevsel başlıklara ayırmak
- Kullanıcı arayüzü üzerinden kolay görüntüleme, filtreleme ve yapay zeka ile etiketleme yapmak

---

## 💻 Teknolojiler

- `Python`
- `Streamlit` – kullanıcı arayüzü
- `Pandas` – veri işleme
- `st-aggrid` – etkileşimli tablo bileşeni
- `OpenAI API` (veya özelleştirilmiş AI modelleri) – otomatik etiketleme

---

## 📁 Girdi Formatı

Proje, `.xlsx` formatında bir tweet veri dosyası bekler.

### Beklenen sütunlar:
- **Kodlu Bölümler** – tweet metni
- **Belge** – sıra numarası/id
- **Belge grubu** – kullanıcı profili (resmî, sivil vs.)
- **Determination of Events** – olay türü (örn. hasar, yardım çağrısı)
- **Tematik Analiz** – içerik başlığı (örn. sağlık, ulaşım)
- **Kabiliyet** – tweet’in yansıttığı ihtiyaç/kabiliyet (örn. su ihtiyacı)
- **Site Visit** – saha ziyareti bilgisi
- **Binary** – belirli ikili sınıflamalar (örn. doğrulanmış: 1/0)

---

## 🚀 Nasıl Çalıştırılır?

```bash
# Gerekli paketleri yükleyin
pip install -r requirements.txt

# Uygulamayı başlatın
streamlit run "src\app.py"
