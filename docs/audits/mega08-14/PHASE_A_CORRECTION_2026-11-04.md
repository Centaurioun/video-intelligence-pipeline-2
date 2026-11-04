# Faz A düzeltme eki — CI kapsamı (2026-11-04)

**Bu ek, önceki rapordaki tek bir CI bulgusunu açıkça düzeltir.** İlk rapor korunmuştur; aşağıdaki finding ve kanıt onun yerine geçer. İlk raporun silinmiş veya baştan doğruymuş gibi düzenlenmiş olduğu izlenimi verilmemelidir.

## Önceki bulgu ve düzeltme

`PRE_EXECUTION_SCOPE_AND_RISKS.md` içindeki `A-01 (P1)` bulgusu, LAB’ın mevcut workflow’unun MEGA-08…14 testlerini seçmediğini ve tamamlılık kontrolü olmadığını ileri sürmüştü. Bu iddia yanlıştır. Workflow’un yalnızca ilk 245 satırlık bölümü okunup, devamındaki eklenmiş adımlar gözden kaçırılmıştır.

### Doğrulanmış kaynak kanıtı — `SOURCE_INSPECTED`

LAB `origin/main` tam olarak `b55b14884dc5d62f8784c60af2a8e14fea107b36` olarak fetch edildi. Aynı commit’in `.github/workflows/vip-ai-studio-synthetic-ci.yml` dosyasında:

- Satır **263–334**: MEGA-08…14 dosya tamlık kontrolü. Bir dalganın hiçbir dosyası yoksa `NOT_SUBMITTED`; kısmi teslimde eksik dosya/progress ledger hata verir.
- Satır **336–412**: MEGA-08, 09, 10, 11, 12, 13 için ayrı pytest adımları; MEGA-14 adımı `test_mega14.py` ve `test_mega08_14_end_to_end.py` dosyalarını birlikte seçer. Her adım test dosyası mevcutsa çalışır; yoksa koşullu olarak atlanır.
- Satır **414–443**: final aggregate, completeness ve test adımlarından herhangi biri `failure` ise job’u başarısız yapar; açıkça `SKIPPED does not mean complete` der.

Baseline’a kıyasla workflow dosyası `M` durumundadır; `22f1ffa…..b55b148…` aralığında 182 satır eklenmiştir. Bu nedenle kontrolün başlangıç baseline’ında bulunduğu değil, sonradan `b55b148…` ile eklendiği anlaşılmalıdır.

### Doğrulanmış Actions kanıtı — `VERIFIED_GITHUB`

[Run 41760125750](https://github.com/Centaurioun/video-intelligence-pipeline-2/actions/runs/41760125750) tam olarak `b55b148…` SHA’sını çalıştırmış ve başarılı tamamlanmıştır. Python 3.11 (`126345582059`) ve 3.14 (`126345582348`) job’ları başarılıdır.

Her iki job logunda da:

- MEGA-08…14 completeness kontrolü `success`;
- MEGA-08…14 pytest adımlarının **yedi tanesi `skipped`** (dosyalar henüz sunulmadığı için koşullu seçici devreye girmemiş);
- aggregate enforcement `success` ve “No submitted … suite failed. SKIPPED does not mean complete.” çıktısı vardır.

Sonuç: CI, bu commit’te yeni dalgaların kodunu/testini yürütmemiştir. Yalnızca yeni dosyaların henüz sunulmadığını doğru biçimde kaydetmiş ve mevcut test matrisinin sonucunu raporlamıştır. `SUCCESS` yeni dalgalar için başarı/uygulama doğrulaması değildir.

## Düzeltilmiş finding

Önceki `A-01 (P1)` **WITHDRAWN — audit reviewer error**. CI workflow kapsamının eksik olduğu yönünde açık bir bulgu artık yoktur; doğrulanan `b55b148…` workflow’u görev programının koşullu seçim/tamamlık davranışını sağlar.

Yeni kod/testler eklendiğinde sonraki incelemede yine exact SHA’da dosya seçimi, her iki Python sürümünde gerçek pytest sonuçları, test sayıları ve fail enforcement doğrulanmalıdır. Şu an yeni dalga sonuçları `NOT_OBSERVED` ve faz durumu `NOT_YET_SUBMITTED` olarak kalır.

## Faz B disposition

`b55b148…` içinde MEGA-08…14 uygulama/test kaynakları olmadığı ve ilgili CI adımları `skipped` olduğu için Faz B başlamaz. Yeni immutable LAB main implementation commit’i yayımlandığında ledger’a yeni inceleme satırı eklenir. Bu düzeltme yalnızca audit branch dokümantasyonudur; LAB main veya protected VIP değiştirilmemiştir.
