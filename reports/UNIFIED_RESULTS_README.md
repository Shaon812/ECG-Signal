# Unified results table — reader guide

Companion to `reports/unified_results.csv` (19 rows, all values copied from verified
existing reports; no estimates, no recomputation).

## Evaluation types

- **CLEAN** — clean validation signals, no added noise.
- **NOISY** — validation signals with NSTDB noise added. The protocol differs by model:
  - B2: a single aggregated noisy validation set (notebook 06); the SNR is not resolved
    per condition in the saved report.
  - B3: six fixed conditions, BW and MA at 18, 12 and 6 dB, noise seed 2027.
- B0/B1 have **no noisy results**; B2 has **no clean results**. These cells are marked
  `NOT_AVAILABLE` rather than estimated.

## Metrics column semantics

| Column | Meaning |
|---|---|
| Accuracy / Macro_F1 / Weighted_F1 / Validation_Loss | Copied verbatim from the cited source file |
| Macro_Precision / Macro_Recall | Only available for B3 (computed by `evaluate_b3.py`); otherwise `NOT_AVAILABLE` |
| Validation_SNR_dB | Condition label or explicit "not resolved" note |
| Source_File | Exact file the numbers came from |
| Notes | Caveats (e.g., metric not computed, mean-row contents) |

The `mean of BW/MA @ 18,12,6 dB` rows contain **only** Macro-F1 because the original
reporting convention (notebook 07) reduces six per-condition Macro-F1 values to a
single unweighted mean; other metrics for the mean row would be an invention and are
marked `NOT_AVAILABLE`.

## Comparability warnings

1. B0/B1 clean results and B2/B3 noisy results are **not directly comparable** as a
   single ranking — different evaluation conditions and different metrics reported.
2. B2's noisy protocol differs from B3's six-condition protocol; B2's Macro-F1
   (0.3496804120822582) must not be compared per-SNR with B3 rows.
3. All B3 values come from full 19,530-beat validation runs with checkpoint hashes
   recorded in `reports/evaluation/EVALUATION_PROVENANCE_SIDECAR.csv`.
4. The sealed patient-independent test split appears nowhere in this table.
