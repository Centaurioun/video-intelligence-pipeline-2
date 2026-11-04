# MEGA-17 Sonrası İki Test Lane'i — Uygulama Planı

> **Uygulayıcı notu:** Bu plan henüz uygulama yetkisi vermez. Owner planı inceleyip ayrıca uygulamayı yetkilendirmelidir. Uygulama başladığında davranış değişiklikleri test-first yapılır; CI kök nedenleri sistematik hata ayıklamayla, sonuç iddiaları doğrulama-before-completion ile ele alınır.

**Goal:** LAB sentetik regresyonlarını ve canonical geçmişe bağlı 33 testi sahip oldukları depolarda, ayrı sonuç ve kanıt makbuzlarıyla çalıştırmak; PR #258 bounded-admission testini Python 3.11 ve 3.14 hosted CI'da açıkça yürütmek.

**Architecture:** LAB lane mevcut sentetik workflow'unu ve altı MEGA-17 suite'ini korur; ayrı bir JUnit/JSON receipt üretir. Canonical-history lane, 33 exact pytest node ID'sini sahiplik, artifact ve Git kimlikleriyle manifestte tutar ve canonical repository içinde çalıştırır. PR #258'in yeni bounded-admission suite'i canonical smoke workflow matrisinde ayrıca seçilir. İki sahiplik lane'i korunur; üç ayrı evidence slice (LAB synthetic, canonical-history 33, PR #258 bounded admission) raporlanır ve birbirini ya da birleşik PASS'i temsil etmez.

**Tech Stack:** GitHub Actions, Python 3.11/3.14, pytest, JUnit XML, JSON evidence receipts, Git object/ref verification.

**Spec:** docs/ai-studio-tasks/POST_MEGA17_TEST_LANE_SEPARATION_DESIGN.md; görev sınırları ayrıca docs/ai-studio-tasks/POST_MEGA17_LAB_MAIN_INTEGRATED_VERIFICATION_AND_CANONICAL_PORTABILITY.md ile uyumlu olmalıdır.

## Global Constraints

- Tarihsel 33 pytest node'u UNRESOLVED kalır; yalnız gerçek canonical-context yürütme sonucu statülerini değiştirir.
- Hiçbir test silinmez, sessizce seçilmez, xfail yapılmaz, beklentisi zayıflatılmaz veya fixture'ı LAB'ye kopyalanmaz.
- LAB synthetic ve canonical-history iki ayrı sahiplik lane'idir. PR #258 bounded-admission canonical lane içinde ayrı workflow/evidence slice olarak ölçülür; üç ayrı receipt/result gösterilir, tek “combined PASS” üretilmez.
- Kanonik kod, tarihsel test beklentileri ve protected media bu planın parçası değildir; PR #258/#259 base güncellemesi owner kontrollü ayrı GitHub işlemi olarak kalır.
- GitHub Actions bütçesi 2026-11-05'te Usage blocked gözlendi. Owner/admin engeli kaldırıp aynı billing ekranında Usage blocked olmadığını yeniden doğrulamadan workflow dispatch/rerun yapılmaz.
- PR #258'in yeni tests/vip_fvs/unit/test_bounded_admission.py testi canonical repo ve gerçek PR head üzerinde Python 3.11/3.14'te sıfır skip ile yürütülmeden hosted-test doğrulaması sayılmaz.
- Workflow'lar mevcut pull_request/push politikasını korur; tarihsel ref erişimi açık doğrulanır. fetch-depth: 0 tek başına preserved ref'in mevcut olduğunu kanıtlamaz.
- Gerçek media, model indirme/çalıştırma, provider, render/export, Gate promotion veya merge yapılmaz.
- Her receipt repo, commit/tree SHA, PR base/head/merge SHA (varsa), workflow path+blob SHA, run/job ID, Python ve pytest sürümü, lockfile SHA-256, manifest SHA-256, node ID'leri ve pass/fail/error/skip/deselected sayımlarını taşır.

## Review Focus

- **Billing gate hâlâ kapalıyken workflow başlatma:** workflow dispatch öncesi GitHub Actions budget durumunun Usage blocked olmadığını kanıtlayan owner/admin doğrulaması gerekir.
- **33 node'un manifestten düşmesi veya yanlış owner'a atanması:** doğrulayıcı tam node-ID kümesinin design envanteriyle birebir eşitliğini ve canonical-history owner'ını kontrol eder.
- **Tarihsel Git ref/object runner'da yokken testleri çalışmış varsayma:** preflight pinned commit/tree/blob ve archive ref'i testten önce doğrular; eksikse lane BLOCKED ve test UNRESOLVED kalır.
- **Collection sırasında skip/deselect veya Python matrisi eksikliği:** JUnit ve pytest collection çıktısı iki interpreter için beklenen node'ların toplandığını ve skip/deselected olmadığını doğrular.
- **Bir lane'in diğerini PASS göstermesi:** her workflow ayrı status context ve artifact üretir; aggregator/ortak yeşil badge eklenmez.

---

## Önkoşullar ve bağımlılık sırası

1. **Billing owner gate (harici):** GitHub Actions Usage blocked durumunu hesap owner/admin giderir. Kod/CI değişikliği bu adıma bağlı değildir; hosted kanıt ve rerun bu adım tamamlanana kadar bekler. Ödeme ayarlarına Codex dokunmaz.
2. **Canonical PR zemini:** PR #258 ve #259 eski 592952da… base'indedir; main@bee314b92981b9ae7ea38d83fe2dbae120c474e4 iki doküman ileridedir. Owner, PR base yenilemesi/rebase kararını ayrıca verir. #258 workflow güncellemesi yeni default branch üzerinde görünmeden PR'ın yeni bounded-admission testi tetiklenemez.
3. **Uygulama onayı:** aşağıdaki plan bağımsız lane sınırlarını tanımlar, ancak workflow/manifest değişikliğine başlamadan owner'ın planı ve uygulama kapsamını onaylaması gerekir.
4. **DAG:** Task 1 (canonical node manifesti) → Task 2 (canonical tarihsel lane) → Task 5 (entegrasyon/kanıt). Task 3 (bounded-admission hosted testi) ayrı dosya sınırında paralel hazırlanabilir. Task 4 (LAB receipt) Task 2/3'ten bağımsızdır. Hosted işler Task 2–4 tamamlanınca billing gate ve ilgili PR/default-branch koşullarına bağlıdır.

## Dosya haritası

| Dosya | Sorumluluk |
|---|---|
| docs/testing/POST_MEGA17_CANONICAL_HISTORY_TEST_MANIFEST.json (yeni, canonical VIP) | 33 sabit node ID, owner, test-source blob, gereksinim kümeleri, pinned path/ref/object ve execution lane metadata. |
| scripts/validate_canonical_history_manifest.py (yeni, canonical VIP) | Şema/benzersizlik/tamlık ve object/path preflight doğrulaması; pytest seçimi üretimi. |
| tests/scripts/test_validate_canonical_history_manifest.py (yeni, canonical VIP) | Manifest doğrulayıcı ve workflow contract regresyonları. |
| .github/workflows/canonical-history-regressions.yml (yeni, canonical VIP) | Yalnız manifestteki 33 node'u 3.11/3.14'te yürütüp lane'e özel receipt/artifact üretimi. |
| .github/workflows/python-synthetic-smoke.yml (mevcut, canonical VIP) | PR #258 bounded-admission suite'ini 3.11/3.14 mevcut smoke matrisine açık ekleme; ayrı receipt. |
| .github/workflows/vip-ai-studio-synthetic-ci.yml (mevcut, LAB) | Mevcut altı MEGA-17 suite doğrulamasını koruyup LAB lane receipt'ini artifact olarak yayımlama. |
| docs/ai-studio-tasks/POST_MEGA17_TEST_LANE_SEPARATION_DESIGN.md | Altı döngülü tasarım ve 33 test kanıt envanteri. |
| docs/ai-studio-tasks/POST_MEGA17_TEST_LANES_EXECUTION_PLAN.md | Bu uygulama sırası, sınırlar ve kabul ölçütleri. |

Canonical dosyalar yalnız ayrı, sonradan owner-onaylı canonical branch/PR'de değiştirilebilir. Bu LAB plan dalı canonical dosya içermez.

---

## Task 1: Canonical-history test manifesti ve fail-closed doğrulayıcı

**Files:**
- Create: docs/testing/POST_MEGA17_CANONICAL_HISTORY_TEST_MANIFEST.json (canonical VIP)
- Create: scripts/validate_canonical_history_manifest.py (canonical VIP)
- Test: tests/scripts/test_validate_canonical_history_manifest.py (canonical VIP)

**Interfaces:**
- Manifest alanları: schema_version, lane_id=canonical-history, owner_repository=Centaurioun/video-intelligence-pipeline, canonical_base_sha, python_versions=[3.11,3.14], expected_node_count=33, nodes[].
- Her node kaydı: node_id, owner_repository, test_path, test_source_blob, required_artifacts[], required_git_objects[], required_refs[], prior_status=UNRESOLVED.
- validate_manifest(manifest_path, repo_root) tam doğrulama yapar; CLI geçerli node ID listesini JSON olarak yazar: python scripts/validate_canonical_history_manifest.py --manifest docs/testing/POST_MEGA17_CANONICAL_HISTORY_TEST_MANIFEST.json --repo-root . --emit-nodeids.

- [ ] **Adım 1: Kırmızı testleri yaz.** Tam 33 ID, tekrar eden ID, 32/34 kayıt, yanlış repo owner'ı, boş digest/ref, yanlış pinned blob, eksik archive ref, manifest status'unda PASS/RESOLVED ve bilinmeyen alanları kapsa.
- [ ] **Adım 2: Test-first doğrula.** python -m pytest -q tests/scripts/test_validate_canonical_history_manifest.py; başlangıçta yeni arayüz nedeniyle FAIL beklenir.
- [ ] **Adım 3: Manifesti tasarım envanterinden üret.** 33 ID'yi POST_MEGA17_TEST_LANE_SEPARATION_DESIGN.md tablosuyla birebir eşle; mevcut SHA/ref ve artifact grup üyeliğini yaz; içerik kopyalama yok.
- [ ] **Adım 4: En küçük doğrulayıcıyı uygula.** ID kümesi tam eşitliği, duplicate reddi, repo/path root sınırı, blob/tree/commit türü ve SHA doğrulaması, ref resolution ve tüm geçmiş statülerinin UNRESOLVED oluşunu denetle. Preflight hata verirse nonzero çık; test seçimi üretme.
- [ ] **Adım 5: Test ve preflight doğrula.** Aynı pytest komutu; ardından manifest CLI. Beklenen: 33 benzersiz ID ve tüm pinned dependencies mevcut canonical checkout'ta geçerli. Yerel tree'de dependency eksikse BLOCKED kaydet, fixture kopyalama.
- [ ] **Adım 6: Yalnız manifest/validator/test değişikliklerini commit et.** test: define canonical history lane manifest.

**Kabul:** Tam 33 ID, birebir design set eşitliği, canonical owner ve UNRESOLVED statüsü; eksik obje/ref/artifact fail-closed olur; LAB testlerinden hiçbiri seçilmez.

## Task 2: Canonical-history için bağımsız Python matrisi ve receipt

**Files:**
- Create: .github/workflows/canonical-history-regressions.yml (canonical VIP)
- Modify only if needed: tests/scripts/test_validate_canonical_history_manifest.py

**Interfaces:**
- Trigger pull_request ve workflow_dispatch (canonical repo branch policy'sine göre); Python matrix 3.11/3.14; receipt canonical-history-receipt.json, JUnit canonical-history-junit.xml.
- Job explicit full-history checkout yapar; archive ref'in varlığını ve manifestteki Git object/path kimliklerini doğrular. Open PR head için base/head/merge kimlikleri receipt'e yazılır.

- [ ] **Adım 1: Workflow contract testi yaz.** İki Python sürümünü, validator çağrısını, JUnit/receipt çıktısını doğrula; mevcut gate0-broad-synthetic-regressions.yml ve gate2-receipt-report-regressions.yml seçimlerinin değişmediğini kontrol et.
- [ ] **Adım 2: Kırmızı doğrula.** python -m pytest -q tests/scripts/test_validate_canonical_history_manifest.py::test_history_workflow_contract; workflow henüz yokken FAIL.
- [ ] **Adım 3: Fail-closed workflow ekle.** Preflight başarısızsa pytest'e geçme. Node ID listesini shell string'e birleştirmek yerine subprocess argv ile geçir: python -m pytest -q --import-mode=importlib --junitxml=<runner-temp>/canonical-history-junit.xml [33 validated node IDs]. Boş/eksik/duplicate selection workflow'u başarısız kılar. Her matrix job kendi receipt/artifact'ini yükler.
- [ ] **Adım 4: Receipt doğrulayıcı testlerini ekle.** Eksik/ekstra node, skip, deselection, collection mismatch, import/setup error, missing ref ve workflow SHA yokluğu durumlarını fail-closed test et.
- [ ] **Adım 5: Yerel doğrulama.** python -m pytest -q tests/scripts/test_validate_canonical_history_manifest.py; iki interpreter varsa manifestten üretilen exact 33 node listesini her ikisinde çalıştır. Interpreter yoksa NOT RUN yaz, CI başlatma.
- [ ] **Adım 6: Yalnız canonical manifest validator, tests ve workflow'u commit et.** ci: add canonical history regression lane.

**Kabul:** Her Python job'u 33 node için collection/execution sayısını receipt'te kaydeder; skip/deselected sıfır; eksik ref, hata veya artifact PASS olamaz. Mevcut Gate-0/Gate-2 broad workflows değişmeden kalır. Lane yalnız canonical repoda çalışır.

## Task 3: PR #258 bounded-admission testini hosted matrise ekleme

**Files:**
- Modify: .github/workflows/python-synthetic-smoke.yml (canonical VIP)
- Test: canonical workflow selection contract test (repo'daki mevcut contract-test yeri önce doğrulanır)

**Interfaces:**
- Test target tests/vip_fvs/unit/test_bounded_admission.py.
- Python matrix mevcut 3.11/3.14; bounded-admission-junit.xml ve bounded-admission-receipt.json.

- [ ] **Adım 1: Selection contract test yaz.** Her iki Python job'unda tam test yolunun seçildiğini, receipt/JUnit oluştuğunu ve continue-on-error/skip/xfail gibi başarıyı örten kural olmadığını doğrula.
- [ ] **Adım 2: Kırmızı doğrula.** Seçilen contract testi mevcut workflow'da bounded-admission target'ı bulamadığı için FAIL olmalı.
- [ ] **Adım 3: Ayrı focused step ekle.** python -m pytest -q --junitxml=<runner-temp>/bounded-admission-junit.xml tests/vip_fvs/unit/test_bounded_admission.py. Mevcut setup/import path kullan; test/asertion değiştirme.
- [ ] **Adım 4: Receipt ve lokal test.** Receipt repo/head, workflow SHA, run/job, Python/pytest, lock hash ve pytest counts yazar. Canonical checkout'ta PYTHONPATH=src:experiments:scripts python -m pytest -q tests/vip_fvs/unit/test_bounded_admission.py; 3.11/3.14 gerçek counts kaydedilir. Geçmişte bildirilen 22 test sayısı zorlanmaz.
- [ ] **Adım 5: Contract ve focused suite doğrula.** Yerel doğrulama sonrası hosted test yalnız billing gate açılıp ilgili owner run yetkisi varsa yürütülür.
- [ ] **Adım 6: Yalnız smoke workflow ve contract testini commit et.** ci: run bounded admission suite in synthetic smoke.

**Kabul:** PR #258 test dosyası iki interpreter job'unda gerçek pytest execution, sıfır skip/deselection ve receipt/JUnit üretir. Workflow canonical default branch'te görünmeden PR #258 için hosted test iddiası kurulmaz. Suite media/model/provider/render çağırmaz.

## Task 4: LAB sentetik lane için receipt

**Files:**
- Modify: .github/workflows/vip-ai-studio-synthetic-ci.yml (LAB)
- Add: workflow runtime artifact lab-synthetic-receipt.json; generated receipt repo'ya commit edilmez.

**Interfaces:**
- Lane ID lab-synthetic; altı mevcut MEGA-17 suite ve workflow'un legacy synthetic coverage'ı; Python 3.11/3.14.
- Her job ayrı JUnit ve lab-synthetic-<python> artifact yükler.

- [ ] **Adım 1: Receipt contract test yaz.** Mevcut CI validator'ı varsa kullan; yoksa zorunlu repo/ref/workflow identity, python/pytest, lock hash, counts, exact test list, zero skip/deselect ve exit status alanlarını kapsa.
- [ ] **Adım 2: Kırmızı doğrula.** Receipt alanları yokken contract testi FAIL olmalı.
- [ ] **Adım 3: Workflow'a receipt üretimi/upload ekle.** Mevcut altı suite presence/execution/no-skip kontrolünü ve legacy coverage'ı değiştirme.
- [ ] **Adım 4: Regression doğrula.** Receipt contract testi ve mevcut exact suite validator; mevcut YAML/actionlint aracı varsa kullan, dependency ekleme.
- [ ] **Adım 5: Yalnız LAB workflow ve testini commit et.** ci: publish separate lab synthetic test receipt.

**Kabul:** Her Python job'u ayrı LAB receipt/artifact üretir; coverage veya MEGA-17 suite seçimi azalmaz; receipt canonical-history başarısı ima etmez.

## Task 5: İki lane ve üç evidence slice'ı uzlaştırma; exact-head kapanışı

**Files:**
- Evidence update: docs/ai-studio-tasks/POST_MEGA17_TEST_LANE_SEPARATION_DESIGN.md
- Add: docs/ai-studio-tasks/POST_MEGA17_TEST_LANES_EXECUTION_RECEIPTS.md (ilgili repo/PR'de; secret/billing kişisel bilgisi yok)

**Interfaces:**
- Ayrı evidence bölümleri: LAB_SYNTHETIC (sahiplik lane L), CANONICAL_HISTORY_33 (sahiplik lane C), PR258_BOUNDED_ADMISSION (lane C içinde ayrı focused test slice'ı).
- Status: PASS, FAIL, BLOCKED, NOT RUN, UNRESOLVED. PASS yalnız exact beklenen node set'i çalışıp tümü geçtiğinde, skip/deselect yokken verilir.

- [ ] **Adım 1: Receipt consistency test yaz.** Üç evidence receipt'inin iki sahiplik lane'ini doğru gösterdiğini, PR #258 sonucunun canonical lane'e ait olduğunu, ortak overall PASS üretmediğini ve 33 canonical node için tek tek sonuç bulunduğunu doğrula.
- [ ] **Adım 2: Kırmızı doğrula.** Eksik receipt, billing block, eski workflow SHA, stale PR head, node mismatch, skip/deselect veya Git object yokluğu PASS üretememeli.
- [ ] **Adım 3: Receipt'i exact ref'e bağla.** Repo, base/head/merge SHA, tree SHA, workflow SHA, run/job URL/ID, Python/pytest, lock hash, manifest hash, node list/counts, artifact digest ve billing gate gözlem zamanını karşılaştır.
- [ ] **Adım 4: Hosted kabul kapısı.** Run'dan hemen önce owner/admin billing ekranında Actions Usage blocked olmadığını gözle; PR base/head güncelliğini kontrol et. #258 workflow değişikliği default branch'te değilse önce owner-controlled default-branch entegrasyonu gerekir. Ayrı owner run yetkisi olmadan dispatch/rerun yapma.
- [ ] **Adım 5: Gözlenen sonuçları raporla.** Her Python job ve node için PASS/FAIL/ERROR/SKIP/NOT RUN yaz. Koşmayan canonical node'lar UNRESOLVED kalır. Yeni kanıt olmadan hata kök nedeni genellenmez.
- [ ] **Adım 6: Yalnız gözlenen kanıtı belgeleyen reconciliation commit'i üret.** Kaynak ve test beklentisi değiştirme.

**Kabul:** İki sahiplik lane'i ve üç ayrı evidence sonucu görünürdür; canonical 33 sonuç tam veya node-bazlı unresolved/blocker olarak raporlanır; LAB PASS canonical statüsüne geçmez; #258 exact PR head üzerinde iki Python/0 skip ile kanıtlanır.

---

## Rollback ve güvenli sınırlar

- CI değişikliği geri alınacaksa owner-onaylı PR'de yalnız ilgili workflow/validator commit'i revert edilir; test veya beklenti değişiklikleri rollback bahanesi olmaz.
- Manifest pinleri ve historical tests değiştirilemez. Yanlış pin varsa ayrı kanıta dayalı review gerekir; tarihi testleri yeşile döndürmek için pin gevşetilmez.
- Billing gate kapalıyken hosted run başlatılmaz. Başlamış workflow başarısızsa root cause incelenmeden rerun yapılmaz.
- PR #258/#259 base yenilemesi, canonical main merge'i ve billing ayarları LAB planının uygulama/rollback kapsamı dışındadır.
- Yanlış ownership, ref veya eksik manifest lane'i BLOCKED yapar; fixture mirror veya skip çözüm değildir.

## Altı döngülü iteratif iyileştirme

1. **Cycle 1 — Kanıt ve sınır:** güncel refs, PR listeleri, workflow seçimleri, billing gate ve 33 node sahipliği tasarım belgesinde sabitlendi.
2. **Cycle 2 — Alternatifler:** iki lane, artifact mirror, seçimden çıkarma ve birleşik suite karşılaştırıldı; owner iki lane'i onayladı, mirror reddedildi.
3. **Cycle 3 — Bağımlılık haritası:** billing owner gate, stale canonical PR base, preserved refs ve default-branch workflow ihtiyacı sıralamaya bağlandı.
4. **Cycle 4 — Task/arayüz:** manifest → canonical lane → receipt zinciri; bounded smoke ve LAB receipt işleri ayrı dosya sınırlarıyla tanımlandı.
5. **Cycle 5 — Negatif kontroller:** eksik refs, node farkı, skip/deselect, stale head, billing block ve lane karışması fail-closed kabul koşullarına çevrildi.
6. **Cycle 6 — Özdenetim:** spec coverage, 33 node sayısı, dosyalar, komutlar, merge/billing yetkisi ve bağımsız sonuçlar yeniden kontrol edildi. Owner planı uygulama öncesi incelemelidir.

## Plan özdenetimi

- **Kapsam:** LAB lane, canonical-history lane, 33 node manifesti, canonical lane içindeki #258 focused test slice'ı, billing non-start, stale PR base, source provenance, ayrı receipts ve no-merge sınırları görevlere bağlandı.
- **Test-first:** her davranış/CI contract değişiminden önce negatif test ve komut tanımlandı; hosted kabul yerel doğrulamadan ayrıldı.
- **Kimlikler:** canonical gözlem main SHA bee314b92981b9ae7ea38d83fe2dbae120c474e4; LAB design base 1fd14c0b246c8da97e07129f6b84173d86f6a500; PR #258 kaydedilmiş head 5a60cd8e0abc021767b05c87ca50202822c049d0; PR #259 kaydedilmiş head e08382db65dcde703aadecc6ab329741f3c4b24c. Uygulamada tekrar fetch etmeden güncel sayılmaz.
- **Belirsizlik:** billing durumu değişebilir; dispatch öncesi yeniden görülmeli. Test sayısı gerçek pytest çıktısından alınır, tarihsel 22 bildirimi kabul kriterine sabitlenmez.
- **Dış onay:** belge uygulama yetkisi değildir. Owner planı ve uygulama kapsamını ayrıca onaylamalıdır; merge yapılmaz.

## Owner plan incelemesi

Plan hedefi, görev sınırları ve kabul ölçütleri owner incelemesine sunulmuştur. Açık onay gelene kadar workflow, manifest, test seçimi, kaynak kodu veya canonical VIP değişikliği yapılmayacaktır.
