# Gate-0 review-input authorized root

`config/gate0/default.json` declares `policy.review_input.authorized_root` as this
directory. The frozen Gate-0 implementation specification v1.1.1 erratum requires
the `evaluate` stage to accept exactly one `--review-input <path>` pointing at a
regular local file strictly beneath that root.

This directory intentionally contains no reviewer judgments: real reviewer input
is human-authored, blinded and frozen before held-out ranking. Synthetic execution
tests generate a deterministic reviewer-input envelope inside this root at test
time (and remove it afterwards) so the structural and policy checks are executed
against the real configured root. Do not commit synthetic or real reviewer input
here.
