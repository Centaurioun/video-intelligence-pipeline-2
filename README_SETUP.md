# Video Intelligence Pipeline (VIP) — Environment Setup Guide

Bu belge, **Video Intelligence Pipeline** projesinin Python çalışma ortamının sıfırdan kurulması, izole sanal ortam (venv) yapılandırması, bağımlılıkların yönetimi ve `PYTHONPATH` tanımlamaları için gereken adımları içerir.

---

## 1. Ön Koşullar

* **İşletim Sistemi:** Linux (Ubuntu 22.04+ / Debian 12+) veya macOS
* **Python Sürümü:** Python 3.10.12 veya üzeri (Önerilen: Python 3.10 veya 3.11)
* **Sistem Paketleri:**
  Debian/Ubuntu sistemlerde `venv` ve `pip` modüllerinin sistem düzeyinde bulunması gerekebilir:
  ```bash
  sudo apt-get update
  sudo apt-get install -y python3-venv python3-pip
  ```

---

## 2. İzole Sanal Ortam (Virtual Environment) Kurulumu

Proje bağımlılıklarını sistem paketlerinden izole etmek ve deterministik çalışma ortamı sağlamak için proje kök dizininde bir sanal ortam oluşturulmalıdır:

```bash
# Proje kök dizinine geçin
cd /path/to/video-intelligence-pipeline

# .venv adında izole bir sanal ortam oluşturun
python3 -m venv .venv

# Sanal ortamı etkinleştirin (Linux / macOS)
source .venv/bin/activate

# Pip'i en güncel sürüme yükseltin
pip install --upgrade pip
```

> **Not (ensurepip bulunmayan yalın sistemler için):**
> Eğer sisteminizde `ensurepip` yüklü değilse, sanal ortam `--without-pip` bayrağı ile oluşturulabilir:
> ```bash
> python3 -m venv --without-pip .venv
> curl -sS https://bootstrap.pypa.io/get-pip.py | .venv/bin/python
> ```

---

## 3. Bağımlılıkların Kurulumu (`requirements.txt`)

Proje kapsamında Gate-0 kilit dosyası `requirements/gate0.lock` altında kilitlenmiştir. Geliştirme ve test süreçleri için asgari bağımlılıkları içeren bir `requirements.txt` dosyası oluşturabilir veya doğrudan mevcut kilit dosyasından kurulum yapabilirsiniz:

### Seçenek A: Mevcut Kilit Dosyasından Kurulum
```bash
pip install -r requirements/gate0.lock
pip install numpy
```

### Seçenek B: `requirements.txt` Dosyası ile Kurulum
Kök dizinde aşağıdaki içeriğe sahip bir `requirements.txt` bulunuyorsa:
```text
pytest==8.3.3
numpy>=1.24.0
```

Kurulumu şu komutla gerçekleştirin:
```bash
pip install -r requirements.txt
```

---

## 4. `PYTHONPATH` Yapılandırması

Video Intelligence Pipeline mimarisi, çekirdek uygulama modüllerini `src/` dizini altında, deneysel ve indeksleme bileşenlerini ise `experiments/` dizini altında barındırır. Modüllerin (`vip_fvs`, `persistent_local_index` vb.) doğru şekilde çözümlenebilmesi için her iki dizin de `PYTHONPATH` ortam değişkenine eklenmelidir.

### Geçici / Terminal Oturumu İçin:
```bash
export PYTHONPATH="$PWD/src:$PWD/experiments"
```

### Kalıcı Yapılandırma (Sanal Ortam Aktivasyonuna Entegre):
Sanal ortam her etkinleştirildiğinde otomatik olarak `PYTHONPATH` atanması için `.venv/bin/activate` dosyasının sonuna ekleyebilirsiniz:
```bash
echo 'export PYTHONPATH="$VIRTUAL_ENV/../src:$VIRTUAL_ENV/../experiments"' >> .venv/bin/activate
```

---

## 5. Kurulumun Doğrulanması (Verification)

Ortamın ve bağımlılıkların eksiksiz kurulduğunu doğrulamak için aşağıdaki adımları çalıştırın:

### 1. Modül İçe Aktarım Denetimi
```bash
python3 -c "
import sys, os
sys.path.insert(0, os.path.abspath('src'))
sys.path.insert(0, os.path.abspath('experiments'))

modules = [
    'vip_fvs.cli',
    'vip_fvs.coordinator',
    'vip_fvs.local_semantic',
    'persistent_local_index.model_profile',
    'persistent_local_index.embedding'
]

for m in modules:
    __import__(m)
    print(f'OK: {m}')
"
```
Beklenen çıktı: Tüm modüllerin `OK` olarak listelenmesi.

### 2. Entegrasyon Testinin Çalıştırılması
```bash
PYTHONPATH="$PWD/src:$PWD/experiments" pytest tests/vip_fvs/integration/test_product_index_query.py -v
```
Beklenen sonuç: Test paketinin (`test_product_index_query.py`) tüm test senaryolarının başarıyla geçmesi (`PASSED`).

### 3. Çalışma Alanı Bütünlük Doğrulaması (İsteğe Bağlı)
```bash
./scripts/verify-workspace.sh
```

---

## 6. Güvenlik ve Mimari İlkeler

* **Kaynak Medya Dokunulmazlığı:** Kaynak video ve ses dosyaları asla yerinde değiştirilmez, dönüştürülmez (transcode edilmez) veya silinmez.
* **Sahte (Synthetic) vs. Gerçek Veri:** Testler sahte (injected/fake) motorlar ve sentetik verilerle yürütülür; bu testlerin başarısı model doğruluğu veya üretim ölçeği başarısı anlamına gelmez.
* **Gizlilik ve Egress:** `.env.local`, API anahtarları veya gerçek medya verileri sürümlere dahil edilmez.
