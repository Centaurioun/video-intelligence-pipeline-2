# MEGA-17 Sonrası Test Lane Ayrımı — Tasarım ve Kanıt Envanteri

Durum: **OWNER APPROVED — 2026-11-05**
Tarih: 2026-11-05
LAB tasarım tabanı: `main@1fd14c0b246c8da97e07129f6b84173d86f6a500`
Kanonik VIP gözlem noktası: `main@bee314b92981b9ae7ea38d83fe2dbae120c474e4`
Kapsam: yalnız dokümantasyon ve test sahipliği/lane tasarımı. Kaynak, test, iş akışı veya beklenti değişikliği yapılmamıştır.

## 1. Amaç ve sınırlar

Bu tasarım, LAB'nin kendi sentetik regresyon kanıtını canonical VIP'nin sabitlenmiş tarihsel dosya ve Git-object bağımlı testlerinden ayırır. Sonuçlar iki ayrı lane olarak raporlanır; bir lane'in başarılı olması diğerinin sonucu yerine geçmez. Daha önceki geniş LAB koşusunda görülen 26 `FAILED` ve 7 `ERROR` çözülmüş sayılmaz. Bu 33 test silinmez, atlanmaz, `xfail` yapılmaz veya beklentileri zayıflatılmaz. Artifact kopyalama varsayılan çözüm değildir.

Bu belge kod/CI değişikliği, test seçimini değiştirme, kanonik PR'ı yeniden çalıştırma, media/model/render çalıştırma, Gate yetkisi veya merge yetkisi vermez. Takip planı tasarım onayı sonrasında ayrı belge olarak hazırlanacaktır.

## 2. Gözlenen GitHub durumları

| Kaynak | Doğrulanan durum |
|---|---|
| LAB PR #4 | Açık/taslak; base `1fd14c0b246c8da97e07129f6b84173d86f6a500`, head `ce11bc50707cf517937c42dfd96e3f325fc1d62f`; son bağımsız yorum `https://github.com/Centaurioun/video-intelligence-pipeline-2/pull/4#issuecomment-6643257050`. |
| Canonical VIP main | `bee314b92981b9ae7ea38d83fe2dbae120c474e`. |
| Canonical PR #258 | Açık/taslak; base `592952daf475b1bbae2eebdee64d992c1a744f08`, head `5a60cd8e0abc021767b05c87ca50202822c049d0`; GitHub PR files tam üç eklenen dosya bildiriyor. |
| Canonical PR #259 | Açık/taslak; aynı eski base, head `e08382db65dcde703aadecc6ab329741f3c4b24c`; GitHub PR files yalnız bir handoff belgesi bildiriyor. |
| Canonical base drift | `592952da…` ile güncel `bee314b9…` karşılaştırmasında main iki commit ileride; yalnız `PRODUCT.md` ve `docs/product-design/VIP_PRODUCT_DESIGN_DECISION_RECORD_2026-11-04.md` eklenmiş. Arada workflow, test veya uygulama kodu değişikliği yok. PR'lar stale base'te kalıyor; rebase henüz gözlenmedi. |

PR #258'in değişiklik listesi `src/vip_fvs/_bounded_admission_fs.py`, `src/vip_fvs/bounded_admission.py`, `tests/vip_fvs/unit/test_bounded_admission.py`; PR #259'un listesi `docs/project/2026-10-29_CHATGPT_HANDOFF_POST_S5_T1_CANDIDATE.md`. İki listede de silme yok.

## 3. Canonical PR kontrollerinin kök neden incelemesi

### 3.1 Workflow ve runner kanıtı

GitHub Actions ayar API'si Actions'ın etkin, izinli eylemlerin `all` olduğunu bildiriyor. İlgili dört workflow aktif; `pull_request` tetikleyicisiyle `main` hedefliyor, `ubuntu-latest` runner ve Python `3.11`/`3.14` matrisi tanımlıyor. Job YAML'larında checkout, Python setup, bağımlılık kurulumu ve pytest adımları var.

PR başına dört run ve iki Python job'u, toplam 16 job, 2026-10-29'da başarısız sonuçlanmış. GitHub job metadata'sı `runner_id=0`, boş runner adı ve `steps=[]` bildiriyor. **Her 16 job'un check annotation'ı** aynı açık mesajı veriyor: “The job was not started because recent account payments have failed or your spending limit needs to be increased. Please check the 'Billing & plans' section in your settings”. Bu, başarısızlığın test veya kod sonucu olmadığını; GitHub-hosted job'un billing/limit kapısında başlamadığını kanıtlıyor. Annotation, “ödemeler başarısız” ve “harcama limiti” seçeneklerinden hangisinin hesapta geçerli olduğunu ayırmıyor. Güncel billing durumu bu tarihli annotation'dan çıkarılamaz.

Ham run logları alınamadı: `gh run view --log-failed` “log not found” döndürdü; Actions log arşivi isteği HTTP 200 ile 22 baytlık boş ZIP döndürdü. Bununla birlikte check annotation'ları kullanılabilir ve kök neden sınıfını doğrudan bildiriyor. `ubuntu-latest` → Ubuntu 26 geçiş notu bilgilendirme annotation'ıdır; başlangıç engeli değildir.

| PR | Workflow / Python job'ları | Run ID | Job ID'leri |
|---|---|---:|---|
| #258 | Gate-0 D1 targeted, 3.11 / 3.14 | `40820177498` | `123270556226`, `123270556431` |
| #258 | Gate-0 broad, 3.11 / 3.14 | `40820177514` | `123270556689`, `123270556576` |
| #258 | Gate-2 receipt/report, 3.11 / 3.14 | `40820177609` | `123270556768`, `123270556519` |
| #258 | Synthetic smoke, 3.11 / 3.14 | `40820177628` | `123270556557`, `123270556900` |
| #259 | Gate-0 D1 targeted, 3.11 / 3.14 | `40821952898` | `123276215646`, `123276215356` |
| #259 | Gate-0 broad, 3.11 / 3.14 | `40821953002` | `123276215548`, `123276215276` |
| #259 | Gate-2 receipt/report, 3.11 / 3.14 | `40821953085` | `123276215860`, `123276215669` |
| #259 | Synthetic smoke, 3.11 / 3.14 | `40821953053` | `123276215887`, `123276216232` |

Bu annotation gerçek nedeni “billing/spending-limit job-start block” olarak sınırlar; pytest assertion başarısızlığı, bozuk workflow syntax'i, test-selection hatası veya S5-T1 kod kusuru olarak sınıflandırmaz. Workflow'ların GitHub tarafından run/job olarak oluşturulmuş olması ve aktif workflow kayıtları workflow parse edildiğini destekler. Ancak test adımları hiç yürütülmedi.

### 3.2 Değişen dosyalar ile test applicability

| Workflow | Tanımlı pytest seçimi | 33 historical test ile ilişki | PR değişikliği doğrulaması |
|---|---|---|---|
| Gate-0 D1 | On adet açıkça yazılmış D1/kimlik/JSON test modülü | 33 node içinden hiçbiri doğrudan seçilmiyor | İki PR'de de D1 girdisi değişmedi. |
| Gate-0 broad | `pytest -q tests/gate0` | 33 node'dan 9 Gate-0 node'u kapsar: üç pinned blob, altı A04/Atlas/C05 contract testi | İlgili 9 node runner başlamadığı için denenmedi. |
| Gate-2 receipt/report | `pytest -q tests/gate2` | 33 node'dan 24 Gate-2 node'unu kapsar | İlgili 24 node runner başlamadığı için denenmedi. |
| Synthetic smoke | Sabit node listesidir; Gate-0 JSON/D1, Gate-1 compatibility, Gate-2 fault, Gate-3/FVS ve CLI seam testleri içerir | 33 node'lardan hiçbiri açık seçim listesinde yok | Bu smoke PR #258'in yeni bounded-admission testini de seçmiyor. |

Canonical PR #258'in mevcut diff'i üç dosya ekliyor: `src/vip_fvs/_bounded_admission_fs.py`, `src/vip_fvs/bounded_admission.py` ve `tests/vip_fvs/unit/test_bounded_admission.py`. GitHub contents API bu test dosyasını canonical main üzerinde 404, PR #258 head `5a60cd8e0abc021767b05c87ca50202822c049d0` üzerinde blob `5ecbbd33d9d136984424cdcb787669b83be4db84` olarak doğruladı. Bu nedenle smoke workflow'a koşulsuz test adımı main'de tek başına eklenirse #258 dışındaki main/PR job'ları bozulabilir. Güvenli sıra Task 3'te tanımlanır: PR #258'in aynı aday head'inde kaynak/test ve workflow değişikliği birlikte bulunur; eksik test hiçbir koşulda skip edilmez ve workflow değişikliği ayrı commit/PR olarak main'e indirilmez. PR #259 dokümantasyon-only olduğu için ürün davranışı testi eklemiyor.

### 3.3 Güncel Billing/Actions çalıştırma kapısı

2026-11-05'te GitHub kişisel hesap Centaurioun için **Budgets and alerts** ekranı salt-okunur yenilendi; hesap düzeyindeki **Actions** satırı `Usage blocked` gösterdi. Repo filtresi seçili değildi. Owner açıklamasına göre bu durum ücretli aşım harcamasını engeller, dahil edilmiş Actions allowance'ının bittiğini göstermez; owner şu an yaklaşık 3.000 dakika allowance kaldığını bildiriyor. Bu miktar Codex tarafından ayrıca ölçülmedi. LAB PR #5'in exact head `f69334705919f10b10c4b78ecc235c6f160d3b6b` üzerindeki otomatik hosted run `41928274424` 2026-11-04 22:47 UTC'de Python 3.11 ve 3.14 için `SUCCESS` tamamlandı. Farklı zaman/repo kanıtları korunur; LAB CI başarısı canonical repo allowance'ını kanıtlamaz. Billing ayarı değiştirilmedi; ödeme yöntemi/geçmişi incelenmedi. **Her gelecekteki hosted execution veya rerun öncesinde hedef repository/job ile ilişkili GitHub hesabının kalan dahil edilmiş dakikaları yenilenip doğrulanmalıdır.** Yeterli included allowance varsa `Usage blocked` tek başına durdurma nedeni değildir; allowance yetersiz kalacak ve ücretli aşım gerekecekse run başlatılmaz.

## 4. İki-lane tasarımı

### Lane L — LAB synthetic

- Sahibi: `video-intelligence-pipeline-2`.
- Kanıt: LAB'ye ait sentetik `tests/vip_lab` suite'leri ve bunların açıkça kaydedilmiş LAB iş akışları.
- Ortam: LAB checkout/ref'i ve onun sentetik fixture'ları; hosted kanıt varsa commit, workflow, job, Python sürümü, passed/failed/skipped/deselected sayıları ayrı kaydedilir.
- Yorum: başarılı LAB lane yalnızca LAB sentetik sözleşmelerini doğrular. Canonical historical lane yerine geçmez; Gate, gerçek kaynak, prod veya canonical history kabulü değildir.

### Lane C — canonical history

- Sahibi: `video-intelligence-pipeline`.
- Test kaynakları, tarihsel prompt/evidence kayıtları ve pinned Git objects aynı canonical repo içindeki test/source ile yürütülür.
- Ortam: canonical repository; aday `main@bee314b92981b9ae7ea38d83fe2dbae120c474e4` veya PR doğrulaması için açıkça kayıtlı `base SHA + PR head SHA + merge SHA`. PR'lar güncel main'e göre güncellenmeden PR kabulü için stale base job'u yeni kaynak durumu sayılmaz.
- Python: canonical workflow matrisi olan 3.11 ve 3.14. Tarihsel Git blob testleri için workflow'da belirtilen tam tarihçe ve gerekli preserved-history ref erişimi doğrulanmalı; yalnız `fetch-depth: 0` satırına dayanarak ref'in runner'a geldiği varsayılmaz.
- Lane C başarı/başarısızlığı ayrı yayınlanır. Koşmadıysa `NOT RUN`; bağımlılığı yoksa test `BLOCKED` olarak kalır. L lane sonucu C lane'i PASS yapamaz.

İki lane sonuçlarını tek bir “tüm repo PASS” göstergesine indirgemez. İki ayrı status context veya iki bağımsız kabul satırı kullanılabilir; implementasyon ve CI değişikliği için ayrı onay gerekir. Bu doküman şu anda seçim, marker, workflow, pytest config veya test kodu değiştirmiyor.

## 5. 33 node için kanıt manifesti

### 5.1 Sabitlenmiş kaynak ve artifact kümeleri

Canonical GitHub tree API `bee314b92981b9ae7ea38d83fe2dbae120c474e4` üzerinde paths ve Git identities doğrulandı. Git blob/tree SHA'ları içerik kimliğidir; aşağıdaki testlerde assertion olarak kullanılan SHA-256 değerleri farklı bir kimlik uzayıdır ve birbirine karıştırılmamalıdır.

| Küme | Canonical path / identity | İçerik ve kullanım |
|---|---|---|
| `OBJ-D3` | archive ref `archive/history/branch-preservation-v3-20261008` → commit `0dce7a2a4c5b429fac94ebba0088b85e99c6296c`; blob `d3d7a4611e375317e651049bceb345fe0d879744` | Gate-0 evidence freeze testlerinin `git show` / `git cat-file` ile okuduğu tarihsel object. Ref ve object erişimi canonical test ortamında doğrulanmalı. |
| `A04-BASE` | `.orchestration/remaining-work/prompts/H3-A04/` tree `ea057c01b346821affa7c7034e70301b4b58d586`; `core.md` `e8d9627ca904df95c0f92f901bd7af7ae1a81e0e`; `core.json` `67e10666b23f00ae5c2537dd49a76f45b5909c8e` | H3-A04 eski prompt baseline. Test ayrıca içerik SHA-256 `39c408…` bekler. |
| `A04-V101` | `.orchestration/remaining-work/prompts/H3-A04/v1.0.1/` tree `5cbcf60cde84f497b2b11c0c86cd0354e972882c`; `core.md` `5692c46bb742ba4189e84178f1d52872f4078c23`; `core.json` `2c0266784cc794ba8faa364e7851b48b5dd29c67` | Yeni H3-A04 adopted contract prompt; tests file metadata and semantic predicates. |
| `C05-V101` | `.orchestration/remaining-work/prompts/H3-C05/v1.0.1/` tree `ff5861bdd2a5bf5cebdcb2fdce16a482c27a6fa1`; `core.md` `cfca61b9d548fedb292fb69893291543a25938ea`; `core.json` `567229f5dfd1c70672669d3f17920b1eab855dfb` | H3-C05 preserved prior prompt; test additionally checks content SHA-256 `f1bf77…`. |
| `C05-V102` | `.orchestration/remaining-work/prompts/H3-C05/v1.0.2/` tree `3cd44414f5f11f4628ebe2f5d5b22853d4526110`; `core.md` `0d87e024234488232f161773f314b73ac1db0a33`; `core.json` `b4ad22ada8b9f88acfd4c10a9dfebfe5edb3a5b0` | H3-C05 adopted contract prompt; tests bind exact digest and read-only authority language. |
| `ATLAS-INDEX` | `atlas/atlas.json` blob `29565bc63cb4e2d107b56ebd071f4744912dab35`; `prompts/index.json` blob `bfa809a6f5d4cf1b72a35cc28b11c392554dad23` | H3-A04/H3-C05 atlas state and prompt index cross-binding. |
| `DECISIONS` | A04 decision blob `9ea3f9e62412fdab0bc871ed581f2b7e1facfc4a`; C05 decision blob `34ff5db4dbcf6891c4380d87000bb0ce2dc8b20f` | Owner-adoption records read by H3-C05 authority test; source docs are canonical-only. |
| `G2-EXEC` | `docs/agent-runs/2026-10-25-gate2-reliability-execution/` tree `053323754451385be73381ed5e80f9f90b17b97d` | Full report/run evidence subtree, including run receipts, carriers, journals, manifest, report and lane records. |
| `G2-EVIDENCE` | `.../evidence/` tree `d5a6ad5fa24395094b2ff62e2a5a38504e9bb670` | Complete synthetic evidence bundle. `BUNDLE_MANIFEST.json` blob `5cba3ec6c9de424aef985f6bb4bdae6e55166e67`; `run-v2/receipt.json` blob `927188590b3153f9cfbbba7071ce7f210a5e8274`; confirmation receipt `b51a7ef7bf277aed03620b11cd861e9684789a5f`. Tree SHA transitively pins nested carriers and journals. |
| `G2-RECON` | `docs/agent-runs/2026-10-25-g2-12-receipt-report-reconciliation/` tree `a614db4f4514488c0e276a788c2d70eefd54f4fc` | Reconciliation record `G2_12_RECEIPT_REPORT_RECONCILIATION.md` blob `7a2fa4ed519e99477b4747c319853e7b164a688f`; `report-values.json` blob `69d45bda990d50d79a13ec2c3e77f31e287086cd`; other lane evidence pinned by directory tree. |
| `G2-M001` | `.orchestration/remaining-work/runs/H3-F03/measurement/metrics-001/` tree `f51dbadbb4a9245df0a38c94669ab1bf7e63a7c2`; `measurement.json` blob `67d76bdbff95c3f785bf16e08e8b32884fcd8b90` | Preregistration, receipt and three carrier artifacts. Directory tree pins all direct members. |
| `G2-M003` | `.orchestration/remaining-work/runs/H3-F03/measurement/metrics-003/` tree `746781310f92f54c5a8ae6142e5b52f1dbdee8a2`; `measurement.json` blob `92b7a55dbe16740ab337309f20bc3fdccdc9681b` | Current H3-F03 measurement, preregistration, configuration, evidence, fault refusal, checkpoint, refusal-apparatus and carriers. Directory tree pins all descendants. |
| `G2-ACCEPTED-HEADS` | accepted F01 commit `345f9526d54f4fbd582c15f4b0f613bc8ab3996e`, tree `daea7e43cfae051a56927daaf51da5e2a221759d`; accepted F02 commit `d8c42ba7c276e8df86991904efaf0dc09ed5fd01`, tree `720459d545f387688bd1eae1c9a5656d39b75aee` | Gate-2 `resolve_accepted_heads` resolves both commit objects. F01 was the first missing object observed in LAB; F02 is also a required input and has not been independently exercised after F01 resolution. |
| `G2-SOURCE` | `src/gate2/measure.py` blob `c8d68e019d7b4340346f02162fd2e0cc8c7c936d`; `src/gate2/verify.py` blob `dd997e3977a8665ec8d5ce63e012e6eb4fa89444` | Current canonical source whose live contents and accepted dependency constants are consumed by scale-restart tests. |

Test-source blobs are the same in current canonical tree and LAB `origin/main@1fd14c0b…`: `test_evidence_projection.py` `b6fd06d73d8ef9984d105402793598a7b160e052`; `test_evidence_seal.py` `e79a4c126bcd27c793ec5f65d5e57885034c829a`; `test_h3_a04_governing_core_v101.py` `35e06f421d7ceeabaa68e433b675b7f9f57be481`; `test_h3_adopted_core_atlas_index.py` `2624ba19b788aa904c71ec994dbe0cede2ca5adf`; `test_h3_c05_governing_core_v102.py` `cd0196e03e289758dd1baa1f758f0bce9814a9ba`; `test_report_receipt_reconciliation.py` `d1159f47fc071725ed0161c5c18d07122b8571c2`; `test_scale_restart_decision.py` `d40fe01f9a6f671c529377e87b3e860eed6bba71`; `test_synthetic_run_execution.py` `e336697d4a8c7d81d3efb1dc9b8796dbad53613c8`; `test_synthetic_run_evidence_bundle.py` `47cfdd410379a15bb7fe04a1a89de178d8c87325`.

### 5.2 Node-by-node ownership and execution manifest

All 33 rows below belong to **canonical VIP** because both the test modules and their test-owned fixtures/evidence originate in canonical history. Their LAB mirror execution is useful as a reproduction of missing dependency blockers, but is not the intended passing context. The observed first-blocker classes are 25 `MISSING_FIXTURE_OR_PROMPT` and 8 `MISSING_PINNED_GIT_OBJECT`; `IMPORT_OR_ENV`, `REPRODUCIBLE_PRODUCT_DEFECT`, and `UNKNOWN` were not the first blocker for any of these 33 nodes in that run. By row, object blockers are #1–3 and #22–26; missing-file blockers are #4–21 and #27–33. This describes only the first observed failure point. Every status remains `UNRESOLVED`; resolving only the first exception does not imply later assertions pass.

| # | Exact pytest node ID | Test-source blob | Required group(s) / pinned identity | Proper lane/environment | Prior observed state |
|---:|---|---|---|---|---|
| 1 | `tests/gate0/unit/test_evidence_projection.py::test_capture_frozen_fixture_and_guarantee_limits` | projection `b6fd06d7…` | `OBJ-D3`: blob `d3d7a461…`; archive ref commit `0dce7a2a…` | C; canonical repo with preserved archive ref; Python 3.11/3.14 | `UNRESOLVED`; LAB Git object missing. |
| 2 | `tests/gate0/unit/test_evidence_seal.py::test_tasks12_13_14_16_s9_inventory_is_exact` | seal `e79a4c12…` | `OBJ-D3` | C; same as above | `UNRESOLVED`; LAB Git object missing. |
| 3 | `tests/gate0/unit/test_evidence_seal.py::test_task15_has_no_successor_behavior_delta` | seal `e79a4c12…` | `OBJ-D3` | C; same as above | `UNRESOLVED`; LAB Git object missing. |
| 4 | `tests/gate0/unit/test_h3_a04_governing_core_v101.py::test_a04_old_frozen_core_remains_byte_identical` | A04 `35e06f42…` | `A04-BASE` | C; canonical tree `bee314b9…`; py3.11/3.14 | `UNRESOLVED`; prompt path absent in LAB. |
| 5 | `tests/gate0/unit/test_h3_a04_governing_core_v101.py::test_a04_option_b_core_integrity_and_exact_one_shot_semantics` | A04 `35e06f42…` | `A04-V101` | C; canonical tree `bee314b9…`; py3.11/3.14 | `UNRESOLVED`; v1.0.1 core path absent in LAB. |
| 6 | `tests/gate0/unit/test_h3_adopted_core_atlas_index.py::test_owner_adopted_cores_are_exactly_bound_in_atlas_and_prompt_index` | atlas/index `2624ba19…` | `A04-V101` + `C05-V102` + `ATLAS-INDEX` | C; canonical tree `bee314b9…`; py3.11/3.14 | `UNRESOLVED`; atlas path absent in LAB. |
| 7 | `tests/gate0/unit/test_h3_c05_governing_core_v102.py::test_c05_old_frozen_core_remains_byte_identical` | C05 `cd0196e0…` | `C05-V101` | C; canonical tree `bee314b9…`; py3.11/3.14 | `UNRESOLVED`; v1.0.1 core absent in LAB. |
| 8 | `tests/gate0/unit/test_h3_c05_governing_core_v102.py::test_c05_adopted_core_is_digest_bound_and_consistent_with_producers` | C05 `cd0196e0…` | `C05-V102` | C; canonical tree `bee314b9…`; py3.11/3.14 | `UNRESOLVED`; v1.0.2 core absent in LAB. |
| 9 | `tests/gate0/unit/test_h3_c05_governing_core_v102.py::test_c05_read_only_contract_and_restricted_authority` | C05 `cd0196e0…` | `C05-V102` + `DECISIONS` | C; canonical tree `bee314b9…`; py3.11/3.14 | `UNRESOLVED`; first absent read was v1.0.2 core. |
| 10 | `tests/gate2/integration/test_report_receipt_reconciliation.py::test_evidence_manifest_still_verifies` | report `d1159f47…` | `G2-EVIDENCE` | C; canonical repo and evidence tree; py3.11/3.14 | `UNRESOLVED`; `BUNDLE_MANIFEST.json` absent in LAB. |
| 11 | `tests/gate2/integration/test_report_receipt_reconciliation.py::test_report_values_match_receipts_and_carriers` | report `d1159f47…` | `G2-EXEC` + `G2-RECON` | C; canonical repo and exact evidence/report trees; py3.11/3.14 | `UNRESOLVED`; `report-values.json` absent in LAB. |
| 12 | `tests/gate2/integration/test_report_receipt_reconciliation.py::test_receipts_are_the_committed_ones` | report `d1159f47…` | `G2-EVIDENCE` + `G2-RECON` | C; canonical repo; py3.11/3.14 | `UNRESOLVED`; first read `report-values.json` absent. |
| 13 | `tests/gate2/integration/test_report_receipt_reconciliation.py::test_report_tables_match_carriers` | report `d1159f47…` | `G2-EXEC` + `G2-RECON` | C; canonical repo; py3.11/3.14 | `UNRESOLVED`; report path absent in LAB. |
| 14 | `tests/gate2/integration/test_report_receipt_reconciliation.py::test_reconciliation_record_is_complete` | report `d1159f47…` | `G2-RECON` | C; canonical repo; py3.11/3.14 | `UNRESOLVED`; reconciliation document absent in LAB. |
| 15 | `tests/gate2/integration/test_report_receipt_reconciliation.py::test_new_report_related_test_count_matches_report` | report `d1159f47…` | `G2-EXEC` + `G2-RECON` | C; canonical repo; py3.11/3.14 | `UNRESOLVED`; report-values input absent in LAB. |
| 16 | `tests/gate2/integration/test_report_receipt_reconciliation.py::test_check_rejects_reverted_report_value` | report `d1159f47…` | `G2-EXEC` + `G2-RECON` | C; canonical repo; py3.11/3.14 | `UNRESOLVED`; report path absent in LAB. |
| 17 | `tests/gate2/integration/test_report_receipt_reconciliation.py::test_check_rejects_mutated_carrier_copy` | report `d1159f47…` | `G2-EVIDENCE` | C; canonical repo; py3.11/3.14 | `UNRESOLVED`; evidence source directory absent in LAB. |
| 18 | `tests/gate2/integration/test_scale_restart_decision.py::test_receipt_binds_exact_dependencies_and_synthetic_scope` | scale `d40fe01f…` | `G2-M001` | C; canonical repo; py3.11/3.14 | `UNRESOLVED`; metrics-001 measurement absent in LAB. |
| 19 | `tests/gate2/integration/test_scale_restart_decision.py::test_only_carried_metrics_are_measured_and_unavailable_metrics_are_explicit` | scale `d40fe01f…` | `G2-M001` | C; canonical repo; py3.11/3.14 | `UNRESOLVED`; metrics-001 measurement absent in LAB. |
| 20 | `tests/gate2/integration/test_scale_restart_decision.py::test_workload_bounds_and_freeze_are_recorded_before_measurements` | scale `d40fe01f…` | `G2-M001` | C; canonical repo; py3.11/3.14 | `UNRESOLVED`; metrics-001 measurement absent in LAB. |
| 21 | `tests/gate2/integration/test_scale_restart_decision.py::test_rebuilt_metrics_003_binds_git_objects_frozen_preregistration_and_exact_carriers` | scale `d40fe01f…` | `G2-M003` + `G2-ACCEPTED-HEADS` + `G2-SOURCE` | C; canonical repo, full required Git object graph; py3.11/3.14 | `UNRESOLVED`; metrics-003 measurement absent was the first exception in the prior run; later checks remain unverified. |
| 22 | `tests/gate2/integration/test_synthetic_run_execution.py::test_bounded_run_measures_every_preregistered_metric` | execution `e336697d…` | `G2-ACCEPTED-HEADS` | C; canonical repo object database; py3.11/3.14 | `UNRESOLVED`; accepted F01 commit unresolved in LAB; F02 resolution after F01 is unobserved. |
| 23 | `tests/gate2/integration/test_synthetic_run_execution.py::test_interruption_resumes_from_journal_without_duplicate_writes` | execution `e336697d…` | `G2-ACCEPTED-HEADS` | C; same as above | `UNRESOLVED`; accepted F01 commit unresolved in LAB; F02 resolution after F01 is unobserved. |
| 24 | `tests/gate2/integration/test_synthetic_run_execution.py::test_integrity_verification_detects_tampered_artifacts` | execution `e336697d…` | `G2-ACCEPTED-HEADS` | C; same as above | `UNRESOLVED`; accepted F01 commit unresolved in LAB; F02 resolution after F01 is unobserved. |
| 25 | `tests/gate2/integration/test_synthetic_run_execution.py::test_repeated_runs_reproduce_identity_but_not_wall_clock` | execution `e336697d…` | `G2-ACCEPTED-HEADS` | C; same as above | `UNRESOLVED`; accepted F01 commit unresolved in LAB; F02 resolution after F01 is unobserved. |
| 26 | `tests/gate2/integration/test_synthetic_run_execution.py::test_cli_run_executes_and_reports_disposition` | execution `e336697d…` | `G2-ACCEPTED-HEADS` | C; same as above | `UNRESOLVED`; CLI returned 2 on unresolved accepted F01 commit; F02 resolution after F01 is unobserved. |
| 27 | `tests/gate2/integration/test_synthetic_run_evidence_bundle.py::test_both_runs_self_verified_at_execution_time` | bundle `47cfdd41…` | `G2-EVIDENCE` | C; canonical repo and full evidence tree; py3.11/3.14 | `UNRESOLVED`; `run-v2/receipt.json` absent in LAB. |
| 28 | `tests/gate2/integration/test_synthetic_run_evidence_bundle.py::test_fault_injection_evidence_was_derived_from_executed_observations` | bundle `47cfdd41…` | `G2-EVIDENCE` | C; canonical repo; py3.11/3.14 | `UNRESOLVED`; module fixture first receipt absent. |
| 29 | `tests/gate2/integration/test_synthetic_run_evidence_bundle.py::test_every_preregistered_metric_has_a_matching_committed_carrier` | bundle `47cfdd41…` | `G2-EVIDENCE` | C; canonical repo; py3.11/3.14 | `UNRESOLVED`; module fixture first receipt absent. |
| 30 | `tests/gate2/integration/test_synthetic_run_evidence_bundle.py::test_identity_is_reproducible_across_independent_invocations` | bundle `47cfdd41…` | `G2-EVIDENCE` | C; canonical repo; py3.11/3.14 | `UNRESOLVED`; module fixture first receipt absent. |
| 31 | `tests/gate2/integration/test_synthetic_run_evidence_bundle.py::test_durable_journals_are_complete_and_ordered` | bundle `47cfdd41…` | `G2-EVIDENCE` | C; canonical repo; py3.11/3.14 | `UNRESOLVED`; module fixture first receipt absent. |
| 32 | `tests/gate2/integration/test_synthetic_run_evidence_bundle.py::test_disposition_justifies_no_additional_mechanism` | bundle `47cfdd41…` | `G2-EVIDENCE` | C; canonical repo; py3.11/3.14 | `UNRESOLVED`; module fixture first receipt absent. |
| 33 | `tests/gate2/integration/test_synthetic_run_evidence_bundle.py::test_real_scale_evidence_remains_not_observed` | bundle `47cfdd41…` | `G2-EVIDENCE` | C; canonical repo; py3.11/3.14 | `UNRESOLVED`; module fixture first receipt absent. |

The `G2-EXEC`, `G2-EVIDENCE`, `G2-RECON`, `G2-M001`, and `G2-M003` tree IDs bind all nested file blobs; the table uses these root trees rather than copying or re-listing every carrier. Rows 21–26 also depend on live `src/gate2/measure.py`/`verify.py` and both accepted dependency heads. The tests compare current contents and Git object resolution, so candidate executions must record exact base/head/merge tree identities rather than transplanting stale literals.

The preceding LAB run was Python 3.14.9 with `--import-mode=importlib`; it recorded **2,043 passed, 26 failed, 7 errors** across the broad selection and a targeted Gate-2 rerun of **17 failed, 2 passed**. Those failures were initial dependency blockers in LAB. This document does **not** claim all 33 tests will pass when executed in canonical context. A future C-lane run must preserve each test's actual final result, additional failures, skip/deselection count and SHA-bound environment.

### 5.3 Bağımsız beklenen node kimliği oracle'ı

Aşağıdaki exact node ID listesi 5.2 dependency manifestinden ayrı, immutable expected-set referansı olarak dondurulmuştur. Canonical runtime bu LAB belgesini okumaz veya ağdan almaz. Ayrı onaylı canonical uygulamada liste tests/contracts/canonical_history_expected_nodeids.json içine kopyalanır; test kodu bu oracle ile manifestin tam set eşitliğini karşılaştırır ve literal checksum'u ayrıca sabitler.

Provenance: LAB PR #5 tasarım belgesi commit f69334705919f10b10c4b78ecc235c6f160d3b6b, blob eb5972bd1fa8098a82b8ca78720b47d51d9ab907. Bu provenance yalnız review/portability içindir, runtime fetch girdisi değildir.

Canonical bytes: UTF-8 JSON serialization of sorted(node_ids), compact separators, ensure_ascii=false, followed by LF. Count: 33. SHA-256: 8248fbf704f0ebba5e877a26106ab9e8b77a9b7a92fd5695a7f4e2820002b016

    [
      "tests/gate0/unit/test_evidence_projection.py::test_capture_frozen_fixture_and_guarantee_limits",
      "tests/gate0/unit/test_evidence_seal.py::test_task15_has_no_successor_behavior_delta",
      "tests/gate0/unit/test_evidence_seal.py::test_tasks12_13_14_16_s9_inventory_is_exact",
      "tests/gate0/unit/test_h3_a04_governing_core_v101.py::test_a04_old_frozen_core_remains_byte_identical",
      "tests/gate0/unit/test_h3_a04_governing_core_v101.py::test_a04_option_b_core_integrity_and_exact_one_shot_semantics",
      "tests/gate0/unit/test_h3_adopted_core_atlas_index.py::test_owner_adopted_cores_are_exactly_bound_in_atlas_and_prompt_index",
      "tests/gate0/unit/test_h3_c05_governing_core_v102.py::test_c05_adopted_core_is_digest_bound_and_consistent_with_producers",
      "tests/gate0/unit/test_h3_c05_governing_core_v102.py::test_c05_old_frozen_core_remains_byte_identical",
      "tests/gate0/unit/test_h3_c05_governing_core_v102.py::test_c05_read_only_contract_and_restricted_authority",
      "tests/gate2/integration/test_report_receipt_reconciliation.py::test_check_rejects_mutated_carrier_copy",
      "tests/gate2/integration/test_report_receipt_reconciliation.py::test_check_rejects_reverted_report_value",
      "tests/gate2/integration/test_report_receipt_reconciliation.py::test_evidence_manifest_still_verifies",
      "tests/gate2/integration/test_report_receipt_reconciliation.py::test_new_report_related_test_count_matches_report",
      "tests/gate2/integration/test_report_receipt_reconciliation.py::test_receipts_are_the_committed_ones",
      "tests/gate2/integration/test_report_receipt_reconciliation.py::test_reconciliation_record_is_complete",
      "tests/gate2/integration/test_report_receipt_reconciliation.py::test_report_tables_match_carriers",
      "tests/gate2/integration/test_report_receipt_reconciliation.py::test_report_values_match_receipts_and_carriers",
      "tests/gate2/integration/test_scale_restart_decision.py::test_only_carried_metrics_are_measured_and_unavailable_metrics_are_explicit",
      "tests/gate2/integration/test_scale_restart_decision.py::test_rebuilt_metrics_003_binds_git_objects_frozen_preregistration_and_exact_carriers",
      "tests/gate2/integration/test_scale_restart_decision.py::test_receipt_binds_exact_dependencies_and_synthetic_scope",
      "tests/gate2/integration/test_scale_restart_decision.py::test_workload_bounds_and_freeze_are_recorded_before_measurements",
      "tests/gate2/integration/test_synthetic_run_evidence_bundle.py::test_both_runs_self_verified_at_execution_time",
      "tests/gate2/integration/test_synthetic_run_evidence_bundle.py::test_disposition_justifies_no_additional_mechanism",
      "tests/gate2/integration/test_synthetic_run_evidence_bundle.py::test_durable_journals_are_complete_and_ordered",
      "tests/gate2/integration/test_synthetic_run_evidence_bundle.py::test_every_preregistered_metric_has_a_matching_committed_carrier",
      "tests/gate2/integration/test_synthetic_run_evidence_bundle.py::test_fault_injection_evidence_was_derived_from_executed_observations",
      "tests/gate2/integration/test_synthetic_run_evidence_bundle.py::test_identity_is_reproducible_across_independent_invocations",
      "tests/gate2/integration/test_synthetic_run_evidence_bundle.py::test_real_scale_evidence_remains_not_observed",
      "tests/gate2/integration/test_synthetic_run_execution.py::test_bounded_run_measures_every_preregistered_metric",
      "tests/gate2/integration/test_synthetic_run_execution.py::test_cli_run_executes_and_reports_disposition",
      "tests/gate2/integration/test_synthetic_run_execution.py::test_integrity_verification_detects_tampered_artifacts",
      "tests/gate2/integration/test_synthetic_run_execution.py::test_interruption_resumes_from_journal_without_duplicate_writes",
      "tests/gate2/integration/test_synthetic_run_execution.py::test_repeated_runs_reproduce_identity_but_not_wall_clock"
    ]

## 6. Alternatives and decision matrix

| Option | Test and artifact ownership | Evidence quality | Maintenance/risk | Decision |
|---|---|---|---|---|
| **A. Explicit two-lane manifest, tests run in owning repositories** | LAB synthetic tests stay LAB-owned; the 33 listed historical tests and their canonical artifacts/objects stay canonical-owned. | Separate commit/ref, environment and result per lane; no lane can imply the other's PASS. | Small documentation/CI-selection concept; requires canonical billing recovery and explicit focused S5-T1 test selection. | **Selected by owner.** Preserve all node IDs and unresolved state; prefer no mirror. |
| B. Read-only mirror of pinned artifacts/Git objects into LAB | Copy 25 historical prompt/evidence paths plus 8 Git-object/history dependencies into LAB. | Could reproduce bytes if every path/object is pinned and verified; does not reproduce the canonical repository identity by itself. | Adds duplicated canonical history, licensing/provenance/retention burden, maintenance drift; still does not fix the observed billing block. | Rejected as default. Consider only if a concrete compatibility requirement demands cross-repo execution and owner separately approves exact paths/objects. |
| C. Split pytest selection but leave canonical lane undefined | LAB selection omits exact canonical nodes; no artifact transfer. | Risks turning unresolved test coverage into a report-only exclusion unless a separately owned lane and result contract exist. | Smallest code diff, but weakens end-to-end visibility and may let omission appear green. | Rejected. The tests remain required and unresolved until their canonical lane executes. |
| D. Keep all tests in one combined LAB suite | Existing LAB copied tests continue to execute against LAB paths/objects. | Reproduces current missing-path/object blocker but does not test canonical ownership environment. | Couples two repositories; encourages fixture mirroring or misleading red/green interpretation. | Rejected. No artifact restoration or forced unification without a new owner decision. |

Option A is approved as the design direction. Any later implementation of selectors, workflow jobs, report schemas, or cross-repository invocation requires a separately scoped plan and approval; this design does not change any of them.

## 7. Six-cycle refinement record

1. **Cycle 1 — Live provenance:** verified LAB PR #4 comment/state, LAB base/head, canonical main, both canonical PR refs and exact file lists. Stale base delta is exactly two product-context docs.
2. **Cycle 2 — CI failure root cause and allowance interpretation:** checked active workflow YAML, Actions enabled state, 16 historical job annotations and inaccessible/empty log artifacts. Those canonical jobs reported a billing/spending-limit start refusal; that message does not prove included minutes were exhausted. The 2026-11-05 account-level UI showed Actions `Usage blocked`; owner clarified this is an overage-spending guard and reported about 3,000 included minutes remain. LAB PR #5 run `41928274424` succeeded on 2026-11-04. Preserve these distinct evidence types, refresh remaining allowance for the relevant account/repo before each future hosted run, and do not incur overage.
3. **Cycle 3 — Applicability and ownership:** compared PR file lists to workflow selectors; verified the bounded-admission test is absent from canonical main (404) and exists at PR #258 head as blob `5ecbbd33d9d136984424cdcb787669b83be4db84`; #259 is documentation-only. Confirmed the 33 historical test-source blobs and pinned dependencies above.
4. **Cycle 4 — Separation proposal:** assigned canonical-history tests/artifacts to canonical lane and LAB synthetic tests to LAB lane; both statuses remain independently required. No mirroring chosen.
5. **Cycle 5 — Alternatives and anti-goals:** evaluated two-lane, artifact mirror, selector-only split and combined-suite options. The owner approved A; mirror, exclusion, xfail and test weakening were rejected.
6. **Cycle 6 — Independent verification:** owner approved Option A and the design direction on 2026-11-05; PR #5 review findings were addressed with a same-candidate Task 3 topology and separate exact-set oracle. Revised plan receives a fresh independent review and exact-head verification; implementation remains subject to owner approval.

## 8. Acceptance contract for the eventual design and follow-up plan

- The test manifest contains exactly 33 unique pytest node IDs, all explicitly unresolved until actually run in canonical context; its set exactly equals independent oracle §5.3 and the later canonical-side pinned copy.
- Every row resolves to canonical test-source blob, required canonical artifact tree/blob or Git object identity, and the canonical Python 3.11/3.14 full-history execution context.
- LAB and canonical result ledgers have distinct repo, commit, workflow/job, interpreter and count fields; missing/blocked/not-run cannot be coerced to PASS.
- No fixture mirroring, test-selection change, workflow edit, source edit or expectation change occurs without a later separately approved implementation scope.
- PR #258 must carry bounded-admission source/test and workflow selection together on one reviewed candidate; exact-head hosted execution is required before claiming hosted-test verification.
- No real media, model, provider, render, production export, Gate promotion or merge is part of this work.

## Evidence references

- [LAB PR #4 and latest owner review comment](https://github.com/Centaurioun/video-intelligence-pipeline-2/pull/4#issuecomment-6643257050)
- [Canonical PR #258](https://github.com/Centaurioun/video-intelligence-pipeline/pull/258)
- [LAB PR #5 independent review comment](https://github.com/Centaurioun/video-intelligence-pipeline-2/pull/5#issuecomment-6644221451)
- [Canonical PR #259](https://github.com/Centaurioun/video-intelligence-pipeline/pull/259)
- Actions runs: #258 [40820177498](https://github.com/Centaurioun/video-intelligence-pipeline/actions/runs/40820177498), [40820177514](https://github.com/Centaurioun/video-intelligence-pipeline/actions/runs/40820177514), [40820177609](https://github.com/Centaurioun/video-intelligence-pipeline/actions/runs/40820177609), [40820177628](https://github.com/Centaurioun/video-intelligence-pipeline/actions/runs/40820177628); #259 [40821952898](https://github.com/Centaurioun/video-intelligence-pipeline/actions/runs/40821952898), [40821953002](https://github.com/Centaurioun/video-intelligence-pipeline/actions/runs/40821953002), [40821953085](https://github.com/Centaurioun/video-intelligence-pipeline/actions/runs/40821953085), [40821953053](https://github.com/Centaurioun/video-intelligence-pipeline/actions/runs/40821953053).
- Prior node/error inventory: [POST_MEGA17_INTEGRATED_REGRESSION_REPORT.md at PR #4 head `ce11bc50707cf517937c42dfd96e3f325fc1d62f`](https://github.com/Centaurioun/video-intelligence-pipeline-2/blob/ce11bc50707cf517937c42dfd96e3f325fc1d62f/docs/ai-studio-tasks/POST_MEGA17_INTEGRATED_REGRESSION_REPORT.md). This source is still in draft PR #4 and is not part of the `1fd14c0b…` base tree.
