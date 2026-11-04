# MEGA-17 kanonik VIP taşınabilirlik karar matrisi

Denetim tarihi: 2026-11-05. LAB `main`: `1fd14c0b246c8da97e07129f6b84173d86f6a500`. Kanonik VIP `main` **yalnızca okundu** (`bee314b92981b9ae7ea38d83fe2dbae120c474e4`). PR #258/#259 başlıkları güncel remote ref'lerden alındı. Amaç kod taşımak değil; LAB kanıtını kanonik sözleşmelere göre sınıflandırmaktır.

Durum etiketleri görev belgesindeki kontrollü değerlerdir: `ALREADY_CANONICAL`, `EXACT_DUPLICATE_DO_NOT_IMPORT`, `LAB_ONLY_SYNTHETIC_HARNESS`, `CANONICAL_ADAPTER_CANDIDATE`, `CONFLICTS_WITH_OPEN_CANONICAL_PR`, `BLOCKED_BY_UNRESOLVED_AUTHORITY`, `NOT_OBSERVED`.

## Döngü 1–2: Kaynak ve sözleşme eşleşmesi

| Aday bileşen / yollar | LAB ve kanonik durum | Üretici/tüketici ve doğrulanan örtüşme | Karar / gerekçe |
|---|---|---|---|
| `src/vip_lab/mega03..17/**`, `tests/vip_lab/test_mega*.py` | LAB-specific; kanonik main'de aynı VIP Lab wave bulunmuyor | Dalgalar LAB task/harness içinde birbirine bağlanıyor; kanonik Gate-0/1/2/3 kodları ayrı otoriter sözleşmeleri uyguluyor | `LAB_ONLY_SYNTHETIC_HARNESS`. Toplu kopyalama reddedildi; hazır olma raporu gerçek ürün/gate implementasyonu sayılmaz. |
| Gate-0 query/arm readiness: `src/vip_lab/mega17/gate0_readiness.py`, `source_readiness.py` | LAB üretici `1fd14c0b…`; kanonik Gate-0 sözleşme main'de mevcut | Sözleşme 24 pozitif, 8 absent, 8 geliştirme sorgusu; iki reviewer; metadata baseline + tek yerel semantic-visual kol; Hit@10 ≥20/24, paired lift ≥5/24, aile başına ≥3/6. Üç SigLIP profili Gate-1 kapsamı. | `LAB_ONLY_SYNTHETIC_HARNESS`. Değerli olan yalnız sözleşme eşlemesi; canonical Gate-0 implementation'a taşıma gerekmiyor. AI Studio'nun 50-video / Hit@5 / dört kol anlatısı kanonik değil; güncel kod/test beklentisi bu yanlış anlatıyı uygulamıyor. |
| Synthetic scenario/queue lineage: `mega14/scenario.py`, `mega15/16`, `mega17/orchestrator.py` | LAB-only gerçek `SyntheticLabScenario`; Gate producer/report modelinden ayrıdır | MEGA-17 senaryoyu `run_mega15_16_offline_pipeline(scenario=scen)` ile geçiriyor; query/source/arm üyeliği, revision ve occurrence kimliği ile digest kontrolü E2E'de testli. | `LAB_ONLY_SYNTHETIC_HARNESS`. Kopya değil, canonical interface portu da değil. Yalnızca bu suite'in testlerinden fikir alınabilir; gerçek product lineage'ı kanıtlamaz. |
| Source-readiness ve fixture claims: `mega17/source_readiness.py` | LAB sentetik D-2 schema fixture; gerçek byte admission değil | Statik prerequisite inventory dışında source guard, S5 admission, E01 seam veya sealed review bundle API çağrısı yok. Kanonik main'de aranan fonksiyon isimleri bulunmadı. | `LAB_ONLY_SYNTHETIC_HARNESS`; `NOT_OBSERVED` real admission. Gerçek D-2 Owner input'ları, source discovery/processing permission ve D-3 yürütme ayrı. |
| Kanonik media byte admission / S5-T1 | PR #258 `5a60cd8e…`: yeni `src/vip_fvs/_bounded_admission_fs.py`, `src/vip_fvs/bounded_admission.py`, `tests/vip_fvs/unit/test_bounded_admission.py`; PR draft/open | Kanonik PR, descriptor-relative bounded synthetic file admission API ekliyor; MEGA-17 source readiness bu modülleri kullanmıyor. PR refactor boundary'si 353 satır FS primitive + public API ve kapsamlı testler. | `CONFLICTS_WITH_OPEN_CANONICAL_PR`. PR #258 review/CI tamamlanmadan LAB kodunu veya başka admission engine'i içeri alma. PR contract/CI geçtikten sonra **ince bir adapter adayı** olabilir; ayrı design ve authority review şart. |
| PR #259 handoff | Yalnız `docs/project/2026-10-29_CHATGPT_HANDOFF_POST_S5_T1_CANDIDATE.md`; draft/open | Kanonik yeni source API'si değil; doğrulanmış #258 bağlamını sonraki konuşmaya taşır. | `EXACT_DUPLICATE_DO_NOT_IMPORT` (implementation açısından) / dokümantasyon için `NOT_OBSERVED` gereklilik. Handoff, kabul veya merge kanıtı değildir; LAB koduyla birleştirilmemeli. |
| `PRODUCT.md` ve `docs/product-design/VIP_PRODUCT_DESIGN_DECISION_RECORD_2026-11-04.md` | İki dosya mevcut canonical `main@bee314b9` ağacında; PR #258/#259 base’i hâlâ `592952da`. Dosyalar PR tabanından sonra `dcec681` ile eklendi ve GitHub PR file listelerinde silinme yok. | `ALREADY_CANONICAL`; içerik handoff’ta PROPOSED UX bağlamıdır, implementation talimatı değildir. | `EXACT_DUPLICATE_DO_NOT_IMPORT`. Stale-base ile current-main karşılaştırması PR diff’i değildir; PRODUCT tasarımı uygulama izni sayılmaz. |

## Döngü 3–4: Zaman, insan kararı ve çıkış yetkisi

| Sözleşme yüzeyi | LAB/kanonik karşılaştırması | Karar |
|---|---|---|
| D-2 haklar/kaynak kabulü ile D-3 gerçek medya izni | MEGA-17 sentetik D-2 şema ve sahte/eksik beyanları sınar; gerçek owner attestation veya archive byte erişimi yoktur. PR #258 descriptor/custody ortak sözleşmesini etkileyebilir. | `BLOCKED_BY_UNRESOLVED_AUTHORITY`; iki sınır ayrı tutulmalı. D-2 sentetik pass, D-3 yetki değildir. |
| Source-native PTS/timebase ve VFR | LAB candidate/timeline proposal'ı gerçek measured frame sınırı saymıyor; canonical contract source stream + PTS/timebase mapping istiyor. Nominal-FPS çarpımıyla VFR frame hesaplama yasak. | `ALREADY_CANONICAL` temel invariants; LAB yalnız synthetically tests refusal. Gerçek mapping/PTS `NOT_OBSERVED`. |
| A-7 stream namespace ve IT-6 terminal tail | Açık Owner-governed cross-contract/terminal-boundary kararları; sentetik test onları kapatmıyor. | `BLOCKED_BY_UNRESOLVED_AUTHORITY`. Stream index/terminal tail için adapter/copy kararı verilmez. |
| Model/tool proposal, human decision, versioned edit plan | MEGA-15/17 proposal lineage'ı insan onayı değildir; MEGA-16 release refusal external execution'ı kapatır. Kanonik Gate-3 human decision ayrı evidence/principal gerektirir. | `ALREADY_CANONICAL` contract principles; LAB harness `LAB_ONLY_SYNTHETIC_HARNESS`. Human editorial authority gerçek hayatta `NOT_OBSERVED`. |
| Teknik, visual/audio QC ve export | Synthetic readiness checklist'i measured technical QC veya `VISUALLY_OBSERVED`/`AUDIO_OBSERVED` insan QC oluşturmaz; production export grant ayrı. | `BLOCKED_BY_UNRESOLVED_AUTHORITY`; refusal sınırlarını tut; gerçek QC/production flow'yu kopyalama. |
| H3-C05, H3-A04 ve Atlas sıralaması | Kanonik WBS/Atlas handoff'u dated launch-pack stale drift'ini açıkça not eder; task packet/CI changelog güncel kanıt değildir. | `NOT_OBSERVED` canlı task hazır oluşu. Her yeni H3 çalışmasından önce source/contract/lease yeniden alınmalı ve güncel delta review yapılmalı. |

## Döngü 5–6: En küçük taşınabilir dilim ve NO-IMPORT listesi

Şimdilik **MEGA-03…17 source/test kodundan canonical VIP'ye import edilecek dilim yok**. Potansiyel en küçük faydalı konu, S5-T1 kabulünden sonra MEGA-17'nin synthetic prerequisite ledger'ındaki alanları canonical admission çıktısına bağlayan bir **adapter contract/design** olabilir. PR #258'in sözleşmesi önce review edilmeli; ortak `SourceDescriptor`/rights/permission şekli, error mapping, digest identity, lifetime ve D-2 ile D-3 sınırı için owner-approved design + dar implementation plan gerekli. PR #259 yalnız handoff'tur.

NO-IMPORT kararları:

1. `src/vip_lab/mega03..17/**` paketlerinin tamamı: canonical ürün modülü gibi kopyalama yok.
2. Synthetic corpora, fake owners/reviewers, scenario IDs, fixture digests ve refusal reports: authentic source/rights/reviewer/PTS/QC kanıtı gibi kullanma yok.
3. MEGA-15/16 rendering/QC/release preflight: production render/export ya da Gate promotion yetkisine yükseltme yok.
4. PR #258 source files: draft PR, mevcut failed check view ve açık API review çözülmeden import yok.
5. PR #259 handoff ve `PRODUCT.md`: architecture source of truth veya application build approval sayma yok.
6. Eski H3-C05/H3-A04 task order/launch pack: yeni READY work veya grant varsayma yok.

## GitHub PR diff düzeltmesi ve CI notu

Önceki sürümdeki “iki product-context dokümanı siliniyor” ifadesi yanlış karşılaştırmadan kaynaklandı. GitHub `pulls/258/files` ve `pulls/259/files` endpoint'leri doğrudan kontrol edildi: #258 yalnızca `src/vip_fvs/_bounded_admission_fs.py` (added, 353 satır), `src/vip_fvs/bounded_admission.py` (added, 245 satır) ve `tests/vip_fvs/unit/test_bounded_admission.py` (added, 454 satır); #259 yalnızca `docs/project/2026-10-29_CHATGPT_HANDOFF_POST_S5_T1_CANDIDATE.md` (added, 176 satır). İki listede de `removed` yok. Her iki PR base SHA `592952daf475b1bbae2eebdee64d992c1a744f08`; canonical `main` SHA `bee314b92981b9ae7ea38d83fe2dbae120c474e4`. `PRODUCT.md` ve product decision record `dcec681` commit'inde eski base'ten sonra eklendi, bu yüzden base-to-head PR file listesinde yok. Önceki `current main..PR head` karşılaştırması base-to-head PR diff'i değildi ve main'den sonra eklenen dosyaları yanlışlıkla absent/deleted gibi gösterdi. Stale-base farkı kanıtlıdır; PR'de silinme yok.

PR #258 ve #259 güncel head'leri 2026-11-05 tarihinde açık/draft. `gh pr checks` her ikisinde Gate-0 D1, Gate-0 broad, Gate-2 report/receipt ve Synthetic smoke kontrollerini failed gösterdi. İlişkili run/job'lar 2–3 saniyede bitmiş, step listesi/log yok; `log not found` ve bağımsız GitHub denemesinde `404 BlobNotFound` nedeniyle job log içeriği alınamadı; failure root cause doğrulanamadı. Bu raporda PR içeriği kaynak koddan ve diff'ten okundu; PR statusu başarı olarak sunulmuyor. Kanonik main'e hiçbir yazma yapılmadı.
