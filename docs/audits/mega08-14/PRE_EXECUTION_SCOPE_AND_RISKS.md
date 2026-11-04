# MEGA-08–14 bağımsız ön denetim: mimari, kaynak sözleşmeleri ve entegrasyon açıkları

**Durum:** Faz A tamamlandı; Faz B `NOT_YET_SUBMITTED`  
**İncelenen LAB baseline:** `22f1ffa7064f697d4049e39587945b1decabec4e`  
**Güncel LAB `origin/main` gözlemi:** `b55b14884dc5d62f8784c60af2a8e14fea107b36`  
**Korunan proje main gözlemi:** `592952daf475b1bbae2eebdee64d992c1a744f08`  
**Audit worktree/dal:** `/private/tmp/vip-lab-mega08-14-audit`, `codex/audit-mega08-14-20261104`  
**Kanıt sınıfları:** `VERIFIED_GITHUB`, `SOURCE_INSPECTED`, `INFERRED`, `NOT_OBSERVED`

## 1. Sonuç özeti

- 307 testlik LAB baseline, belirtilen exact commit’te Actions run `41756569162` ile Python 3.11 ve 3.14 matrisinde başarılıdır. Workflow logunda MEGA-03…07 ve cross-gate seçicileri çalışmıştır. Bu, yalnızca `22f1ffa…` koduna ve sentetik/model-free kapsama aittir.
- LAB `origin/main` baseline’ın ileri soyudur. `22f1ffa…..b55b148…` farkı sadece `.github/workflows/vip-ai-studio-synthetic-ci.yml` ile iki MEGA-08–14 dokümanını ekler; yeni dalga kaynak/test dosyası yoktur. `git diff --check` temizdir.
- Kanonik mimari bu LAB modüllerine sınırlı bir sentetik entegrasyon alanı bırakır. Gerçek medya kabulü, A-7 pozitif stream eşlemesi, gerçek Gate-0 D-3, gerçek SigLIP2 çalıştırması, temsili Gate-2 ölçek testi ve üretim QC/export açıkça yetki dışıdır veya `NOT_OBSERVED` durumundadır.
- **P1 — Hosted doğrulama açığı:** Mevcut workflow MEGA-08…14 kaynak/testlerinin varlığını, eksik kardeş dosyalarını, yeni testleri veya E2E testini kontrol etmiyor/çalıştırmıyor. MEGA-03…07 matrisiyle sınırlı. Görev programı §16 AI Studio’nun workflow düzenlemesini yasakladığından, yeni dalgalar için gerçek CI kapısı Owner/CI bakımından ayrıca sağlanmalıdır. Bu düzeltilmeden workflow’un yeşil olması yeni dalgalara kanıt sayılamaz.
- MEGA-09/14, var olan sorgu, retrieval, çoklu kaynak, üç kollu benchmark ve rapor doğrulama API’lerine bağlanmalı; bunların klonlanması görev belgesinin kendi tekrar-yapmama koşulunu ihlal eder. MEGA-10/11/13 de mevcut temporal, insan-kararı ve QC sınırlarını aşamaz.
- Bu rapor bir kod denetimi ya da nihai onay değildir. İncelenecek yeni uygulama commit’i sunulmadığından aday disposition `NOT_YET_SUBMITTED` olarak kalır.

## 2. Baseline ve depo kimliği

### 2.1 İzolasyon ve ref’ler — `VERIFIED_GITHUB`

Remote `origin` `Centaurioun/video-intelligence-pipeline-2` adresidir. Korunan canonical repo ayrı `gh` read-only sorgularıyla gözlenmiştir; hiçbir kaynak checkout’u veya yazımı yapılmamıştır. Remote audit dalı `codex/audit-mega08-14-20261104` `22f1ffa…` idi; aynı ref’ten yeni izole worktree oluşturuldu. LAB ana worktree’de önceden bulunan `.gitignore` değişikliği ve `.ignore` dosyası korunmuştur.

LAB `origin/main` SHA `b55b148…`; baseline commit `22f1ffa…` onun atasıdır. Bu aralıktaki değişiklikler:

- `M .github/workflows/vip-ai-studio-synthetic-ci.yml`
- `A docs/ai-studio-tasks/MEGA_08_14_PARALLEL_CODEX_AUDIT.md`
- `A docs/ai-studio-tasks/MEGA_08_TO_14_ALL_REMAINING_LAB_CODE_PROGRAM.md`

Audit, hareketli `main` adı yerine bu SHA’ları kullandı. `b55b148…` üzerinde yeni MEGA-08…14 uygulama kodu/testi yoktur.

### 2.2 307-test kanıtı — `VERIFIED_GITHUB`

GitHub Actions run [41756569162](https://github.com/Centaurioun/video-intelligence-pipeline-2/actions/runs/41756569162), `headSha=22f1ffa7064f697d4049e39587945b1decabec4e`, `conclusion=success`. İki job da başarılıdır: Python 3.11 (`126333964527`) ve Python 3.14 (`126333964855`). Her ikisinde de baseline, MEGA-03/04/05/06/07 ve cross-gate pytest adımları gerçekten çalışmış, toplu durum adımı `MEGA-03=success … CROSS=success` yazmıştır. `docs/ai-studio-tasks/MEGA_03_07_PROGRESS.md:19-23` her sürüm için test toplamını **307 PASS** (267 + 13 + 6 + 5 + 6 + 6 + 4) olarak kaydeder.

Bu kanıt gerçek Actions çalıştırmasıdır; gerçek video/model/provider, üretim veya Gate kabulü değildir.

### 2.3 Gerekli başlangıç parçaları — `SOURCE_INSPECTED`

`22f1ffa…` ağacında altı `src/gate0/media/` dosyasının tümü mevcuttur (`__init__.py`, `decode.py`, `probe.py`, `proc.py`, `source_guard.py`, `tool_identity.py`). MEGA-03…07 modülleri ve testleri ile `tests/vip_lab/test_cross_gate_integration.py` ve `test_lab_cli.py` mevcuttur. MEGA-08…14 paketleri yoktur. Bu, görev paketinin baseline hard-gate’ini geçer; izinli yeni geliştirme alanının başlangıç kanıtıdır.

## 3. Mimari ve mevcut sözleşme yüzeyleri

Aşağıdaki işaretler baseline kaynak koduna ilişkindir; yeni tüketici uygulamalarının davranış kanıtı değildir.

| Mevcut sözleşme | Doğrulanan semboller | MEGA-08–14 için anlamı |
|---|---|---|
| LAB paketleri | `src/vip_lab/common.py:176-235,283-349,373-395,437-517`: canonical JSON/SHA, yinelenen JSON anahtar reddi, sınırlı `O_NOFOLLOW` yükleme, sahte otorite alanlarını temizleme, `ReadinessPacket` | İkinci genel rapor/parser çerçevesi yerine mevcut katı serializer/parser kullanılmalı. |
| Sorgu kataloğu | `src/vip_fvs/query_batch.py:71-187`: `QueryCatalogItem`, `QueryCatalog`, sıralı query ID’leri ve ayrı ID’lerle yinelenebilen metin | P09/P14 sorgu kataloğu kopyalamamalı; query ID ve metin kimliklerini korumalı. |
| Çoklu kaynak | `src/vip_fvs/source_adapter.py:62-162`: `SourceManifestEntry`, `MultiSourceManifest`, locator + source SHA ile bağlama; `src/vip_fvs/multi_source_retrieval.py:15-88`: adayların manifest girdisine bağlanması ve `retrieve_multi_source` | Aynı içeriğe sahip farklı sentetik path’ler ayrı occurrence olarak kalmalı. Manifest metaverisi gerçek kaynak-byte doğrulaması sayılmaz. |
| Batch retrieval | `src/vip_fvs/batch_retrieval.py:51-177,220-319`: `BatchCandidateRecord`, `BatchQueryResult`, `SingleArmBatchResult`, `_from_multi_source_candidate`, `run_batch_retrieval` | P09/P14 mevcut arama yolunu tüketmeli, yeni ranking/search algoritması kurmamalı. Tam imza/type kontrolleri her yeni exact SHA’da yeniden yapılmalı. |
| Üç kollu retrieval | `src/vip_fvs/three_arm_batch.py:245-320`: arm sonuçları, `ThreeArmBatchResult`, `run_three_arm_batch` | Model-space ve generation kimliklerini her arm’da koru; 768D eşitliği V1/V2 uyumluluğu anlamına gelmez. |
| Batch rapor | `src/vip_fvs/batch_report.py:140-160,224-382`: canonical digest/serialize, single/three-arm builder, `verify_batch_report` | P14 mevcut rapor doğrulayıcıyı çağırmalı; aynı adlı daha zayıf verifier yazmamalı. Yeni üst raporun kendine ait sözleşmesi yine test edilmelidir. |
| Index | `src/vip_fvs/semantic_index.py:20-53`: `SemanticIndexEngine` query ve index_source ayrımı | Sorgu aşaması önceden üretilmiş sentetik index kullanmalı; source indexing çağrısı yapmamalı. |
| Zaman | `src/vip_lab/mega07/candidate_temporal_gate.py:69-…` ve `src/gate3/pts.py`, `rational.py`, `temporal.py` | Tam sayı PTS + rasyonel timebase korunmalı; semantik zaman frame/cut değildir; generated PTS yalnızca tanısal ve `NOT_OBSERVED` kalır. |
| Karar/QC | `src/vip_lab/mega07/editorial_lineage.py:77-163`; `src/vip_lab/mega07/qc_export_readiness.py:62-91,119-160` | İnsan kararı formatını üretmek/otorite vermek yasak; sentetik QC binding-consumable olamaz ve export yetkisi vermez. |
| S5 | `src/vip_lab/mega03/s5_preflight.py:112-123,172-189` | `snapshot_root` ile çağrı açıkça reddedilir; byte stat/open/hash/probe yoktur. PR #258 S5 kabulünün yerine geçmez. |

## 4. Kanonik kararlar ve engeller

### 4.1 S5 / PR #258 — `VERIFIED_GITHUB`

Protected repo sorgusu PR #258’i `OPEN`, `isDraft=true`, HEAD `5a60cd8e0abc021767b05c87ca50202822c049d0`, base main `592952daf475b1bbae2eebdee64d992c1a744f08` olarak gösterdi. `docs/decisions/2026-10-29-a7-s5-scoped-synthetic-tdd-plan-owner-adoption.md` (kanonik main dosyası) karar statüsünü `PLAN_ADOPTED_FOR_SEPARATELY_AUTHORIZED_SYNTHETIC_TDD`, `IMPLEMENTATION_AUTHORIZED=FALSE`, `PRODUCTION_READY=FALSE` yapıyor; T2 exact D2-grant ve çağıran kapanışına, T3 E01 bütçe yolu çözümüne bağlı. Bu LAB görevinde paralel BoundedAdmission API’si, parser/caller kaynağı veya S5 kabulü üretilemez. MEGA-08 kaynak envanteri S5’i yalnızca mevcut metadata-only/refusal davranışı olarak tanımlamalıdır.

### 4.2 D-3 / model / ölçek / Gate-3

LAB programı §2 ve `docs/project/01_CURRENT_STATE_AND_HANDOFF.md:44-52` uyarınca Gate-0 D-2 girdileri sağlanmamış; D-3 gerçek kaynak/model/harici işlem yetkisi yoktur. SigLIP2 native tokenizer/processor/pooling/runtime ve gerçek ağırlıklar `NOT_OBSERVED`; Gate-B gerçek benchmark `NO_GO_BLOCKED`. Temsili gerçek arşiv performansı ve Gate-3 ölçülmüş timing/human editorial/render/QC de bu görevde gösterilemez. H3-C05 successor ve H3-A04 signer yorumu teklif/pending durumundadır. Bu statüler LAB rapor alanları veya başarı bayrakları haline getirilmemelidir.

### 4.3 A-7 pozitif eşleme — `NOT_OBSERVED`

Kanonik karar kaydı pozitif FFprobe-global-index → ISO-BMFF track eşlemesini benimsemiyor; ordinal eşitliğinden identity türetilemez. LAB yalnızca sentetik negatif/red davranışını gösterebilir. Hiçbir synthetic stream fixture bunu gerçek kaynak occurrence ya da stream identity kanıtına yükseltemez.

## 5. Faz A risk envanteri

| ID | Önem | Kanıt/etki | Önerilen düzeltme ve denetim ölçütü |
|---|---|---|---|
| A-01 | **P1** | `b55b148…:.github/workflows/vip-ai-studio-synthetic-ci.yml:117-245` MEGA-03…07 ve cross-gate tamamlılığı/testlerini tanımlar. `tests/vip_lab/test_mega08.py`…14 ve end-to-end için eşdeğer varlık kontrolü/seçici görünmüyor. Yeşil run yalnız eski 307 baseline’ı kanıtlayabilir. | Kod sahibi dosyalara dokunmadan önce CI sahibi/Owner yeni dalgalar için 3.11/3.14 seçimini ve eksik testte fail davranışını sağlasın. Yeni aday run’ın her test komutunu ve test sayısını Actions logundan exact SHA’ya bağla. CI düzenlemesi ayrıca yetkili kanaldan yapılana dek yeni dalgaları `NOT_EXECUTED` tut. |
| A-02 | **P1** | P09/14’ün kullandığı `MultiSourceManifest` ve retrieval zaten locator + digest ile aday üretir; P14 ayrıca gerçek `verify_batch_report` arayüzünü kullanmak zorundadır (`MEGA_08_TO_14_ALL_REMAINING_LAB_CODE_PROGRAM.md:323-350`). Yeni retrieval/manifest/report klonları sahte ikinci sözleşme ve yanlış test güveni oluşturur. | İlk yeni SHA’da tam dataclass alanları, builder/runner imzaları ve fixture’ın index-source çağırmadığını kod/test üzerinden doğrula. E2E’de gerçek mevcut runner + gerçek batch verifier çağrıları görünür olmalı; sadece preset dönüş mock’ları yeterli değil. |
| A-03 | **P1** | P10 temporal output, P11 proposal ve P13 QC zinciri insan kararı/edit planı/üretim dışa aktarımına yakın trust boundary’lerdir. Mevcut MEGA-07 karar ve export-refusal kodu ayrı ayrı çalışır (`editorial_lineage.py:81-163`; `qc_export_readiness.py:62-91`). | Her üretici bağlanmış upstream digest, source revision, occurrence, stream namespace ve model space’i korusun; “approved”, “MEASURED”, bare QC PASS ve export alanlarının hostile input testleri side-effect spy’larıyla reddedilsin. `HumanDecisionArtifact`, EditPlan veya kaynak timing’i taklit eden pozitif sentetik kayıt üretmeyin. |
| A-04 | **P1** | Görev §10–13 E2E için tüm gerçek producer/consumer zincirini ister; paket bağımlılık tablosu P08 ve P12’yi bağımsız, P09→P10→P11’i sıralı, P13/14’ü gerçek upstream’lere bağlı gösterir (`…PROGRAM.md:352-370`). Mock-only tek kompozisyon testinin yeşil olması source seams’i kanıtlamaz. | Her dalga için producer/consumer sözleşmesini ayrı doğrula; P14’te gerçek arayüzlü küçük fixture kullan. Her bloklu önkoşul yapılandırılmış başarısızlık üretmeli, kısmi sonuç `SUCCESS` diye raporlanmamalı. |
| A-05 | **P2** | Baseline yalnız MEGA-03…07’yi kapsıyor. Program açıkça `NOT_NEEDED` (mevcut fonksiyonun aynısı) ve `BLOCKED_SCOPE` (kanonik/operasyonel yetki) durumlarını destekliyor (§7, §15). | Dalga adedi başarı metriği yapılmasın. Her yeni sembol bir gerçek yeni tüketici ve adversarial regresyonla gerekçelendirilmeli; uygun olan dalgalar kod yazmadan `NOT_NEEDED` veya `BLOCKED_SCOPE` olabilir. |
| A-06 | **P2** | Audit programı yeni run SHA’larında önceki sonucu tarihsel saymayı emreder. Rapor/Progress ledger’da mutable `main` adına dayalı toplu “pass” yanlış olabilir. | Her incelemede commit, parent, changed paths, tree deletions, iki Python workflow job’ı, seçilmiş ve atlanmış testler ayrı kaydedilsin. Her yeni SHA önceki aday disposition’ını yeniden açar. |

## 6. Dalga bazında gerçek açık / mevcut işlev / yetki sınırı

| Dalga | Baseline’da bulunan ve yeniden kullanılacak | Gerçek yeni ihtiyaç (programda tarif edildiği şekliyle) | Ön karar |
|---|---|---|---|
| MEGA-08 | `ReadinessPacket`, canonical hash/strict JSON; MEGA-03…07 preflight/readiness; görev §6 kaynak sembolleri | Allowlist edilmiş kod sembollerini davranışsal test durumundan ayıran advisory inventory ve gap digest | **Plausible LAB gap**, fakat arbitrary filesystem scan/import yasak; WBS/Gate state mutate etmez. |
| MEGA-09 | `QueryCatalog`; multi-source manifest ve `retrieve_multi_source`; `run_batch_retrieval`; batch result candidate yapıtaşları | Run/query/model generation + source occurrence provenance’ını kaybetmeden review queue oluşturma | **Plausible yeni consumer**, mevcut retrieval’ı kopyalamamalı; exact path/locator/manifest binding çoklu occurrence’da test edilmeli. |
| MEGA-10 | `PtsTable`, `Rational`, `TimeBase`, `resolve_start`, `resolve_end`, VFR sınıflaması; MEGA-07 `inspect_candidate_temporal` | Review candidate’i temporal refine request’e dönüştürme, yalnız generated PTS tanı raporu | **Plausible yeni input boundary**; source path’i opaque, end half-open, duplicate tick ambiguity fail-closed. |
| MEGA-11 | `HumanDecisionArtifact`, `ReviewBundle`, `EditPlan` modelleri ve MEGA-07 lineage doğrulaması | Upstream digest’lere bağlanan, versiyonlanan ama `PROPOSED_NOT_APPROVED` editorial proposal | **Sınırlandırılmış yeni metadata**; mevcut otorite-bearing artefact’lerden ayrı tür/namespace gerektirir. |
| MEGA-12 | `gate2.faults`, `gate2.recovery`, `gate2.workload`; MEGA-06 generated recovery matrix | Explicit synthetic stage replay/generation/idempotency consistency doğrulaması | **Plausible test seam**; mevcut `RecoveryHarness`/journal klonlanmaz, desteklenmeyen fault `NOT_EXECUTED` kalır. |
| MEGA-13 | MEGA-07 structured QC checks ve unconditional synthetic export refusal | Çoklu kaynak/QC evidence completeness, release/export refusal raporu | **Muhtemel küçük orchestration/validator ihtiyacı**; export kapısı yeni izin verici koda dönüşmemeli. |
| MEGA-14 | `vip_fvs` query/retrieval/report, MEGA-03…07, mevcut CLI/integration | Tüm zinciri gerçek producer seams’leri ile üreten/verify eden synthetic scenario + CLI | **En yüksek entegrasyon riski**; ikinci search, manifest ya da rapor verifier kurulmamalı; workflow açığı kapatılmalı. |

Bu tablo öneri kapsamıdır. Yeni kaynak gelmeden bir wave `IMPLEMENTED`, `VERIFIED` veya kabul edilmiş sayılamaz.

## 7. Şimdiki test/işlem sınırı ve sonraki adım

- Yeni uygulama kaynakları ve testleri `NOT_YET_SUBMITTED`; dolayısıyla bu rapor için yerel aday testleri çalıştırılmadı. Baseline CI sonucu yeni dalgalara taşınmaz.
- Hiçbir protected media, model, FFmpeg/provider/network/production işlemi yapılmadı. Orijinal VIP kaynağına read-only GitHub metadata ve karar belgesi dışında erişilmedi; repo içeriği değiştirilmedi.
- AI Studio yeni bir LAB main commit’i yayımladığında parent SHA ve changed paths exact SHA’ya bağlanmalı; önce tree ve deletions, sonra bütün yeni kaynak/testler, ardından CI job/log/test sayıları incelenmelidir.
- Eklenmiş test sayısı dosya varlığıyla değil pytest seçici loglarıyla kanıtlanmalı. İki Python sürümünden biri eksikse tam hosted verification değildir.
- Nihai aday kararı ancak kaynak incelemesi + uygun hosted run + exact-base diff + trust/evidence audit sonrasında verilebilir. Şimdiki disposition: **`NOT_YET_SUBMITTED`**.
