# P1_DOCUMENTATION_VERIFICATION_REPORT

Generated: 2026-11-22
Scope: read-only research documentation; additive files only. No training, no test
evaluation, no checkpoint promotion, no dataset change, no historical-result change.

---

## Summary

| Task | Status |
|---|---|
| 1. Dataset references | **PASS** |
| 2. Evaluation provenance | **PASS** |
| 3. Unified clean-vs-noisy results | **PASS** |
| 4. Historical hardware documentation | **PASS** |
| 5. Verification (25 checks) | **PASS — 25/25** |

---

## Task 1 — Dataset references — PASS

New file: `reports/DATASET_REFERENCES.md`.

Two distinct databases documented from their official PhysioNet pages (fetched
2026-11-22) and bundled local documentation:

| | MITDB | NSTDB |
|---|---|---|
| Official name | MIT-BIH Arrhythmia Database | MIT-BIH Noise Stress Test Database |
| Version | 1.0.0 | 1.0.0 |
| PhysioNet URL | https://physionet.org/content/mitdb/1.0.0/ | https://physionet.org/content/nstdb/1.0.0/ |
| DOI | 10.13026/C2F305 | 10.13026/C2HS3T |
| Published | 2005-02-24 | 1999-08-03 |
| Authors | Moody, Mark | Moody, Mark |
| License | ODC-BY 1.0 | ODC-BY 1.0 |

Citations are transcribed from the official pages: Moody & Mark (2005) dataset
citation and the original 2001 IEEE EMB paper for MITDB; Moody, Muldrow & Mark
(1984) Computers in Cardiology paper for NSTDB; plus PhysioNet's standard citation.
No publication detail was invented. The document explicitly states that only NSTDB
noise records `bw` and `ma` (channel 0) are used, and that `em`, the sample noisy
records and the `old/` first edition are not used by B3.

## Task 2 — Evaluation provenance — PASS

Two additive changes:

1. **`evaluate_b3.py` updated** so every future output (summary, per-class and
   confusion-matrix CSVs) includes `checkpoint_sha256` and `config_version` columns,
   and the console prints both. Config version is read from
   `reports/B3_training_config_canonical.json`; the SHA256 is computed from the exact
   checkpoint file being evaluated. Verified with an 8-beat subset written to a temp
   directory (project untouched): all three CSV headers contained both columns.
2. **`reports/evaluation/EVALUATION_PROVENANCE_SIDECAR.csv`** (13 rows) maps every
   pre-existing evaluation file to its file SHA256, checkpoint SHA256, evaluation
   type, generation timestamp and config-version status. Existing files were
   generated before the canonical config existed, so their config version is honestly
   recorded as `NOT_RECORDED_AT_GENERATION` — no retroactive claim was made.

**All 13 pre-existing evaluation files are byte-for-byte unchanged** (hash-compared
against a snapshot taken before this work).

## Task 3 — Unified results — PASS

New files: `reports/unified_results.csv` (19 rows) and `reports/UNIFIED_RESULTS_README.md`.

Contents, copied verbatim from verified sources:
- B0_CNN and B1_ResNet: clean validation (accuracy, macro-F1, loss).
- B2: noisy validation from a single aggregated noisy set (accuracy, macro-F1,
  weighted F1, loss) with its SNR explicitly marked as not resolved per condition.
- B3 best (Epoch 3) and latest (Epoch 5): clean validation with full metrics, six
  noisy conditions each with full metrics, plus a mean row containing only Macro-F1.

Missing metrics are written as `NOT_AVAILABLE`; **no value was estimated or inferred**.
The README warns that B0/B1 clean, B2 noisy and B3 six-condition noisy protocols are
not directly comparable as one ranking, and that the sealed test split is absent.

## Task 4 — Historical hardware — PASS

New file: `reports/HISTORICAL_TRAINING_ENVIRONMENT.md`.

**Confirmed from stored notebook outputs:** Google Colab; NVIDIA Tesla T4 (15,360 MiB,
~12,683 MiB in use), NVIDIA-SMI/Driver 580.82.07, CUDA 13.0, compute capability 7.5
(notebook 07 cell 177); TensorFlow 2.21.0; Keras 3.13.2 at checkpoint save time;
batch 128 / 467 batches; recorded epoch times from `B3_training_history.csv`.

**Explicitly unknown:** Colab host CPU/RAM, Python version and full package set in
Colab, runtime region, precision/XLA settings, and the reason notebook 05 reported
`GPU available: False` (so B0/B1 device is not claimed).

The local Intel i5 / 8 GB / no-GPU machine is documented separately as the migration
and audit machine, not the historical training machine.

## Task 5 — Verification — PASS

25/25 checks passed:

| Area | Checks | Result |
|---|---:|---|
| New files present and parseable | 12 | PASS |
| Unified values match sources / no estimates / no test data | 6 | PASS |
| Evaluator compiles and emits provenance columns | 3 | PASS |
| 30 research files + 13 evaluation files unchanged; history 5 rows; no staging files | 4 | PASS |

---

## New files (all additive)

- `reports/DATASET_REFERENCES.md`
- `reports/HISTORICAL_TRAINING_ENVIRONMENT.md`
- `reports/evaluation/EVALUATION_PROVENANCE_SIDECAR.csv`
- `reports/unified_results.csv`, `reports/UNIFIED_RESULTS_README.md`
- `P1_DOCUMENTATION_VERIFICATION_REPORT.md`

Modified (additive-only improvement): `evaluate_b3.py` (provenance columns).

## Remaining blockers before Epoch 6 training

1. **Hardware:** no GPU on this laptop. Epoch 6 must run on a suitable GPU machine
   (`--train` refuses without one unless `--allow-cpu` is passed).
2. **Epoch 6 not started** by design; no staged checkpoint exists yet.
3. **Staged evaluation step is manual:** after `--train`, run both
   `evaluate_b3.py --checkpoint .../epoch6_latest.keras` and the `--clean` variant
   before `--commit` (documented in `B3_EPOCH6_WORKFLOW.md`).
4. **Sealed test split:** must remain unused until final model selection; use
   `--approved-test` only with explicit approval.
5. **Keras version difference:** checkpoints were saved with Keras 3.13.2, local
   environment has 3.15.1; loading is verified, but no checkpoint rewrite was done.

None of these are documentation blockers; all P1 items are resolved.

## Integrity statement

All 30 non-notebook research files and all 13 pre-existing evaluation outputs are
byte-for-byte unchanged. No training, promotion, test evaluation or dataset
regeneration occurred.
