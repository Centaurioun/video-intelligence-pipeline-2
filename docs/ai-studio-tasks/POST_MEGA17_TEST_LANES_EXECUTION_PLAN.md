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
- 2026-11-05 account billing ekranındaki Usage blocked, owner açıklamasına göre included Actions allowance'ın bitmesi değil ücretli aşım harcamasının engellenmesidir. Owner şu anda yaklaşık 3.000 dakika allowance kaldığını bildiriyor; bu miktar UI'da bağımsız okunmadı. Gelecek her hosted run öncesi ilgili hesabın kalan included minutes ve repo/runner kapsamı yenilenerek kontrol edilir; yeterli dakika varsa mevcut Usage blocked göstergesi tek başına durdurma nedeni değildir. Plan dışı ücretli aşım kullanılmaz, billing ayarı değiştirilmez.
- PR #258'in yeni tests/vip_fvs/unit/test_bounded_admission.py testi canonical repo ve gerçek PR head üzerinde Python 3.11/3.14'te sıfır skip ile yürütülmeden hosted-test doğrulaması sayılmaz.
- Workflow'lar mevcut pull_request/push politikasını korur; tarihsel ref erişimi açık doğrulanır. fetch-depth: 0 tek başına preserved ref'in mevcut olduğunu kanıtlamaz.
- Gerçek media, model indirme/çalıştırma, provider, render/export, Gate promotion veya merge yapılmaz.
- Her receipt repo, commit/tree SHA, PR base/head/merge SHA (varsa), workflow path+blob SHA, run/job ID, Python ve pytest sürümü, lockfile SHA-256, manifest SHA-256, node ID'leri ve pass/fail/error/skip/deselected sayımlarını taşır.

## Review Focus

- **Allowance'ı tüketilmiş varsayma veya overage'a girme:** hosted execution öncesi hedef hesap/repo için kalan included Actions minutes yenilenip doğrulanır; Usage blocked göstergesi tek başına allowance'ın tükendiğini göstermez. Yeterli included minutes yoksa ve ücretli aşım gerekecekse run durdurulur.
- **33 node'un manifestten düşmesi veya yanlış owner'a atanması:** doğrulayıcı tam node-ID kümesinin design envanteriyle birebir eşitliğini ve canonical-history owner'ını kontrol eder.
- **Tarihsel Git ref/object runner'da yokken testleri çalışmış varsayma:** preflight pinned commit/tree/blob ve archive ref'i testten önce doğrular; eksikse lane BLOCKED ve test UNRESOLVED kalır.
- **Collection sırasında skip/deselect veya Python matrisi eksikliği:** JUnit ve pytest collection çıktısı iki interpreter için beklenen node'ların toplandığını ve skip/deselected olmadığını doğrular.
- **Bir lane'in diğerini PASS göstermesi:** her workflow ayrı status context ve artifact üretir; aggregator/ortak yeşil badge eklenmez.

---

## Önkoşullar ve bağımlılık sırası

1. **Allowance/billing gate (her hosted run öncesi tazele):** UI Usage blocked, owner açıklamasına göre harcama üst sınırındaki ücretli aşımı durdurur; included allowance'ın tükendiğini göstermez. Owner yaklaşık 3.000 Actions dakikası kaldığını bildiriyor; bu sayı owner-reported, Codex tarafından ölçülmedi. Gelecek her hosted execution öncesi ilgili hesapta remaining included minutes ve repo/runner kapsamını yenile. Yeterli included allowance varsa bu gösterge tek başına engel değildir; aşım ücreti gerekecekse run başlatma. Billing ayarlarını değiştirme.
2. **Canonical PR zemini:** PR #258 ve #259 eski 592952da… base'indedir; main@bee314b92981b9ae7ea38d83fe2dbae120c474e4 iki doküman ileridedir. Owner, #258 base refresh/rebase kararını ayrıca verir. GitHub contents API test path'ini canonical main üzerinde 404, PR #258 head `5a60cd8e0abc021767b05c87ca50202822c049d0` üzerinde blob `5ecbbd33d9d136984424cdcb787669b83be4db84` olarak doğruladı. Workflow adımı #258 source/test ile aynı PR candidate/head'e eklenir; workflow-only main PR açılmaz.
3. **Uygulama onayı:** aşağıdaki plan bağımsız lane sınırlarını tanımlar, ancak workflow/manifest değişikliğine başlamadan owner'ın planı ve uygulama kapsamını onaylaması gerekir.
4. **DAG:** Task 1 (independent oracle + manifest exact equality) → Task 2 (canonical history lane) → Task 5 (receipt reconciliation). Task 3 (PR #258 source/test/workflow same-head candidate) mevcut PR #258 içinde yürütülür; workflow-only change main'e veya ayrı PR'a önceden indirilmez. Task 4 (LAB receipt) bağımsızdır. Hosted işler Task 2–4 sonrasında allowance refresh ve exact candidate head'e bağlıdır.

## Dosya haritası

| Dosya | Sorumluluk |
|---|---|
| docs/testing/POST_MEGA17_CANONICAL_HISTORY_TEST_MANIFEST.json (yeni, canonical VIP) | 33 sabit node ID, owner, test-source blob, gereksinim kümeleri, pinned path/ref/object ve execution lane metadata. |
| tests/contracts/canonical_history_expected_nodeids.json (yeni, canonical VIP) | 33 exact node ID için independent oracle listesi; canonicalized-set SHA-256 `8248fbf704f0ebba5e877a26106ab9e8b77a9b7a92fd5695a7f4e2820002b016`. |
| scripts/validate_canonical_history_manifest.py (yeni, canonical VIP) | Şema/benzersizlik, oracle ile exact set eşitliği ve object/path preflight doğrulaması; pytest seçimi üretimi. |
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
- Create: tests/contracts/canonical_history_expected_nodeids.json (canonical VIP)
- Create: scripts/validate_canonical_history_manifest.py (canonical VIP)
- Test: tests/scripts/test_validate_canonical_history_manifest.py (canonical VIP)
- Oracle provenance: design source commit `f69334705919f10b10c4b78ecc235c6f160d3b6b`, source blob `eb5972bd1fa8098a82b8ca78720b47d51d9ab907`; canonical CI reads the committed canonical oracle only, never a LAB path or network resource.

**Interfaces:**
- Manifest alanları: schema_version, lane_id=canonical-history, owner_repository=Centaurioun/video-intelligence-pipeline, canonical_base_sha, python_versions=[3.11,3.14], expected_node_count=33, nodes[].
- Independent oracle file holds the exact 33 sorted node IDs in design §5.3. SHA-256 of compact sorted JSON plus LF is `8248fbf704f0ebba5e877a26106ab9e8b77a9b7a92fd5695a7f4e2820002b016`; the test pins this literal independently from manifest contents.
- Her node kaydı: node_id, owner_repository, test_path, test_source_blob, required_artifacts[], required_git_objects[], required_refs[], prior_status=UNRESOLVED.
- validate_manifest(manifest_path, repo_root) tam doğrulama yapar; CLI geçerli node ID listesini JSON olarak yazar: python scripts/validate_canonical_history_manifest.py --manifest docs/testing/POST_MEGA17_CANONICAL_HISTORY_TEST_MANIFEST.json --repo-root . --emit-nodeids.

- [ ] **Adım 1: Kırmızı testleri yaz.** Oracle digest ve manifest/oracle exact-set equality testlerini ekle. Negative cases: 32/34 IDs, bir node'u çıkarıp yabancı node ile değiştirme, duplicate, permuted order, yanlış digest/owner/blob/ref, eksik archive ref, PASS/RESOLVED state ve unknown field. Order-only permutation canonicalization'dan geçmeli; substitution kesin FAIL olmalı.
- [ ] **Adım 2: Test-first doğrula.** python -m pytest -q tests/scripts/test_validate_canonical_history_manifest.py; başlangıçta yeni arayüz nedeniyle FAIL beklenir.
- [ ] **Adım 3: Oracle ve manifesti bağımsız kaydet.** Önce design §5.3'teki 33 ID'yi canonical oracle test fixture'ına kopyala ve checksum literalini testte sabitle; ardından manifesti ayrı oluştur. Runtime canonical oracle/manifesti karşılaştırır, LAB dosyasına veya ağa başvurmaz.
- [ ] **Adım 4: En küçük doğrulayıcıyı uygula.** ID kümesi tam eşitliği, duplicate reddi, repo/path root sınırı, blob/tree/commit türü ve SHA doğrulaması, ref resolution ve tüm geçmiş statülerinin UNRESOLVED oluşunu denetle. Preflight hata verirse nonzero çık; test seçimi üretme.
- [ ] **Adım 5: Test ve preflight doğrula.** Aynı pytest komutu ve manifest CLI. Exact set oracle == manifest; checksum literal `8248fbf704f0ebba5e877a26106ab9e8b77a9b7a92fd5695a7f4e2820002b016`; 33 benzersiz ID ve tüm pinned dependencies bulunmalı. Substitution testi FAIL, order permutation testi PASS olmalı. Eksik dependency BLOCKED; fixture kopyalama.
- [ ] **Adım 6: Yalnız manifest/validator/test değişikliklerini commit et.** test: define canonical history lane manifest.

**Kabul:** Tam 33 ID ve birebir eşitlik üç tarafta: bağımsız oracle, manifest ve tasarım envanteri; oracle checksum sabittir; canonical owner ve UNRESOLVED statüsü korunur; eksik obje/ref/artifact fail-closed olur; LAB testlerinden hiçbiri seçilmez.

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

## Task 3: PR #258 source/test/workflow değişikliklerini aynı candidate'de doğrulama

**Files (same canonical PR #258 candidate/head):**
- Existing PR #258 files: src/vip_fvs/_bounded_admission_fs.py, src/vip_fvs/bounded_admission.py, tests/vip_fvs/unit/test_bounded_admission.py.
- Modify in that same PR branch: .github/workflows/python-synthetic-smoke.yml.
- Add/modify a source-owned canonical workflow contract test; verify its exact existing path before implementation.

**Safe integration sequence and dependency:**

1. Owner first authorizes refreshing the stale PR #258 base onto the then-current canonical main. Re-check the PR base/head and all three file identities; do not change its base implicitly.
2. Add the bounded-admission pytest step to the same PR #258 branch containing both source modules and the new test. The pull_request candidate merge ref must contain source, test, and workflow changes at one exact candidate SHA; receipt binds base/head/merge SHA, test blob, workflow SHA and run.
3. Do not create/land a workflow-only PR, cherry-pick the workflow into main first, or target the absent test unconditionally from canonical main. The changes co-land when the owner merges the existing #258 PR as one reviewed unit; unrelated PRs against main remain unaffected beforehand.
4. Candidate missing the test path fails explicitly before pytest. No if-exists, skip, xfail, continue-on-error, or green fallback is allowed.

**Interfaces:**
- Exact target: tests/vip_fvs/unit/test_bounded_admission.py. Reviewed PR #258 head blob: 5ecbbd33d9d136984424cdcb787669b83be4db84 (re-verify at implementation).
- Python 3.11/3.14 matrix; bounded-admission-junit.xml plus bounded-admission-receipt.json.

- [ ] **Adım 1: Same-candidate contract test first.** Add a failing contract test asserting source module, target test, focused workflow step, and both Python jobs coexist in candidate tree.
- [ ] **Adım 2: Prove red on pre-change canonical main.** Run the verified contract node against main and confirm failure due to absent test/step. Never run the proposed PR workflow on main without the test.
- [ ] **Adım 3: Update the existing PR #258 candidate together.** After owner-authorized base refresh, amend the existing #258 branch with both source modules, test file, and workflow selector. Run: python -m pytest -q --junitxml=<runner-temp>/bounded-admission-junit.xml tests/vip_fvs/unit/test_bounded_admission.py. Add a fail-closed existence/selection assertion; no skip logic.
- [ ] **Adım 4: Verify the exact candidate locally.** Check all four paths and test blob at candidate commit; run the workflow contract test and PYTHONPATH=src:experiments:scripts python -m pytest -q tests/vip_fvs/unit/test_bounded_admission.py on Python 3.11 and 3.14. Record real collection/pass/fail/error/skip counts; do not hardcode historical 22.
- [ ] **Adım 5: Hosted execution gate.** Immediately refresh relevant account/repo remaining included minutes and billing UI. If sufficient allowance is available, the owner-authorized normal PR #258 event may run without an overage charge; Usage blocked alone does not mean the allowance is exhausted. If included allowance is insufficient and an overage would be billed, stop. Verify PR base/head/merge SHA and test/workflow blobs.
- [ ] **Adım 6: Atomic integration boundary.** Existing PR #258 is the sole carrier of source, test, and selector through review. No workflow-only merge. A stale-base conflict returns to PR review; never split changes or weaken selection.

**Kabul:** Exact #258 candidate has both implementation modules, test file, and focused workflow step. Python 3.11/3.14 execute the exact test with zero skip/deselection and separate receipts; missing target fails the job. Unrelated PRs against main are unaffected before atomic #258 adoption. No media/model/provider/render calls.

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
- [ ] **Adım 3: Receipt'i exact ref'e bağla.** Repo, base/head/merge SHA, tree SHA, workflow SHA, run/job URL/ID, Python/pytest, lock hash, manifest hash, node list/counts, artifact digest ve ilgili hesabın included allowance gözlem zamanını karşılaştır.
- [ ] **Adım 4: Hosted kabul kapısı.** Run'dan hemen önce ilgili hesap/repo için kalan included Actions minutes değerini tazele ve receipt'e allowance miktarı + zaman damgası olarak kaydet. Usage blocked, owner açıklamasına göre ücretli overage guard'dır; yeterli included minutes varsa bu tek başına run'ı durdurmaz. Overage gerekirse dur. PR #258 source/test/workflow aynı candidate head'inde olmalıdır; workflow'u default branch'e önceden indirme.
- [ ] **Adım 5: Gözlenen sonuçları raporla.** Her Python job ve node için PASS/FAIL/ERROR/SKIP/NOT RUN yaz. Koşmayan canonical node'lar UNRESOLVED kalır. Yeni kanıt olmadan hata kök nedeni genellenmez.
- [ ] **Adım 6: Yalnız gözlenen kanıtı belgeleyen reconciliation commit'i üret.** Kaynak ve test beklentisi değiştirme.

**Kabul:** İki sahiplik lane'i ve üç ayrı evidence sonucu görünürdür; canonical 33 sonuç tam veya node-bazlı unresolved/blocker olarak raporlanır; LAB PASS canonical statüsüne geçmez; #258 exact PR head üzerinde iki Python/0 skip ile kanıtlanır.

---

## Rollback ve güvenli sınırlar

- CI değişikliği geri alınacaksa owner-onaylı PR'de yalnız ilgili workflow/validator commit'i revert edilir; test veya beklenti değişiklikleri rollback bahanesi olmaz.
- Manifest pinleri ve historical tests değiştirilemez. Yanlış pin varsa ayrı kanıta dayalı review gerekir; tarihi testleri yeşile döndürmek için pin gevşetilmez.
- Included allowance yetersiz ve ücretli overage gerekecekse hosted run başlatılmaz. Başlamış workflow başarısızsa root cause incelenmeden rerun yapılmaz.
- PR #258/#259 base yenilemesi, canonical main merge'i ve billing ayarları LAB planının uygulama/rollback kapsamı dışındadır.
- Yanlış ownership, ref veya eksik manifest lane'i BLOCKED yapar; fixture mirror veya skip çözüm değildir.

## Altı döngülü iteratif iyileştirme

1. **Cycle 1 — Kanıt ve sınır:** güncel refs, PR listeleri, workflow seçimleri, overage budget ile included allowance ayrımı ve 33 node sahipliği tasarım belgesinde sabitlendi.
2. **Cycle 2 — Alternatifler:** iki lane, artifact mirror, seçimden çıkarma ve birleşik suite karşılaştırıldı; owner iki lane'i onayladı, mirror reddedildi.
3. **Cycle 3 — Bağımlılık haritası:** run-öncesi remaining allowance refresh, stale canonical PR base, preserved refs ve PR #258 source/test/workflow same-head bağımlılığı sıralamaya bağlandı.
4. **Cycle 4 — Task/arayüz:** manifest → canonical lane → receipt zinciri; bounded smoke ve LAB receipt işleri ayrı dosya sınırlarıyla tanımlandı.
5. **Cycle 5 — Negatif kontroller:** eksik refs, node farkı, skip/deselect, stale head, billing block ve lane karışması fail-closed kabul koşullarına çevrildi.
6. **Cycle 6 — Özdenetim:** spec coverage, 33 node sayısı, dosyalar, komutlar, merge/billing yetkisi ve bağımsız sonuçlar yeniden kontrol edildi. Owner planı uygulama öncesi incelemelidir.

## Plan özdenetimi

- **Kapsam:** LAB lane, canonical-history lane, 33 node manifesti ve bağımsız oracle, canonical lane içindeki #258 focused test slice'ı, run-öncesi allowance refresh, stale PR base, source provenance, ayrı receipts ve no-merge sınırları görevlere bağlandı.
- **Test-first:** her davranış/CI contract değişiminden önce negatif test ve komut tanımlandı; hosted kabul yerel doğrulamadan ayrıldı.
- **Kimlikler:** canonical gözlem main SHA `bee314b92981b9ae7ea38d83fe2dbae120c474e4`; LAB design base `1fd14c0b246c8da97e07129f6b84173d86f6a500`; PR #258 kaydedilmiş head `5a60cd8e0abc021767b05c87ca50202822c049d0`, test blob `5ecbbd33d9d136984424cdcb787669b83be4db84`; oracle canonical JSON SHA-256 `8248fbf704f0ebba5e877a26106ab9e8b77a9b7a92fd5695a7f4e2820002b016`. Uygulamada tekrar fetch etmeden SHA'lar güncel sayılmaz.
- **Belirsizlik:** Usage blocked overage harcamasını durduruyor; owner yaklaşık 3.000 included Actions dakikası kaldığını bildiriyor. Bu sayı owner-reported ve her execution öncesi ilgili hesap/repo'da yeniden doğrulanmalı; hiçbir ücretli overage yapılmaz. Test sayısı gerçek pytest çıktısından alınır, tarihsel 22 bildirimi sabitlenmez.
- **Dış onay:** belge uygulama yetkisi değildir. Owner planı ve uygulama kapsamını ayrıca onaylamalıdır; merge yapılmaz.

## Owner plan incelemesi

Plan hedefi, görev sınırları ve kabul ölçütleri owner incelemesine sunulmuştur. Açık onay gelene kadar workflow, manifest, test seçimi, kaynak kodu veya canonical VIP değişikliği yapılmayacaktır.
