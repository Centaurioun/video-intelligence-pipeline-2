# MEGA-17 sonrası owner kararları ve sonraki dar dilimler

Durum tarihi: 2026-11-05. Bu kayıt karar bekleyen noktaları toplar; herhangi bir kanonik kod değişikliğini, Gate'i veya üretim işlemini yetkilendirmez.

## Döngü 1–2: Şimdi geçerli duruş

- LAB P0 PR #1/#2 birleşik; güncel LAB main `1fd14c0b246c8da97e07129f6b84173d86f6a500` hosted Python 3.11/3.14 testlerinde yeşil. Yerel MEGA-17/LAB suite geçti.
- Kapsamlı Gate-0…3/FVS source-only taramasındaki tarihsel ref/fixture eksikleri düzeltilmedi; bu rapordaki sonuç `POST_MEGA17_CI_OR_CONTRACT_BLOCKED`.
- Kanonik `main` `bee314b92981b9ae7ea38d83fe2dbae120c474e4`; #258 `5a60cd8e0abc021767b05c87ca50202822c049d0`, #259 `e08382db65dcde703aadecc6ab329741f3c4b24c`; iki PR de draft/open. PR check listesinde zorunlu workflow'lar failure; step log yok, root cause belirsiz.
- Bu güncelleme mevcut LAB PR #4 draft'ında yalnızca izin verilen üç denetim belgesine eklenecek.
- PR #258/#259 GitHub file diff'lerinde silinen dosya yok; önceki deletion iddiası yanlış `current main..PR head` karşılaştırmasından geri çekildi. Bu nedenle product-document silinmesi için PR yazarından açıklama isteme aksiyonu kaldırıldı; ürün tasarımının uygulama izni olmadığı yönündeki ayrı karar değişmedi.

## Döngü 3: Owner kararı gereken konular

| Karar | Önerilen güvenli varsayılan | Owner'dan gereken yanıt |
|---|---|---|
| Kanonik #258 bounded admission adayının durumu | Şimdilik import yok; PR'nin failed checks/log erişimi ve sözleşme review'i çözülene kadar `CONFLICTS_WITH_OPEN_CANONICAL_PR` | PR sahibinden workflow log/root-cause ve API compatibility düzeltmesi; yalnız exact reviewed head üstünden yeniden test |
| Kanonik Gate-0/D-2 gerçek girdileri | NOT_OBSERVED; sentetik fixture yeterli değil | Gerçek corpus rights/retention/egress beyanı, iki atanmış reviewer, owner binding, valid query/reviewer inputs ve D-2 rulings ayrı kanaldan tamamlanmalı |
| D-3 media execution | `NOT_AUTHORIZED` | Kaynak discovery, byte read/hash, derivation, model run, no-egress, retention/cleanup gibi hakları açıkça ayıran ayrıca kapsamlandırılmış izin |
| Gate-3 A-7 / IT-6 | Kararlar açık; nominal FPS fallback veya tail-evidence uydurması yok | Stream identity mapping ve terminal-tail için owner-approved contract ruling / measured-source evidence gereklilikleri |
| H3-C05/H3-A04 execution order | Eski Atlas/launch pack'ten hazır olma veya grant türetme yok | Güncel main'de fresh contract/lease/readiness delta reconciliation; yeni slice scope ve owner approvals |
| PROPOSED `PRODUCT.md` UX | App/code build izni değil | Ürün tasarımını gerçek uygulama talimatına dönüştürmek istenirse ayrı onaylı spec/plan |

## Döngü 4–5: Sıralı ve dar sonraki dilimler

1. **P0 — LAB test-scope / artifact sync kararı (LAB owner):** decide whether LAB will carry the exact pinned canonical prompts/reports/measurement evidence and Git objects that its copied Gate tests require, or whether those tests belong in a separately sourced canonical test lane. Keep all 33 node IDs explicit; do not skip them and call the wide suite green. This documentation PR makes no implementation or fixture changes.
2. **P1 — object/fixture provenance (both repository owners):** preserve canonical source SHAs for d3d7… blob, F01 commit 345f… and the 25 path fixtures; choose a reproducible, license/authority-compliant read-only mirror mechanism for LAB. Recheck exact blob/commit identity before rerun.
3. **P2 — targeted re-verification (LAB owner):** after the above decision and an authorized source-only sync, rerun the exact 33 nodes; then rerun bounded Gate-0/2 and full synthetic regression on Python 3.11/3.14. Record skip/deselection counts separately.
4. **Canonical PR health (PR owners):** #258/#259 failed hosted contexts returned 404 `BlobNotFound`; obtain detailed logs or rerun exact current heads and diagnose before any import decision.
5. **Read-only S5-T1 contract review:** PR #258 public API, descriptor lifetime/close behavior, size ceilings, symlink/race refusal, immutable bytes, reason codes ve callers matrix'ini canonical D-2/D-3 contracts karşısında review et. Yalnız draft source'tan başka engine yazma.
6. **Fresh Gate-3 delta packet:** A-7 stream identity, source-native PTS/timebase/VFR ve IT-6 tail decisions'i canonical main/PR state üzerinden yeniden doğrula; H3-C05/H3-A04 launch pack drift'ini READY schedule sayma.
7. **Tasarım önerisi (ayrı owner approval):** yalnız owner onayı sonrasında, LAB synthetic source-readiness requirement'larını accepted canonical descriptor/admission receipt'e map eden ince adapter sözleşmesini yazılı tasarla. `SyntheticLabScenario` canonical scenario modeli olmaz; identity/revision/digest mapping ve provenance açık olmalı.
8. **Implementation/pytest PR (ayrı scope/approval):** design signoff ve PR #258 acceptance sonrası, dar adapter+contract tests. Yalnız synthetic fixtures; D-3 auth, real-media bytes, Gate promotion, PTS evidence, human decision, render/QC üretmez.

Bu adımlar ayrı kontrol noktalarıdır; 2–8 otomatik onay, #258 merge veya Gate ilerlemesi anlamına gelmez.

## Döngü 6: Açık engeller ve yeniden açma koşulları

- Yerel Python 3.11 interpreter yoktu (`NOT_OBSERVED`); hosted mevcut LAB branch'inde iki sürüm yeşil.
- Geniş tarihsel koşudaki 26 failed + 7 error artık node bazında sınıflandırıldı: 25 node canonical VIP tree'de bulunan fakat LAB `main@1fd14c0b`'de olmayan .orchestration prompt/measurement veya docs/agent-runs evidence artifact'ine; 8 node canonical'da çözülen ancak LAB object store'da bulunmayan pinned Git object'ine takıldı. Tam 33 node, exact pytest ID + first traceback + owning repo karşılaştırması için regression report envanterine bakılmalı. `IMPORT_OR_ENV`, `REPRODUCIBLE_PRODUCT_DEFECT`, `UNKNOWN` yok. Bu yine de LAB historical regression'ı blokluyor; başarısızlığı test skip'iyle PASS saymak doğru değil.
- Kanonik PR check failures log'suz olduğundan S5-T1 kod kalitesi veya PR başarısızlığının nedeni hakkında olumlu/olumsuz source verdict verilemez.
- Gerçek Gate-0, D-2 Owner inputları, gerçek iki reviewer, local model benchmark, PTS/frame evidence, A-7, IT-6, gerçek editorial/QC, export authorization ve production suitability `NOT_OBSERVED`/ayrı yetki gerektirir.

Bu audit'in yeniden açılma koşulu: güncel kanonik refs ve PR check logları erişilebilir olduğunda compatibility matrix'i yalnız yeni kanıtla güncellemek. Owner açıkça ayrıca scope vermedikçe source, test, workflow, canonical checkout, model veya medya davranışını değiştirmemek.
