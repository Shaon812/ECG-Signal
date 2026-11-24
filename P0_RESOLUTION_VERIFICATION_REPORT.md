# P0_RESOLUTION_VERIFICATION_REPORT

Generated: 2026-11-22
Project root: `C:\Users\Lenovo\Downloads\ECG_QPAIN_2027`

All P0 issues from `RESEARCH_REPRODUCIBILITY_AUDIT.md` were addressed with
**additive files only**. No training, no test evaluation, no checkpoint promotion,
no dataset modification, no change to historical metrics. All 30 non-notebook
research files remain byte-for-byte unchanged.

---

## Summary

| Task | Status |
|---|---|
| 1. Canonical B3 experiment configuration | **PASS** |
| 2. Machine-readable checkpoint registry | **PASS** |
| 3. Exact dependency lock | **PASS** |
| 4. Split-count discrepancy investigation | **PASS — RESOLVED** |
| 5. Verification suite (48 checks + smoke test) | **PASS — 48/48 + smoke PASS** |

---

## Task 1 — Canonical B3 configuration — PASS

New file: `reports/B3_training_config_canonical.json` (`config_version: B3-canonical-v1`).

Contains: seed 2027 (with per-component seed usage), batch size **128**,
learning rate 0.0001, LAMBDA_CAM 0.1, class weights
`[0.281067, 7.632924, 3.533728, 35.547619]` plus full-precision values,
bandpass 0.5–40 Hz order 4, beat window 126/162 (288 samples), noise seed 2027,
noise types BW/MA channel 0, validation SNRs [18,12,6], training SNRs [24,18,12,6],
fresh Adam with `state_restored: false`, planned epochs 10, test data not used.

The stale `batch_size: 32` is **corrected in the new canonical file only**.
`reports/B3_B4_experiment_config.json` is **retained unchanged** as the historical
record (verified by SHA256 against the pre-migration snapshot); the canonical file
explicitly names it as superseded.

## Task 2 — Checkpoint registry — PASS

New file: `reports/checkpoint_registry.csv` (5 rows, 9 columns incl. Notes).

| Epoch | Checkpoint | Status | Macro-F1 |
|---|---|---|---|
| initial | `initial_B3_from_B2.keras` | backup | — |
| 3 | `best_B3_resnet.keras` | best | 0.3644898279927664 |
| 4 | `backups/latest_epoch4_…keras` | backup | 0.34801116820149897 |
| 3 | `backups/best_epoch4_…keras` | backup | 0.3644898279927664 |
| 5 | `latest_B3_resnet.keras` | latest | 0.3542619613487781 |

Every SHA256 and `date_saved` was computed directly from the checkpoint file /
embedded `metadata.json` at creation time, then re-verified by the audit suite.
Only verified values were used: the `best_epoch4` backup is registered as
**Epoch 3 weights** (byte-identical to the best checkpoint) with an explicit note
that the snapshot was taken after Epoch 4 — no epoch number was inferred without evidence.

## Task 3 — Dependency lock — PASS

New file: `requirements.lock.txt` with **145** pinned `name==version` entries taken
from the exact installed `.venv` packages via `importlib.metadata`. Header records
Python 3.12.16, the interpreter path, platform and generation method.
Verification: locked set == installed set (145 vs 145), **0 version mismatches**.
No package was upgraded or downgraded; `requirements.txt` remains the unpinned
human-readable list.

## Task 4 — Split-count discrepancy — PASS (conclusively resolved)

New file: `reports/SPLIT_COUNT_DISCREPANCY_INVESTIGATION.md`.

**Cause:** notebook 03 cell 16 defines `BEFORE_R = 126`, `AFTER_R = 162`
(`BEAT_LENGTH = 288`) and skips any annotation whose full window falls outside
the 650,000-sample record:

```python
if start < 0 or end > len(filtered_signal):
    boundary_count += 1
    continue
```

Stored notebook outputs record `Boundary beats: 45`. Recomputing directly from
`wfdb.rdann` for all 48 records with the same window gives **Train 23 / Validation 10 /
Test 12 = 45**, exactly matching the observed differences. The 11,196 non-AAMI
annotations were already excluded upstream when split totals were computed, so
they are unrelated. Not corruption or leakage; no unresolved aspects remain.

## Task 5 — Verification suite — PASS

Automated checks (48 total):

| Area | Checks | Result |
|---|---:|---|
| Config consistency (incl. original config unchanged) | 12 | **12 PASS** |
| Registry: paths, SHA256, dates, F1, status, config version | 27 | **27 PASS** |
| Lock file coverage and versions | 2 | **2 PASS** |
| Dataset counts, quality report, discrepancy, investigation file | 6 | **6 PASS** |
| Research-file integrity (30 files) and history row count | 2 | **2 PASS** |
| **Total** | **48** | **48 PASS / 0 FAIL** |

Additional safe check: `python train_b3_epoch6.py --smoke` — one batch-4 step on an
in-memory clone with a fresh Adam; all losses finite, 31/31 temporary trainable
arrays updated, and **all official checkpoints/backups/history unchanged**.

---

## Files created (all additive)

- `reports/B3_training_config_canonical.json`
- `reports/checkpoint_registry.csv`
- `requirements.lock.txt`
- `reports/SPLIT_COUNT_DISCREPANCY_INVESTIGATION.md`
- `REPRODUCIBILITY_CHECKLIST.md`, `RESEARCH_REPRODUCIBILITY_AUDIT.md` (previous audit)
- this report

## Remaining notes (not blockers)

- Checkpoints were saved with Keras 3.13.2; the local environment has Keras 3.15.1.
  Loading was already verified successful; no rewrite was performed.
- P1/P2 recommendations from the earlier audit (dataset citations, evaluation CSV
  provenance columns, unified clean-vs-noisy table, sealed test protocol) remain open.
- Epoch 6 is still deliberately untrained; requires a suitable GPU.
- No `--commit`, no promotion, no test evaluation was executed.

## Integrity statement

All 30 non-notebook research files re-hashed after the work: **0 changed**.
Epoch 4 backups, `best_B3_resnet.keras` (Epoch 3), `latest_B3_resnet.keras`
(Epoch 5), all processed arrays, notebooks and historical CSVs are untouched.
