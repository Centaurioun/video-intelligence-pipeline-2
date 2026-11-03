# A-12 / P-11 — S5 için dar kapsamlı sözleşme değişikliği

**Karar durumu:** Owner tarafından onaylanan kapsam değişikliği; bu belgeyle kalıcı kayda alınmak üzere sunulmuştur. S5 uygulama planı ve kaynak kodu için ayrı yetkilendirme gerekir.

**Karar tarihi:** 2026-10-28  
**Karar tabanı:** `main@1d1355aed506226c7f9a1450921afd436f0542a6`  
**Kapsam:** Yalnızca Gate-3 A-7 S5 ReviewBundle tüketiminde sınırlı stream identity yeniden doğrulaması.

## Owner kararı

Seçenek A kabul edilmiştir. A-12 / P-11, aşağıda belirtilen dar ve S5’e özel tüketim doğrulamasını kapsayacak şekilde değiştirilmiştir.

ReviewBundle tüketim noktasında, S2/S3 tarafından kabul edilen stream identity kuralını yeniden uygulamak için, adı ve beklenen SHA-256 özeti doğrulanan kaynak dosyanın tam baytlarının okunmasına izin verilir. İnceleme yalnız stream identity için gereken ISO-BMFF yapısal metadata ile sınırlıdır: `moov/trak/tkhd` ve video handler için `trak/mdia/hdlr`.

Kaynak baytlarının SHA-256 doğrulaması, kimlik metadata’sı çıkarılan aynı bayt dizisi üzerinde yapılmalıdır. Uygulama planı dosya boyutu, bellek ve işlem sınırlarını belirlemeli; sınır dışındaki kaynaklar okunmadan fail-closed reddedilmelidir. Limit değerleri uygulama planında gerekçelendirilip sentetik testlerle doğrulanmalıdır; bu karar sayısal limit belirlemez.

Bu izin yalnız A-7 S5 ReviewBundle tüketim denetimi içindir.

## Değiştirilemeyecek sınırlar

- Ek FFprobe veya FFmpeg çalıştırması yapılamaz.
- Kaynak-native zamanlama tabloları yeniden parse edilemez.
- Yeni PTS/timebase hesabı veya edit boundary üretilemez.
- Source/probe digest uyuşmazlığında, artifact eksikliğinde, yapısal belirsizlikte veya pozisyonel eşleşme başarısızlığında işlem fail-closed kalır.
- Stream index ile ISO-BMFF track arasında tahminî, ordinal, sayım-eşitliği veya box-order tabanlı eşleşme kurulamaz. Yalnız kabul edilmiş S2/S3 pozisyonel kimlik kuralı geçerlidir.
- `PRODUCER_SEALED` bağımsız probe-source eşleşme kanıtı olarak sunulamaz. `demuxer_build_state=NOT_OBSERVED` korunur.
- Yeni kanıt alanı, şema, receipt veya sealed kayıt değişikliği yapılamaz.
- Tarihsel V1/V2/V3 ReviewBundle kayıtları değiştirilemez. Mevcut yükleme semantiğiyle doğrulanabilen kayıtlar okunabilir kalabilir; ancak identity doğrulaması yapılamayan kayıtlar bağlayıcı tüketim veya editoryal kabul yetkisi kazanamaz.
- Kaynak-native PTS/timebase, zaman sınırları için tek otorite olmayı sürdürür. Bu karar zamanlama veya edit listesi davranışını değiştirmez.
- S4’ün bağlama anındaki kontrolü ve mevcut fail-closed negatif yolları korunur.

## Kararın dayanağı

Mevcut P-11/A-12 kaydı, tüketim zamanı kontrolünü digest/verbatim-binding yeniden doğrulamasıyla sınırlar. S5 planı ise ReviewBundle tüketiminde ek `moov/trak/tkhd` kaynak metadata okuması ister. Bu kayıt, yalnızca bu metadata yeniden okumasını S5 için açıkça kapsayarak sözleşme çelişkisini giderir.

Bu karar, S2/S3/S4 kanıtının gücünü artırmaz. S2 identity sonucu kalıcı bir alan olarak saklanmıyor; S4’teki `PRODUCER_SEALED` eşleşme iddiası bağımsız tüketici kanıtı değildir. Metadata yeniden doğrulaması da bu sınırı kaldırmaz.

İlgili kayıtlar:

- [A-7 P2 Governance Reconciliation](2026-10-28-a7-p2-governance-reconciliation.md)
- [A-7 Cross-Contract Integration Readiness](2026-10-25-g3-a7-cross-contract-integration-readiness.md)
- [A-7 Stream Identity Mapping Implementation Plan](../superpowers/plans/2026-10-25-g3-a7-stream-identity-mapping-implementation-plan.md)
- [Authority Disposition Matrix](../agent-runs/2026-10-25-g3-cprime-v1/authority-disposition-matrix.md)

## Bu kararın vermediği yetkiler

Bu sözleşme değişikliği tek başına aşağıdakileri yetkilendirmez:

- S5 uygulama planı hazırlamak veya yürütmek;
- kaynak kodu, test, schema, receipt, evidence veya sealed kayıt değiştirmek;
- gerçek/protected medya çalıştırmak;
- FFmpeg/FFprobe, model veya provider çağırmak;
- export/production işlemi yapmak;
- Gate promotion yapmak.

Bir sonraki adım, yalnız bu kararı kalıcı kayda alan ve ayrıca incelenecek dokümantasyon PR’ıdır. S5’in ayrıntılı uygulama planı ve kaynak kodu çalışması ayrı yetkilendirmeye tabidir.
