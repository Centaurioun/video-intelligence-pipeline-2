# MEGA-08–14 Phase B bağımsız denetim bulguları

**İncelenen LAB main:** `46cedd19512b8b30ac99d169908ce6716d65c165`  
**Uygulama:** `59958b91987b89da8a495d50086e198aade4ae4b`  
**Restorasyon:** `ddde7df49d2abe46a482d291cc38ece1ddcb40b3`  
**Actions:** [41763786941](https://github.com/Centaurioun/video-intelligence-pipeline-2/actions/runs/41763786941), head `ddde7df…`, `failure`  
**Sınırlama:** Bu audit exact main SHA'daki kaynak incelemesi ve hosted CI logudur; yerel test çalıştırılmadı.

## Sonuç

`59958b9` MEGA-08–14 kod ve testlerini ekledi, ancak aynı commit altı `src/gate0/media/**` dosyasını sildi. `ddde7df` bu altı dosyayı ayrı commit ile geri eklemiştir. Başlangıç `22f1ffa` ile `origin/main` arasındaki ağaçta altı dosyanın tamamı vardır; restorasyon sonrası bu dosyalarda silinme yoktur. `59958b9` tek başına koruma koşulunu ihlal eder ve CI'da aynı nedenle bağımlı testlere de zarar verebilirdi. `git diff --check 59958b9^..59958b9` temizdir; bu, içerik/işlev doğruluğu değildir.

Actions her iki Python sürümünde de önceki 307 baseline testini PASS etti. Yeni wave sonuçları: M08 5 PASS/5 FAIL; M09 6 PASS; M10 6 PASS; M11 5 PASS; M12 4 FAIL; M13 4 FAIL; M14 import/collection aşamasında 2 ERROR, davranış testleri çalışmadı. Aggregate enforcement doğru şekilde başarısız oldu. Run genel olarak FAILED; yeni dalgalar doğrulanmış veya tamamlanmış değildir.

## Bulgular

### B-01 — P1 — MEGA-08'in izinli referans kümesi kendi varsayılan girdisiyle çelişiyor

`src/vip_lab/mega08/capability_inventory.py:227-231` tüm girdileri `ALLOWED_INVENTORY_PREFIXES` ile kısıtlıyor; `:324-347` bu kontrol sonrası hedefi doğrudan açıyor. Varsayılan envanterin `docs/decisions/2026-10-29-a7-s5-scoped-synthetic-tdd-plan-owner-adoption.md` advisory referansı bu allowlist dışında kalıyor. Actions iki sürümde de 3 envanter testi bu nedenle `INVENTORY_PATH_NOT_ALLOWLISTED` ile düşmüş; forged-authorization testi de hedeflenen blok durumuna ulaşmadan `INVALID` alıyor.

**Öneri/test:** AST ile incelenen yürütülebilir Python kaynaklarını kapalı advisory doküman referanslarından ayırın. Traversal, mutlak yol, symlink ve bilinmeyen dosya retleri sürmeli. Geçerli varsayılan envanterle contract-gate forged claim testi hedef `BLOCKED/NOT_AUTHORIZED` sonucuna ulaşmalı; allowlist dışı keyfi yol hâlâ reddedilmeli.

### B-02 — P1 — MEGA-12 ve MEGA-13 kanonik Gate-2 API'leriyle uyumsuz

`src/gate2/workload.py:32-45` `WorkloadSpec` alanları `jobs/stages/artifact_bytes/cost_units/fault_position/seed/...` şeklindedir. `src/vip_lab/mega12/replay_graph.py:109-125` ve `:134-152` ise olmayan `workload_id/job_count/stages_per_job/payload_bytes` alanlarını varsayıyor; `RecoveryBinding`'i yalnızca iki alanla kurup olmayan `RecoveryHarness(binding)` ve `run_job()` biçimini çağırıyor. Gerçek `RecoveryBinding` 10 alanlıdır (`src/gate2/recovery.py:21-32`), gerçek harness `open(checkpoint_path, binding, adapter)` ve `run(crash_point=...)` sunar (`:116-138`). `fault_scenarios.py:82-165` aynı hayali workload alanlarını tüketiyor. Actions'ta test fixture `WorkloadSpec(workload_id=...)` sebebiyle M12'nin dört testi düşmüş; M13'ün dört testi aynı hatalı fixture nedeniyle başlamadan düşmüş.

**Öneri/test:** Kanonik Gate-2 üreticisini/API'sini adapte edin, canonical `WorkloadSpec` alanı eklemeyin. Tüm binding değerlerini gerçek sentetik kimliklerden üretip adapter receipt kontrolü ve idempotence akışını çalıştırın. Pozitif replay, yinelenen replay, yanlış generation/space, bozuk JSONL, desteklenmeyen FaultClass ve arşiv ölçeği iddiası yok testleri ekleyin. M13 gerçek M12 grafiğiyle çalışıp lineage/QC negatiflerini ayrıca doğrulamalı.

### B-03 — P1 — MEGA-14 paket import'u collection'ı engelliyor

`src/vip_lab/mega14/__init__.py:3` `MEGA_08_14_SPEC_VERSION`'ı `vip_lab.mega08.gap_digest` içinden import ediyor; sabit `capability_inventory.py` içinde tanımlı, `gap_digest.py` içinde değil. Actions'ta M14 ve E2E iki test modülü bu nedenle collection aşamasında import error aldı; M14 davranışı `NOT_EXECUTED`.

Düzeltme yalnız import yolunu onarmakla bitmez: `scenario.py:127-131,259-263` ve `orchestrator.py:329-335` kanonik olmayan WorkloadSpec alanlarını kullanıyor; MEGA-12/13 bağımlılık zinciri de aynı API uyuşmazlığını taşıyor.

**Öneri/test:** Spec sürümü için tek yetkili modül kullanın; `import vip_lab.mega14`, CLI ve E2E koleksiyonunu sınayın. Ardından tam producer→consumer zincirini gerçek sentetik retrieval, batch verifier, recovery, QC ret ve digest doğrulamasıyla çalıştırın. CLI yasak gerçek/provider/render/download bayraklarını herhangi bir yan etkiden önce reddetmeli.

### B-04 — P2 — MEGA-12 ölçüm kanıt sınıfı sözcüğü belirsizliği

`src/vip_lab/mega12/consistency_review.py:33-64` yalnızca sentetik in-memory sayaçları `Measurement(evidence="MEASURED")` olarak kaydediyor; kaynak etiketleri sentetik olduklarını belirtiyor ve arşiv metrikleri `NOT_OBSERVED` kalıyor. Bu, proje sözleşmesindeki `MEASURED` sınıfıyla karıştırılmaya açık bir raporlama yüzeyidir; CI bunu doğrulamış sayılmaz.

**Öneri/test:** Projenin `Measurement` evidence enum/serializer sözleşmesiyle kıyaslayın; sentetik sayaçları `MEASURED` şeklinde etiketlemek gerçekten kabul ediliyorsa raporda bunun sentetik fixture ölçümü olduğu açık, makinece ayrıştırılabilir alanla taşınmalı. Hiçbir tüketici bunları kaynak/üretim ölçümüne yükseltememeli.

## Yeniden kullanım / kapsam

Kod MEGA-09 ve MEGA-14'te mevcut `run_batch_retrieval` ve `verify_batch_report` API'lerini çağırıyor (`mega09/candidate_queue.py:30,356`; `mega14/orchestrator.py:16,18,220-280`); görünür bir ikinci genel retrieval/report-verifier klonu saptamadım. MEGA-12 `RecoveryHarness`'ı isim olarak kullanıyor fakat gerçekte onun API'siyle uyumsuz çağırıyor; bu bir kanonik işlevi doğru tüketme değil. MEGA-14'te kaynak içeriğini açan/network/provider/FFmpeg çağrısı taranan kodda görülmedi; `Path` oluşturma ve sentez index adları mevcut. Bu statik tarama tüm davranışsal yan etkilerin yokluğunu kanıtlamaz.

## Güncel dal / remediation durumu

`origin/main` şu an `46cedd1…` ve yalnızca `docs/ai-studio-tasks/MEGA_08_14_HOSTED_CI_REMEDIATION_2026-11-04.md` eklemiştir. Belge kök nedenleri ve onarım planını tanımlar, fakat kaynak/test onarımı veya yeni CI run değildir. Dolayısıyla AI Studio remediation **NOT_YET_SUBMITTED**; sonraki yeni immutable main SHA ve exact-head Actions run ayrıca denetlenmelidir. Bu denetimin adayı: **CHANGES_REQUESTED**.
