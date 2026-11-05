# VIDEO INTELLIGENCE PIPELINE — Yeni ChatGPT Oturumu İçin Kapsamlı Geçiş / CORE CLI Ürün Kapanışı

**Tarih:** 2026-11-06 (Europe/Istanbul)  
**Belge sürümü:** VIP-CHATGPT-CORE-CLOSURE-HANDOFF-v1.0.0  
**Tür:** Tarihli ve GitHub üzerinden doğrulanmış devam belgesi; yürütme izni veya ürün sertifikası değil.  
**Bu belgenin deposu:** https://github.com/Centaurioun/video-intelligence-pipeline-2 (LAB)  
**Kalıcı ürün deposu:** https://github.com/Centaurioun/video-intelligence-pipeline (canonical)  
**GitHub kontrol anındaki canonical main:** 3bfcc2ba221b36df6773e630b44479ec961d630a  
**GitHub kontrol anındaki LAB main:** b96c80758ad774f9e38b65e2667e7792f177e120  
**Ayrım:** LAB kaynak uygulama adayı 44d4e0a6c80c924b837303a34ff373fc0d2a14cc; LAB b96c807... bundan sonra gelen **yalnız dokümantasyon** commit'idir. Bu yeni handoff da LAB main'i bir kez daha yalnızca belge yazarak ilerletecektir.

> **BU BELGEYİ OKUYAN YENİ CHATGPT İÇİN:** Kullanıcı aynı projeye, aynı hedefle devam etmek istiyor. Çalışmanın amacı tüm araştırma Gate'lerini, UI'ı, insan değerlendirmeli benchmark'ı veya render'ı şimdi bitirmek değildir. Kullanıcının tanımladığı yakın ürün bitişi, **izinli tek bir yerel videoyu komut satırından gerçek yerel görsel semantik analizden geçirip kaynak kimliği, zaman konumları, güvenilir PTS/timebase ve açık sınırlamalarla yapılandırılmış JSON üretebilen çalışan CORE CLI'nin tamamlanmasıdır**. Önce LAB/Google AI Studio'da gerekli kaynak kod tamamlanacak, Codex yerelde gerçek Python testleriyle onaracak, yalnız gerekli kod kontrollü biçimde canonical depoya aktarılacak ve son doğrulama canonical ortamda yapılacaktır. Şu anda **CORE-01 kodu LAB main'dedir fakat Codex'in bağımsız yerel test/onarım sonucu henüz alınmamıştır.** Başka işi yapılmış kabul etme, kullanıcıyı önceki konuşmayı yeniden anlatmak zorunda bırakma.

---

## 0. İlk cevap verilmeden önce: kesin yeniden başlatma protokolü

1. **Bu belgeyi baştan sona oku.** Tarihli SHA'ları gelecekte canlı durum sanma.
2. GitHub üzerinden **iki** deponun güncel main SHA/tree/son commit'lerini, ilgili değişiklikleri, gerekli PR/CI durumlarını yeniden doğrula. LAB ana faaliyet alanı; canonical ürün/kontrat otoritesi.
3. Canonical main üzerinde sırayla oku: AGENTS.md, docs/INDEX.md, docs/project/00_PROJECT_CHARTER.md, docs/project/01_CURRENT_STATE_AND_HANDOFF.md, docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md, docs/project/STATE_MAINTENANCE_PROTOCOL.md. Orijinal 01_CURRENT_STATE... tarihsel üst kayıtları içerebilir; mevcut SHA/kanıt bunlardan üstündür.
4. LAB üzerinde **mevcut kesin görev dosyalarını** oku:
   - docs/ai-studio-tasks/MEGA_CORE_01_TEMPORAL_STREAM_AND_CLI_CORRECTNESS.md
   - docs/ai-studio-tasks/MEGA_CORE_01_CODEX_VERIFICATION_AND_REPAIR.md
5. Kullanıcı sıradaki Codex raporunu verirse ilk iş, raporun söylediği sonuçları **gerçek LAB GitHub commit, changed-file diff ve CI** ile karşılaştır. Gerçek modelin veya gerçek videonun çalıştığı iddia ediliyorsa ayrıca o çalışmanın kaynağı/izinleri/artifact kanıtını ara.
6. CORE-01 **genuinely verified** olmadan CORE-02 kaynak uygulamasını başlatma veya eski AI Studio kodunu tekrar yükletme. Codex çalışması sürüyorsa gereksiz yeni aynı kapsamlı iş çıkarma.
7. Her adımda **SOURCE_INSPECTED / SYNTHETIC_TESTED / AUTHENTICALLY_MEASURED / NOT_OBSERVED / BLOCKED / PENDING** ayrımını koru; bunlar birbirinin yerine kullanılamaz. Canonical delil sınıflarını değiştirme.
8. Yeni cevapları **Türkçe**, kısa ama teknik bakımdan kesin ver; kullanıcı istediğinde gönderilebilir kısa prompt ve repo içindeki ayrıntılı görev belgesiyle çalış. Gerçekleşmemiş yetki, test, push veya merge iddia etme.

**Şu an beklenen en olası kullanıcı mesajı:** Yerel Codex'in MEGA-CORE-01 verification/repair raporu. O rapor geldiğinde bu belgenin 4–7. bölümlerini ve canlı GitHub durumunu esas alıp ilerle.

---

## 1. Kullanıcının özel olarak belirlediği ürün bitişi — en önemli karar

Kullanıcı birçok defa şu ayrımı yaptı:

- Yazılım geliştirmesi **bitmiş** sayılsın istiyor: bir video verelim, program onu analiz etsin, videonun hangi anında neye benzer görsel içerik bulunduğunu kaynağa bağlanmış zaman konumları ve güvenilir bir çıktı dosyasıyla anlatsın/göstersin.
- Başlangıçta beş dakikalık bir video üzerinde kare çıkarma ve karelerin içeriklerini inceleyen basit bir gösterim yaptıklarını kullanıcı bildirdi. Bu **tarihsel kullanıcı anlatımıdır**; mevcut exact CORE CLI branch'inde yeniden gözlenmiş authentic full-path test olarak kullanılamaz.
- Sistem komut satırında çalışabilir. İlk teslim için React/Node dashboard, masaüstü arayüz veya tarayıcı UI **gerekmiyor**.
- Üç SigLIP profilinin benchmark'ı, gerçek insan değerlendirmeli Gate-0/1 ölçümleri, optimizasyon, throughput, büyük arşiv ölçeği, Qdrant/LanceDB geçişi, prodüksiyon editing/render/export ve dış sağlayıcı entegrasyonları **sonraki fazlar**dır.
- Dört Gate'in tamamının operasyonel ve bilimsel olarak onaylanması, yakın CORE ürün tesliminin eşanlamlısı değildir.
- Kullanıcı uzun (45–60 dakikalık) Google AI Studio görevlerinden hızlı kod çıktısı almak istiyor; her mikro düzeltme için yeni sohbet ve sekiz tur PR döngüsünden hoşlanmıyor. Gereksiz tekrar, yeni mimari inşası ve test edilemeyen başarı iddialarından kaçın.

**V1 ürün semantiği — henüz kesinleşmemiş kritik nüans:** Mevcut yerel SigLIP hattı kullanıcı tarafından verilen bir metin sorgusuyla **semantic retrieval** yapabilir; hiçbir sorgu olmadan videoyu baştan sona özgün doğal dille otomatik sahne-sahne caption'layan bir model değildir. Önceki çift-repo denetim, küçük çalışır ürün için QUERY_DRIVEN_SEMANTIC_REPORT_V1'i önermişti. Bunu kullanıcı tarafından bağımsız onaylanmış “otomatik caption yeterlidir” kararı gibi sunma. CORE-02 ürün sözleşmesini dondururken sorguya dayalı aramanın kullanıcının “hangi noktada ne var” beklentisini karşılayıp karşılamadığını açıkça belirt. Ayrı üretken captioning gerekecekse yeni capability ve gerçek runtime seçimi gerektirir; asla hayali caption üretme.

**CORE_CLI_PRODUCT_COMPLETE kriterleri:** Yetkilendirilmiş tek yerel video; gerçek/provenance-bound kaynak snapshot; doğru video stream ve PTS/timebase; yerel gerçek inference ile semantik retrieval; yaklaşık MATCHED aday konumları ile source-native MEASURED teknik ölçümün ayrılması; versioned machine-readable analiz JSON; tutarlı status/error ve exit code; immutable kaynak; temiz canonical ortamda yeniden çalıştırılmış testler ve gerçek bir end-to-end acceptance receipt. Son karar ancak bu gereksinimlerin gerçekten gözlemlenmiş kanıtıyla verilebilir.

---

## 2. İki depo niçin var ve nasıl kapatılacak?

### A. Canonical orijinal ürün — korunmuş uzun vadeli hedef

https://github.com/Centaurioun/video-intelligence-pipeline  
**Doğrulanmış main:** 3bfcc2ba221b36df6773e630b44479ec961d630a

Kaynak/PTS/provenance/Gate/yetki kontratlarının, editoryal ve release sınırlarının, asıl geçmişin ve uzun vadeli tek ürünün merkezidir. Çok fazla dosya, tarihsel dokümantasyon, reference-pack ve özel kaynak barındırdığı için tamamını Google AI Studio'ya yüklemek pratik olmamıştı. Google AI Studio'nun doğrudan orijinal depoda çalışması tercih edilmedi.

### B. LAB / Google AI Studio çalışma deposu — geçici hızlandırıcı

https://github.com/Centaurioun/video-intelligence-pipeline-2  
**Doğrulanmış main:** b96c80758ad774f9e38b65e2667e7792f177e120  
**CORE-01 kod adayı:** 44d4e0a6c80c924b837303a34ff373fc0d2a14cc

Başta Google AI Studio'nun yaklaşık ilk 100 dosyalık import sınırını aşmak ve büyük görevleri rahatlıkla hazırlatmak için kanonikten seçilmiş dosyalarla kuruldu; daha sonra üretilen MEGA sentetik kodlar burada geliştirildi. **LAB'daki her dosya canonical'a taşınmayacaktır.** Üretim için gerekli olup canonical'da eksik/daha eski kalan kaynak ve testler blob/diff tabanlı seçici aktarılacak; fake harness ve gereksiz laboratuvar modülleri LAB'da kalacak.

**Çalışma tarzı, kullanıcının açık tercihi:**
- Ben/ChatGPT ayrıntılı, sürümlü işi LAB docs/ai-studio-tasks/ içine yazarız; kullanıcıya yalnız bu dosyayı çalıştıran kısa AI Studio promptu verilir.
- Kullanıcı AI Studio'yu yeni bir instance'ta, LAB main snapshot'unu içe alarak çalıştırır. AI Studio Python/pytest/model çalıştırmayabilir; kod ve testleri yazar.
- AI Studio Git metadata'sı bulunmayan ZIP snapshot ortamında “git push BLOCKED/NOT_OBSERVED” diyebilir, **ancak UI/GitHub senkronizasyonu gerçekten remote main'i ileri taşıyabilir**. Karar AI Studio metnine göre değil, GitHub refs/commit/diff üzerinden verilir.
- LAB'da normal kullanım: **doğrudan LAB main'e push/sync**, yeni repo veya PR açma zorunluluğu yok. Ancak bu akış canonical main'e uygulama izni değildir.
- Codex yerel Git worktree ile LAB main'i çeker, Python 3.11/3.14 ve gerçek pytest/FFmpeg sentetik testlerini çalıştırır; saptanan kusuru küçük TDD düzeltmesiyle giderip gerekli kanıtı toplar. Kirli ana çalışma ağacına dokunmaz.
- Google AI Studio full-tree sync geçmişte src/gate0/media/ altındaki altı kanonik dosyayı silmişti. Her doğrudan main senkronizasyonundan sonra **path diff ve bu altı dependency dosyası denetlenmeli; kayıp dosyalar ancak doğrulanmış sağlam Git blob'larından seçici restore edilmelidir.** Asla sessiz broad overwrite veya imal edilmiş stub kullanma.
- CORE tamamlanırken gerekli kodun canonical'a **tek tek gerekçeli / seçici** taşınması gerekir. Canonical'da gerçek ürün ve local verification başarıyla görülünce bundan sonra yalnız canonical repo'ya odaklanılacak.
- İki depo birleştirilip LAB geçmişi canonical main'e toplu merge edilmeyecek.

**Git güvenliği:** force push, git clean, hard reset, rebase ile history rewrite, dirty checkout'u temizleme, worktree/branch silme ve kanıt objesi budama kullanıcı tarafından ayrıca açıkça yetkilendirilmedikçe yapılmaz. Yalnız dürüst, forward-only ve bağımsız doğrulanabilir teslim.

---

## 3. Doğrulanmış kilometre taşları — eski açık PR döngüsüne dönmeyin

GitHub'da 2026-11-06 tarihinde yeniden denetlenenler:

| Depo / PR | Durum | Merge commit |
|---|---|---|
| Canonical #264 — historical 33-node manifest / Task 1 | MERGED | 269cbaacfb8e5dfb1689025372c148c6b615aed8 |
| Canonical #265 — historical regression lane / Task 2 | MERGED | c9d0daffbe8c599a8c65891e69d108c3169f8eb9 |
| Canonical #258 — S5-T1 bounded synthetic descriptor admission | MERGED | 3bfcc2ba221b36df6773e630b44479ec961d630a |
| Canonical #259 — eski ChatGPT handoff PR | CLOSED WITHOUT MERGE | Yok |
| LAB #6 — 37-node MEGA-17 synthetic receipt / Task 4 | MERGED | e111cc2c006fb57671cb5120259a9bed9c175747 |
| LAB #7 — Task 5 receipt reconciliation | MERGED | 324f6814b9b97e5505e592e9c5d41b3a4c49b532 |

Canonical #258 yıllarca süren bağımsız quality-loop sonucu olarak değil, 2026-11-05'te **Owner'ın yalnız bu PR'a verdiği açık CodeScene istisnasıyla** birleştirildi. Merge mesajı CodeScene 9.39/10.00 (result_validation.py, complexity), buna rağmen bounded-admission 22/22 iki Python sürümünde ve ilgili synthetic Gate-0/2 testleri/GitGuardian PASS olduğunu açıkça belirtiyor. **Bu istisna genelleştirilemez**, yeni kodların kalite kapıları otomatik geçilmiş sayılmaz. #258'i açık/Draft diye tanımlayan eski MEGA belgeleri artık tarihsel ve stale.

MEGA-03–07, 08–14, 15–16, MEGA-17 ve Workstreams A–E LAB'da büyük miktarda **sentetik ve offline hazırlık yazılımı** üretti. MEGA-08–14 için tarihsel hosted 350/350 test/yorumlayıcı milestone'u; MEGA-17 için 37-node synthetic lane ve altı evidence lane'in kendi immutable receipt'leri vardır. Bu hedefli kanıtlar **otantik model çalıştırması, gerçek video, insan kararı, Gate yükseltmesi veya production export** değildir.

Task 5 tarihi raporunda üç ayrı kanıt dilimi C1 canonical history, C2 PR258 bounded admission ve L1 LAB synthetic olarak tutuldu; genel cross-lane verdict **PARTIAL** olarak korunmuştu. Başarılı scoped receipt'ler yüzünden tarihi raporu genel PASS'a çevirme.

Canonical Issues:
- #260 — structured observability ve işlem durumları: OPEN, BACKLOG.
- #261 — dashboard / inceleme arayüzü: OPEN, DEFERRED.
- #262 — opsiyonel Gemini / sağlayıcı credential boundary: OPEN, DEFERRED.
Bu issue'ların **GitHub Projects V2 #2 kartlarına gerçekten eklenip eklenmediği** bu oturumda bağımsız doğrulanmadı; UI ve provider şu andaki CORE P0 kapsamı değildir.

---

## 4. MEGA-CORE-01 — mevcut en yakın uygulama durumu (ŞİMDİKİ TAM DEVAM NOKTASI)

**Görevin tam adı:** Source PTS, Video Stream Identity, Semantic Timing and CLI Exit Correctness.  
**Ayrıntılı AI Studio teknik spesifikasyonu:**  
https://github.com/Centaurioun/video-intelligence-pipeline-2/blob/main/docs/ai-studio-tasks/MEGA_CORE_01_TEMPORAL_STREAM_AND_CLI_CORRECTNESS.md

**Kod GitHub'da gerçekten mevcut.** 2026-11-06 kontrolünde LAB main'de gördüğümüz CORE-01 kaynak/test teslim commit'i: **44d4e0a6c80c924b837303a34ff373fc0d2a14cc**, daha sonraki **b96c807... ise yalnız Codex doğrulama Markdown'u ekledi.**

Sekiz değişmiş yol:
1. experiments/persistent_local_index/media.py
2. experiments/persistent_local_index/tests/test_media_pts.py
3. experiments/persistent_local_index/tests/test_indexer.py
4. src/vip_fvs/real_source_service.py
5. src/vip_fvs/cli.py
6. tests/vip_fvs/unit/test_real_source_service.py
7. tests/vip_fvs/integration/test_cli_acceptance.py
8. tests/vip_fvs/integration/test_product_index_query.py

AI Studio'nun bildirdiği ve GitHub diff/blob ile teslimi teyit edilen dört düzeltme:

| Repair | Sorun | Yazılmış düzeltme; henüz exact yerel davranış sertifikası değil |
|---|---|---|
| A — Native PTS/timebase | pts_time × denominator hesabı, payı 1 olmayan timebase'te yanlış | Rasyonel numerator/denominator, showinfo filter timebase kontrolü, yanlış/eksik veri retleri |
| B — Stream identity | İlk video akışı mutlak stream 0 varsayılmış | ffprobe gerçek index çıkarma, açık selection, ffmpeg -map 0:absolute_index ve persist edilen kimlik |
| C — Semantic candidate timing | timestamp_human string olunca tüm hit'ler 0–1 saniyeye çöküyordu | Kaynak/hit stream, PTS ve timebase doğrulamasıyla yaklaşık konum; gerçek pencere yoksa uydurma +1 saniye yok |
| D — CLI failure | index-local hata sayısı olsa bile exit 0 | failed count ve JSON shape doğrulaması; başarısızlıkta exit nonzero, tek JSON rapor |

**Kritik kanıt ayrımı:** Google AI Studio pytest çalıştırmadı; RED/GREEN testlerini yazdı ve AST/syntax kontrolünü bildirdi. Kodun remote'a gelmesi ile kodun gerçek Python/FFmpeg testlerinden geçmesi farklı olgulardır. GitHub [synthetic CI run 42127295591](https://github.com/Centaurioun/video-intelligence-pipeline-2/actions/runs/42127295591) at 44d4e0a6... SUCCESS idi, ama yeni CORE-01 PTS/indexer/real-source/CLI test dosyalarının tamamı o workflow'un seçilen popülasyonunda değildi. Bu başarıyı CORE-01 kabulü diye yazma.

**Henüz gözlenmeyen:** Codex'in gerçek local pytest + generated-media FFmpeg sonucu, gerçek 3.11/3.14 focused suite sayaçları, run-time kusur tamiri, model ağırlıklarıyla inference, genuine one-video CLI end-to-end, canonical'a seçici transfer. Bunlar PENDING/NOT_OBSERVED.

### Öncelikli gerçek Codex doğrulama dosyası

https://github.com/Centaurioun/video-intelligence-pipeline-2/blob/main/docs/ai-studio-tasks/MEGA_CORE_01_CODEX_VERIFICATION_AND_REPAIR.md

Belge 2026-11-06 tarihli ve durumu PENDING. Kopyala-yapıştır prompt yerine önce bu dosyanın **tamamı** uygulanacak. Mevcut LAB main'de yalnız bu Markdown'un b96c807... ile eklendiği doğrulandı; buna bakarak test geçti iddiası yapılamaz.

### Eğer Codex'den henüz sonuç gelmediyse en kısa görev promptu

~~~text
Use the existing local Video Intelligence Pipeline 2 repository.

Fetch the latest origin/main non-destructively and read:
docs/ai-studio-tasks/MEGA_CORE_01_CODEX_VERIFICATION_AND_REPAIR.md

Execute the complete verification and bounded repair task.
The AI Studio source candidate is 44d4e0a6c80c924b837303a34ff373fc0d2a14cc.

Use an isolated worktree, preserving all dirty checkouts. Run genuine
Python 3.11/3.14 focused tests and permitted generated-media FFmpeg checks.
Diagnose observed failures before minimal repair; preserve all established
source/temporal/evidence/CLI contracts. If needed, forward-only publish
a separately verified small fix to LAB main.

Do not alter canonical main, run protected media, download models, call
providers, initiate render/export, or begin CORE-02.

Respond in Turkish with exact initial/final commits, commands and counts,
confirmed defects, review outcome, hosted CI, and remaining blockers.
~~~

Kullanıcıya bu prompt **önceki konuşmada zaten verildi**. Aynısını yeniden teklif edip mükerrer Codex işini başlatma. Kullanıcı Codex'in yanıtını gönderirse bundan devam et.

---

## 5. CORE-01'de özellikle incelenecek beş sözleşme riski

Bunlar **ön inceleme soruları**, henüz bağımsız olarak doğrulanmış yeni bug değil:

1. FFmpeg showinfo *input timebase* ile kaynak ffprobe stream timebase eşitliği gerçekten kanıtlanabiliyor mu? showinfo config satırı **hiç gelmediğinde** nasıl davranılıyor? Filtre zaman tabanı değiştiğinde kaynak-native authority uydurulmasın.
2. Ses track'i index 0, video track'i index 1 olduğunda ve çoklu video stream'lerinde probe seçimi ile -map gerçekten aynı mutlak stream'i seçiyor mu? ffprobe stream.index ile ISO-BMFF tkhd.track_ID eşit sayılmasın.
3. Hit'te coarse window tanımlı değilken semantic interval **start == end** kalıyor; zero-width half-open “interval”ın downstream ReviewBundle/Gate-3 sözleşmelerinde geçerli olup olmadığı test edilsin. Nokta gözlemini uydurma durasyona dönüştürme.
4. NEGATIVE_PTS ve NON_MONOTONIC_PTS reddinin desteklenen gerçek medya akışlarında yanlış olumsuz sonuç üretip üretmediği generated fixtures ile değerlendirilsin; nominal FPS üzerinden fallback yapılmasın.
5. index-local summary failed>0, eksik/bozuk sayaç, skip/reused/duplicate, tek JSON ve exit code durumları fresh-process ile doğrulansın. Diğer LAB synthetic/CLI komutları değişmeden kalsın.

Bir tespit gerçek test veya statik kanıt olmadan “CONFIRMED_DEFECT” ilan edilmesin. Program yalnız generated-safe FFmpeg fikstürleri üzerinde denenecek; gerçek arşiv/video yetkisi otomatik türemez.

---

## 6. Sonraki yazılım kapanış planı — mümkün olan en az büyük görev

**Çalışma varsayımı:** CORE-01 doğru sonuçlanırsa tek büyük CORE-02 yazılım paketi + Codex düzeltme/CI paketi yeterli olabilir. Bunun garanti olduğu veya gerçek runtime'ın zaten çalıştığı iddia edilmez. Yeni bug çıkarsa yalnız dar onarım yapılır. Yeni MEGA sayıları üretip yıllarca sürdürmek kullanıcının hedefi değildir.

### Faz 1 — CORE-01 Codex bağımsız verification (aktif / önce)

- Exact LAB main'i fetch et, izole worktree oluştur, mevcut test matrisini çalıştır, sentetik FFmpeg kaynaklarıyla timebase/stream PTS risklerini araştır.
- Gerekirse yalnız kanıtlı kusuru TDD/bugfix ile gider; local Python 3.11/3.14, relevant hosted CI, exact-head source review doğrulansın.
- Gerçek medya/model/sağlayıcı yok, canonical source rewrite yok.
- Çıkış: **MEGA_CORE_01_CODEX_VERIFIED** veya gerekçeli PARTIAL. Son SHA, test komutları ve sayaçlar GitHub'a bağlanmalı.

### Faz 2 — CORE-02: versioned tek-video analiz JSON + kullanılabilir ürün CLI'si (sonraki büyük AI Studio işi)

Bu görev dosyası **henüz yazılmadı ve uygulanmadı**. Önce CORE-01 verified SHA ve güncel canonical/LAB diff kontrol edilecek.

Hedef, aynı mevcut retrieval model ve source-native ölçüm motorunu tekrar yazmadan çalışabilir tek giriş/çıkış arayüzünü tamamlamak. Önce küçük sözleşme kararı ver; sonra bir büyük AI Studio görev dosyası olarak LAB docs/ai-studio-tasks/ içinde sürümlü sakla. Önerilen dosya sorumlulukları (KESİN YENİ MODÜL ZORUNLULUĞU DEĞİL): src/vip_fvs/core_report.py (versioned deterministic report), src/vip_fvs/core_analysis.py (ince orchestration), src/vip_fvs/cli.py (mevcut CLI'ye tek ürün komutu), dar unit/integration/fresh-process testleri ve kısa kullanım rehberi.

Beklenen JSON alanları:
- schema_version, analysis_kind=semantic_retrieval (captioning iddiası değil);
- status, errors, limitations ve deterministik CLI exit status;
- canonical source occurrence/revision/sha256/bytes ve seçili stream/timebase/snapshot/probe kimlikleri;
- query, corpus/index generation, sampling policy, model identity/family/revision/weights digest, processor/semantic space ve yerel runtime provenance;
- actual matched hits/scores ve örnek/native PTS/timebase; approximate semantic candidate ile refined MEASURED technical interval ayrımı;
- MATCHED ile MEASURED, authentic ile synthetic, zero-match ile failed ayrımı;
- JSON output no-clobber/overwrite ve kaynak değişmezliği.
- Sağlanan/çıkarılamayan gerçek kanıtlar için açık NOT_OBSERVED; kaynakta olmayan veriyi uydurma.

Ürün arayüzü **index-local + query-local + prepare-real** gibi mevcut mekanizmaları kullanmalı; yeni decoder, yeni embedding backend, ayrı React/Express sunucu veya yeni provenance engine kurmamalı. Kapsam dondurulmadan doğrudan UI/captioning özelliği icat edilmemeli. Sahte runtime gerçek diye maskelenmemeli.

AI Studio yine Python kodu/testi yazacak; Codex yerelde gerçek test/onarım ve CI doğrulamasını tamamlayacak. LAB main'e direct-push çalışma tarzı korunacak. **CORE-02 başlamadan önce mutlaka CORE-01 Codex sonucu incelensin.**

### Faz 3 — Canonical'a seçici entegrasyon, LAB'ın tamamını taşımak değil

CORE-01 ve CORE-02 LAB'da kaynak/CLI açısından verified olduktan sonra her dosyayı karşılaştır:
- canonical'da zaten var olan / daha doğru üretim kodunu **yeniden kopyalama**;
- yalnız CORE için gerçekten gerekli kaynak, minimal test, sözleşme ve dokümanı kaynak SHA/diff / bağımlılık bazında taşı;
- src/vip_lab/mega03..17, fake reviewer ve sentetik fixture readiness orchestrator'ları **otomatik import dışı**;
- canonical AGENTS/owner-adoption/process kurallarına uy, ayrı izole çalışma dalı ve controlled PR/merge ile doğrula;
- canonical main'in immutable/history/approval kuralları asla LAB direct-main alışkanlığıyla aşılmasın.

### Faz 4 — Gerçek tek-video model/CLI kabulü (ayrı somut yetki gerekir)

Yalnız Owner'ın açıkça izin verdiği bir tek video ve yerelde bulunan, doğrulanmış SigLIP model varlıklarıyla tek bir authentic CLI acceptance çalıştırması. Gerçek izin kapsamı: yol/byte SHA, snapshot/okuma türevleri, geçici dosya, local model/runtime, output, saklama/temizleme/no-egress. Model indirimi veya provider çağrısı otomatik yetki değildir. Rapor, gerçek source_sha256/revision/stream, gerçek sampled PTS/timebase, query/hits, model/processor/runtime identity, digest, errors, limitations ve no-match durumunu kanıtlamalı. Ölçülmüş kaynak PTS'si edit boundary veya insan kararı olarak yanlış terfi etmemeli. Sonra canonical local testleri geçip **CORE_CLI_PRODUCT_COMPLETE** verilebilir.

**Nihai başarılı ürün sonucu:** Canonical repo tek gerçek proje olarak devam eder. Daha sonra UI, üç-arm model benchmark'ı, arşiv çapı concurrency/scale, gelişmiş otomatik caption, editing/render/export, QC ve Gate promotion ayrı ürün/araştırma fazıdır.

---

## 7. Kapsam dışında bırakılacak ürün ve teknoloji işleri

Şimdilik **yapma**: Google AI Studio'ya sahte Node/Vite/Express dev server ekletme; React dashboard, mock upload/progress bar, URL ile provider ingest; Gemini API KEY veya cloud yükleme; fluent-ffmpeg/rasgele interval frame sampling ile PTS authority; yeni backend olarak Qdrant/LanceDB/Milvus; RAG framework; tüm model profillerinin otantik benchmark'ı; Gate-0 iki-hakemli golden-event çalışması; re-identification üzerinden source identity üretme; gerçek arşivin toplu analizi; üretim edit plan/render/export; gerçek insan kararı yerine AI önerisini otomatik koyma.

İleriki teknoloji radarında Qdrant/LanceDB, OpenTimelineIO, FiftyOne, Essentia/Chromaprint ve ffmpeg-quality-metrics değerli aday olabilir. Bunlar ölçülmüş deficit / açık ürün ihtiyacı ortaya çıkmadan CORE teslimini engelleyen bağımlılık değildir. Ayrıntı: kullanıcı tarafından sağlanan teknoloji değerlendirmeleri ve canonical docs/research.

---

## 8. Bilimsel kanıt, zaman ve işlem yetkisi

**Canonical assertion classes:** MEASURED, MATCHED, VISUALLY_OBSERVED, AUDIO_OBSERVED, EDITORIAL_INFERENCE. **NOT_OBSERVED evidence class değil durum marker'ıdır.**

Semantic model/provider timestamp yalnız aday koordinatıdır; exact source-frame/edit boundary değildir. Variable frame rate için seconds × nominal FPS hesabı yasak; native integer PTS, rational timebase, gerçek frame provenance, stream namespace gerekir. ffprobe stream.index ile ISO BMFF tkhd.track_ID eşitlenmez. Raw media immutable. Source path, filename, storage/provider/video/UI/vector IDs canonical source identity değildir; occurrence ve revision/custody ayrımı önemlidir. Fake generated counter gerçek Gate-2 ölçümü değildir. Authentic model çalışmadan model-weight winner ilan edilmez. MEGA-17 readiness veya Gate-3 synthetic preflight, insan editör kararı ve production export yetkisi üretmez.

**Üretim ve veri izinleri:** Bu handoff, GitHub dokümantasyon yazısının izninden başka bir işlem izni vermiyor. Özellikle: protected/archive video read/stat/hash/probe/copy/index; gerçek model download/load veya provider API; public internet upload/egress; yeni gerçek deney; production render/export; Gate promotion; destructive Git temizliği; canonical merge — bunlar mevcut yalnızca CORE-01 local generated-only verification yetkisinden çıkarılamaz. Kullanıcı geçmişte “genel onay veriyorum” demiş olsa da güncel dar medya/model operasyonu için açık dosya ve eylem kapsamı gerektiği korunur.

**Development grants:** Canonical docs/decisions/ADR-0003-development-source-authorization-enforcement-removed.md gereği sıradan development source-authorization *enforcement* DISABLED_BY_OWNER. Bu, gerçek arşiv, media/model/prod yetkisinin genel olarak açıldığı anlamına gelmez. Başka adıyla yeniden gereksiz admin blocker üretme.

---

## 9. Superpowers iş yöntemi ve altı refinement döngüsü

Superpowers'ı her turda göstermelik 12-skill ritüeli gibi çalıştırma; **tetik ve sorumluluğa göre** kullan:
- yeni tasarım/sözleşme → brainstorming ve Owner design signoff;
- kabul edilmiş kapsamlı kod işi → writing-plans;
- yazma gerektiren izolasyon → using-git-worktrees / verified exact head;
- bağımsız alt işler gerçekten varsa → dispatching-parallel-agents, exclusive writer; paylaşılmış CLI dosyalarını yarış halinde edit ettirme;
- davranış değişimi → test-driven-development; AI Studio pytest çalıştıramıyorsa TESTS_AUTHORED_NOT_EXECUTED, Codex gerçek RED/GREEN'e bakar;
- hata → systematic-debugging, önce gerçek failure cause;
- biten feature → requesting-code-review/receiving-code-review;
- başarılı iddia → verification-before-completion.

**Bu belge için altı editöryal öz denetim döngüsü (kaynaklar yalnız eldeki gözlemler):**

1. **Provenance/snapshot:** Her iki GitHub main SHA, code-vs-docs commit ayrımı, merged PR'lar ve aktif iki CORE-01 paket kontrol edildi.
2. **Owner ürün hedefi:** Teknik dört Gate / tarihi 43+ WBS görevi ile Owner'ın dar CORE-CLI coding-finish tanımı karıştırılmadı.
3. **Depoların sahipliği:** LAB AI Studio direct-main, Codex gerçek test, canonical selective-port ve future single-repo stratejisi korunup bulk merge reddedildi.
4. **Test ve kanıt dürüstlüğü:** LAB kod yüklemesi, genel synthetic CI, focused pytest ve authentic media/model kabulünün farklı durumları açıkça etiketlendi.
5. **Adversarial/anti-drift:** .git olmayan AI Studio snapshot'ının UI sync'i, sildiği gate0/media dosyaları, yanlış/eksik timebase, stream namespace, zero-width candidate ve yanlış exit code riskleri ayrı yazıldı.
6. **Yeni instance playback:** Başlangıç okuma sırası, tam devam noktası, beklenen Codex çıktısı, CORE-02 iş sınırı, yetki ve kısa prompt tek belgede yeniden kurulabilecek biçimde denetlendi.

Bu altı döngü **ayrı bağımsız reviewer / Python test / gerçek medya sertifikası yapıldığı anlamına gelmez**. Dokümantasyon incelemesidir.

---

## 10. Eski işleri yeniden çalıştırmadan ulaşılacak kaynak haritası

### Canonical (asıl otorite)

- Repository: https://github.com/Centaurioun/video-intelligence-pipeline
- AGENTS: https://github.com/Centaurioun/video-intelligence-pipeline/blob/main/AGENTS.md
- Index: https://github.com/Centaurioun/video-intelligence-pipeline/blob/main/docs/INDEX.md
- Charter: https://github.com/Centaurioun/video-intelligence-pipeline/blob/main/docs/project/00_PROJECT_CHARTER.md
- State: https://github.com/Centaurioun/video-intelligence-pipeline/blob/main/docs/project/01_CURRENT_STATE_AND_HANDOFF.md
- Orchestration: https://github.com/Centaurioun/video-intelligence-pipeline/blob/main/docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md
- Maintenance: https://github.com/Centaurioun/video-intelligence-pipeline/blob/main/docs/project/STATE_MAINTENANCE_PROTOCOL.md
- Canonical merge #258: https://github.com/Centaurioun/video-intelligence-pipeline/commit/3bfcc2ba221b36df6773e630b44479ec961d630a

### LAB (geliştirme ve current task)

- Repository: https://github.com/Centaurioun/video-intelligence-pipeline-2
- Previous handoff 2026-11-04, HISTORICAL: https://github.com/Centaurioun/video-intelligence-pipeline-2/blob/main/docs/project/2026-11-04_CHATGPT_HANDOFF_POST_MEGA14_PRE_MEGA15_16.md
- CORE-01 AI Studio source task: https://github.com/Centaurioun/video-intelligence-pipeline-2/blob/main/docs/ai-studio-tasks/MEGA_CORE_01_TEMPORAL_STREAM_AND_CLI_CORRECTNESS.md
- CORE-01 Codex verification task: https://github.com/Centaurioun/video-intelligence-pipeline-2/blob/main/docs/ai-studio-tasks/MEGA_CORE_01_CODEX_VERIFICATION_AND_REPAIR.md
- CORE-01 exact code: https://github.com/Centaurioun/video-intelligence-pipeline-2/commit/44d4e0a6c80c924b837303a34ff373fc0d2a14cc
- CORE-01 limited synthetic CI: https://github.com/Centaurioun/video-intelligence-pipeline-2/actions/runs/42127295591
- MEGA-15/16 program: https://github.com/Centaurioun/video-intelligence-pipeline-2/blob/main/docs/ai-studio-tasks/MEGA_15_16_GATE3_OFFLINE_PREPARATION_PROGRAM.md
- MEGA-17 ledger: https://github.com/Centaurioun/video-intelligence-pipeline-2/blob/main/docs/ai-studio-tasks/MEGA_17_CROSS_WORKSTREAM_ACCEPTANCE.md
- Task 5 historical receipts: https://github.com/Centaurioun/video-intelligence-pipeline-2/blob/main/docs/ai-studio-tasks/POST_MEGA17_TEST_LANES_EXECUTION_RECEIPTS.md

LAB 2026-11-05 tarihli POST_MEGA17_OWNER_DECISIONS_AND_NEXT_SLICES.md belgesi canonical PR #258'i hâlâ Draft/OPEN gösteriyor; **artık stale**. Güncel GitHub ref ve bu belgenin kesin tarihi üstündür. Eski spec ve CI raporlarını tarihsel kanıt olarak koru, eski “NEXT” yönlendirmelerini otomatik çalıştırma.

---

## 11. Son iki gerçek promptun arşivi

### A. Google AI Studio için CORE-01 yazdırma promptu — **ALREADY USED / DO NOT REPLAY**

~~~text
Refresh the existing GitHub repository:
Centaurioun/video-intelligence-pipeline-2

Use the current main branch.

Read and execute the complete task specification:
docs/ai-studio-tasks/MEGA_CORE_01_TEMPORAL_STREAM_AND_CLI_CORRECTNESS.md

Implement all four scoped corrections and their regression tests.
Follow the document's safety, source compatibility, and Git publication requirements.

Do not create a new repository, branch, or pull request.
Do not modify the canonical repository.
Do not claim Python tests passed; they will be executed by Codex.

Commit and push the completed changes directly to the existing LAB main branch.
Return the final commit SHA, changed files, corrections, tests authored,
and unresolved blockers in Turkish.
~~~

**Gözlenen sonucu:** GitHub UI sync ile 8 dosyalık CORE-01 commit'i 44d4e0a6... LAB main'e ulaştı. AI Studio .git olmadığı için kendi CLI push'unu NOT_OBSERVED diye raporladı; gerçek GitHub sync ayrı doğrulandı. Testler henüz Codex tarafından gözlenmedi.

### B. Codex için CORE-01 test/onarım promptu — **CURRENT PENDING TASK**

Bu belgenin 4. bölümündeki exact kısa Codex promptu son kullanıcıya verildi. Tam yetki/sınır/giriş komutları MEGA_CORE_01_CODEX_VERIFICATION_AND_REPAIR.md içindedir. Kullanıcının sonraki cevabı muhtemelen bu Codex çalışmasının raporudur. Aynı işi ikinci bir Codex oturumunda başlatma.

### C. Yeni Google AI Studio için gelecekte CORE-02 promptu — **NOT WRITTEN / NOT AUTHORIZED TO EXECUTE YET**

CORE-01 doğrulanınca şu eski çalışma düzeniyle hazırlanacak: görev metnini önce LAB docs/ai-studio-tasks/ içinde oluştur, exact yeni LAB SHA/CLI sözleşmelerini belirt, sonra kısa bir 'read this task file and execute' promptu ver. CORE-01'i yeniden kodlatma; gerçekte olmayan kabulü/benchmark'ı çağırma.

---

## 12. Yeni sohbet için kısa bağlam ve karar uyarıları

Kullanıcıya “projede 43 görev kaldı” diyerek tüm Gate bilimsel WBS'sini CORE coding finish ile bir tutma. Mevcut üç büyük *pratik* iş kategorisi: (1) CORE-01 genuine verification, (2) CORE-02 ürün raporu + tek CLI entegrasyon ve genuine verification, (3) seçici canonical taşınma + kullanıcı onaylı tek gerçek video kabulü. İş sayısı **yaklaşık** ve test kanıtıyla değişebilir; bitti diyerek eksikleri gizleme.

Kullanıcı büyük işleri Google AI Studio'ya hızlı yazdırmak, karmaşık ama daha kısa CI düzeltmelerini Codex'e vermek istiyor. İlgili görev dosyalarını repo'ya yaz, kullanıcıya tek kısa prompt ver. Her yeni doküman/claim için GitHub readback ve SHA göster. Aynı işi yeniden yapmak veya kullanıcıdan daha önce verdiği hedef açıklamasını tekrar istemek kötü deneyimdir.

**Bitiş durumu:** CORE_CLI_PRODUCT_COMPLETE = **NOT_VERIFIED**.  
**Son gerçek kod durumu:** LAB 44d4e0a6... CORE-01 candidate; kullanıcı tarafından Codex'e verilen verification paketi LAB b96c807... docs-only commit'inde mevcut.  
**Exact next:** Codex'den CORE-01 execution report al; current GitHub SHA/diff+focused Python/FFmpeg kanıtını doğrula; gerekirse dar bugfix; ardından versioned CORE-02 task design/spec yazıp yeni AI Studio işi ver.  
**No authority to promote:** real-media, authentic model, Gate, render/export, user approval gerektiren canonical merge.

Bu belge zaman içinde eskiyebilir; **yeni ChatGPT canlı main/CI kontrolünü yeniden yapmalıdır.**

---

## 13. Yeni sohbet başlatma promptu (bu belgeye bağla)

~~~text
Video Intelligence Pipeline projesine bu GitHub handoff'unu tamamen okuyarak devam et:

https://github.com/Centaurioun/video-intelligence-pipeline-2/blob/main/docs/project/2026-11-06_CHATGPT_HANDOFF_CORE_CLI_PRODUCT_CLOSURE.md

Önce iki repo'nun güncel main'ini ve ilgili görev/CI kanıtlarını bağımsız doğrula. Benim CORE_CLI_PRODUCT_COMPLETE bitiş tanımımı, LAB Google AI Studio -> Codex test -> canonical'a seçici aktarım stratejimizi, source-native PTS ve yetki sınırlarını koru. Son iki CORE-01 promptunu tekrar çalıştırma. Sıradaki Codex sonucumu paylaşınca aynı noktadan devam edelim. Benimle Türkçe konuş ve önceki açıklamaları yeniden isteme.
~~~

**Bu yeni handoff yalnızca ChatGPT devamlılık belgesidir; canonical 01_CURRENT_STATE_AND_HANDOFF.md dosyasının yerini alan governing sözleşme veya gerçek işlem izni değildir.**
