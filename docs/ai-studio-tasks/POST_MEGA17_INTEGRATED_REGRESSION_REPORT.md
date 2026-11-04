# MEGA-17 sonrası birleşik regresyon raporu

Tarih: 2026-11-05
Kapsam: yalnızca sentetik testler, kaynak incelemesi ve LAB dokümantasyonu. Bu rapor gerçek Gate tamamlanması, üretim yetkisi veya medya işleme kanıtı değildir.

## Döngü 1 — Kaynak ve Git dayanağı

- LAB `origin/main`: `1fd14c0b246c8da97e07129f6b84173d86f6a500` (`Merge PR #3: record post-MEGA17 Codex integrated verification task`). İzole worktree/branch: `/private/tmp/vip2-post-mega17-audit`, `codex/post-mega17-audit-20261105`; başlangıç ağacı temizdi.
- Ana kullanıcı checkout'unda önceden var olan değişikliklere dokunulmadı. Yerel `main` `7ea814d5c4626ed6b371c01f282c8a9b0138ffa0` ve 19 commit gerideydi; bu nedenle aday güncel `origin/main` üstünden ayrı worktree'de üretildi.
- Kanonik VIP yalnızca okundu: güncel `main` `bee314b92981b9ae7ea38d83fe2dbae120c474e4`. Kanonik PR #258 açık/draft, head `5a60cd8e0abc021767b05c87ca50202822c049d0`; PR #259 açık/draft, head `e08382db65dcde703aadecc6ab329741f3c4b24c`.
- LAB PR #1 `9dedbe965e75d8214534ef51e939cc12f8892779`, PR #2 `f20f4a7efca1e9d93cb3925ec637cbf49893dc9b` commitlerinde birleşmiş. Canlı LAB main daha sonra `1fd14c0b…`'ye ilerlemiş.

## Döngü 2 — Hosted CI ve gerçek pytest

| Kaynak | Python | Kanıt | Sonuç |
|---|---:|---|---|
| Güncel LAB main `1fd14c0b…`, Actions run [41912239686](https://github.com/Centaurioun/video-intelligence-pipeline-2/actions/runs/41912239686) | 3.11 | job 126862542146; MEGA-17 adımı | 37 geçti, altı dosyanın tamamı çalıştı, skip yok |
| Aynı run | 3.14 | job 126862543156; MEGA-17 adımı | 37 geçti, altı dosyanın tamamı çalıştı, skip yok |
| PR #1+#2 birleşik commit `f20f4a7e…`, Actions run [41911453896](https://github.com/Centaurioun/video-intelligence-pipeline-2/actions/runs/41911453896) | 3.11 / 3.14 | hosted pytest çıktısı | iki sürümde de 37 geçti; kuyruk doğrulaması altı suite ve sıfır skip bildirdi |
| Bu rapor PR'si, ilk belge commit'i `f83ca9d0…`, Actions run [41915073493](https://github.com/Centaurioun/video-intelligence-pipeline-2/actions/runs/41915073493) | 3.11 | job 126872473149 | tüm workflow başarılı; altı MEGA-17 dosyasında 37 geçti, sıfır skip |
| Aynı PR run | 3.14 | job 126872472466 | tüm workflow başarılı; altı MEGA-17 dosyasında 37 geçti, sıfır skip |

Python 3.14.9 ile `PYTHONPATH=src:experiments:. python -m pytest -q` eşdeğer interpreter komutları bu worktree'de çalıştırıldı:

| Komutun kapsamı | Sonuç |
|---|---:|
| `tests/vip_lab` | 146 passed |
| MEGA-15, MEGA-16 ve MEGA-15/16 E2E | 26 passed |
| `tests/vip_lab/test_mega17_*.py` (altı suite) | 37 passed |
| Güncel workflow'daki Gate-1/product-path sentetik dosyaları | 146 passed |

Yukarıdaki gruplar kasıtlı olarak kısmen çakışır; sayılar bir toplam değildir. Yerel Python 3.11 bulunmadığından yerel sonucu `NOT_OBSERVED`; ilgili hosted sonucu başarılıdır.

Geniş Gate-0/1/2/3 ve FVS sentetik/source-only pytest denemesi önce normal import kipinde toplama sırasında duplicate `test_canonical_json`, `test_ranking`, `test_schemas` modül adlarına ve Gate-2 `test_verify.py` içindeki bulunmayan tarihsel kontrat yoluna takıldı. `--import-mode=importlib` ile ve yalnızca bu Gate-2 testini dışarıda bırakarak kapsamlı tekrar yapıldı: **2,043 passed, 26 failed, 7 errors**. Bunlar yeşil kabul edilmedi.

Temsilî gerçek eksikler tekrarlandı: H3-A04 ve H3-C05 sabitlenmiş prompt dosyaları `.orchestration/remaining-work/prompts/...` altında yok; Gate-2 CLI testi kabul edilmiş F01 Git commit'ini çözemiyor (`accepted F01 commit cannot be resolved`); Gate-2 evidence bundle `docs/agent-runs/2026-10-25-gate2-reliability-execution/evidence/run-v2/receipt.json` dosyasını bulamıyor. Bunlar MEGA-17 davranışına atfedilmedi. İlk kapsamlı koşudaki aynı tarihsel fixture/ref bağımlılıkları giderilmediğinden geniş eski Gate kapsamı sertifikalandırılmıyor.

## Döngü 3 — Kaynak koruma, CLI ve lineage

`src/gate0/media/` altı Git blob'u güncel LAB main'de beklenenle birebir aynı:

| Yol | Git blob |
|---|---|
| `__init__.py` | `b1198560f5c8582b8be8725fed9412597ca08e96` |
| `decode.py` | `a3c7efad5fdc0c24e7f592512ef176e10e95f128` |
| `probe.py` | `d95b15505550f54263463e6bcbb9681f00620f17` |
| `proc.py` | `244706e9c198ab25afad5894a977cc1a31b39755` |
| `source_guard.py` | `9b0a7a64e7b163c94ad5ed62ba16bfedda99c398` |
| `tool_identity.py` | `056447631d477f57776c4db5e75cb8bad25b8ebd` |

MEGA-03…17 source/test paketleri izinde mevcut; güncel main ağacında bu alanlardan beklenmeyen silme yok ve medya Python dosyaları `.gitignore` tarafından göz ardı edilmiyor.

MEGA-16 CLI sabit, kod tarafından belirlenen `outputs/vip_lab/synthetic-reports` köküne hapsolmuş. Harici mutlak input/output yolunu `stat`/read/write/dizin oluşturma öncesinde reddediyor; CLI root override sunmuyor. `test_mega16.py` yalnız pytest içinde özel root sabitini `monkeypatch` ile değiştiriyor. Mevcut kod ve regresyonlar symlink/no-follow traversal, `.json` sınırı, regular file ve boyut sınırı, URI/medya reddi, no-clobber (`O_EXCL`), descriptor-relative traversal, kısmi write döngüsü, başarısız yazı sonrası eksik dosya temizliği ve salt-okunur verify davranışını koruyor. Bu incelemede kod değişikliği yapılmadı.

MEGA-17 gerçek `SyntheticLabScenario` nesnesini MEGA-15/16 producer API'sine geçiriyor. `SINGLE_ARM` ve `THREE_ARM` E2E suite'leri kaynak revision/occurrence kimliğini, source/query/arm üyeliğini, digest lineage'ını ve karışık senaryo/tahrif edilmiş lineage retlerini kapsıyor. Testler 37/37 geçti. Kaynak admission, insan editorial kararı, PTS ölçümü veya QC otoritesi sentetik declaration'dan yükseltilmiyor; sahte insan/PTS/QC iddialarına ret testleri mevcut.

## Döngü 4 — Gate sözleşmeleri ve yetki sınırları

Kanonik Gate-0 protokolü 60–120 dakika izinli corpus, en az 3 oturum/6 kaynak revizyonu; 24 pozitif değerlendirme sorgusu (dört ailede 6'şar), 8 makul absent evaluation sorgusu, ayrı 8 development sorgusu, iki bağımsız insan reviewer, bir metadata baseline ve tek sınırlı yerel semantic-visual kol belirler. Ölçütler grade-2 `Hit@10 >= 20/24`, eşli artış `>=5/24`, aile başına `>=3/6`. Üç profil SigLIP/SigLIP2 kıyaslaması Gate-1 yetkinlik kararıdır. MEGA-17 Gate-0 sentetik hazırlığı bu bölünmeye uyumlu; kanonik experiment'i çalıştırdığı iddiası yok.

MEGA-17 `source_readiness.py` generative/synthetic D-2 fixture doğrular. `gate0.media.source_guard.assert_source_ok`, `vip_fvs.s5_admission.admit_source_bytes`, `vip_fvs.e01_admission_seam.verify_source_admission_for_e01` veya `vip_fvs.review_bundle.seal_review_bundle` çağrılmaz; repo dosyalarını/önkoşulları statik olarak saymak gerçek admission değildir. Bu sınır `MEGA_17_CROSS_WORKSTREAM_ACCEPTANCE.md` ile aynı şekilde açıklanmış.

Gate-3'te semantic timestamp frame boundary değildir; VFR için nominal FPS ile frame üretme yasaklıdır. Source-native PTS/timebase, A-7 stream namespace, IT-6 terminal-tail kararları sentetik testlerde sahte gerçek kanıta dönüştürülmemiştir. İnsan kararından ayrı model/tool önerisi, versioned edit plan, teknik ve insan visual/audio QC, render/export refusal korunan sınırlar olarak kaldı. Herhangi real media stat/hash/read, model/provider, encode/render/export, Gate promotion çalıştırılmadı.

## Döngü 5 — Portability delta

Kanonik `main`'de çağrılan S5-T1 API'lerin hiçbiri PR #258'deki yeni modüllerle aynı isimde mevcut bulunmadı. PR #258 descriptor-based, bounded synthetic admission ve 454 satırlık unit suite ekliyor; PR #259 continuity handoff belgesidir. İki PR de draft/open. GitHub'ın güncel PR check görünümü #258 ve #259 için Gate-0 D1, Gate-0 broad, Gate-2 report/receipt ve synthetic smoke check'lerini failed gösteriyor; ilişkili run'lar 2–3 saniyede bitmiş, job step/log erişilebilir değil (`log not found`). Dolayısıyla check başarısız; bu kanıtla sebebi belirlenemiyor. Yeni S5-T1 kabul kodunu birleştirmek review/CI durumu ve D-2/D-3 sınırı çözülene kadar beklemeli.

## Döngü 6 — Sonuç ve durum

Sentetik MEGA-17 ve tanımlı LAB workflow regresyonları güncel hosted CI ve ilgili yerel gruplarda geçti. Ancak tüm Gate-0…3/FVS historical suite yeşil değil, Python 3.11 yerel olarak yok ve canonical PR check durumu başarısız/logsuz. Bu nedenle son sınıflandırma: **`POST_MEGA17_CI_OR_CONTRACT_BLOCKED`**.

Kanıt sınırı: hosted CI sentetik yazılım sözleşmelerini test eder; gerçek kaynak hakkını, insan reviewer kararını, model kalitesini, Gate kararını, export iznini veya production hazır oluşunu doğrulamaz.

## Yayın öncesi repo doğrulaması

`bash scripts/verify-workspace.sh` çalıştırıldı ve 27 failure bildirdi. Failure'lar LAB fork'ta olmayan tarihsel canonical VIP materyallerini (`Video_Intelligence_Pipeline_Raporu_v1.0.md`, Astra audit kayıtları, `reference-pack/`, prototype dosyaları ve eski orchestration memo'ları) zorunlu sayıyor; ayrıca bu review worktree'si `main` değil ve verifier canonical VIP origin bekliyor. Bu yüzden verifier bu LAB isolated branch için uygulanabilir acceptance testi değildir. Aynı verifier açıkça `PASS high-confidence secret scan has no tracked-file matches` ve `DISABLED ... DEVELOPMENT_SOURCE_AUTH_ENFORCEMENT=DISABLED_BY_OWNER` bildirdi. Kodun veya verifier policy'sinin kapsamı bu işte değiştirilmedi.
