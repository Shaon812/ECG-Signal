# Split-count discrepancy investigation — RESOLVED

Generated: 2026-11-22
Scope: read-only investigation. No dataset, notebook or historical CSV was modified.

## Observed discrepancy

| Split | `patient_independent_split_summary.csv` / `record_split_assignment.csv` | Processed array / `dataset_quality_report.csv` | Difference |
|---|---:|---:|---:|
| Train | 59,743 | 59,720 | **23** |
| Validation | 19,540 | 19,530 | **10** |
| Test | 22,168 | 22,156 | **12** |
| **Total** | 101,451 | 101,406 | **45** |

## Root cause (established from source code)

`03_ECG_Preprocessing_Beat_Extraction.ipynb`:

- Cell 3 / cell 15 define the beat window:
  `BEFORE_R = 126`, `AFTER_R = 162`, `BEAT_LENGTH = BEFORE_R + AFTER_R = 288` samples.
- Cell 16 extracts a beat as `start = sample - BEFORE_R`, `end = sample + AFTER_R`,
  then applies this explicit boundary check:

  ```python
  if start < 0 or end > len(filtered_signal):
      boundary_count += 1
      continue
  ```

  An annotation is therefore dropped whenever its 288-sample window would extend
  before the first or past the last sample of the 650,000-sample record.

- Stored outputs of cells 16 and 20 record:
  `Excluded annotations: 11196` and **`Boundary beats: 45`**.

The 45 boundary-excluded beats match the total discrepancy exactly.

The 11,196 "excluded annotations" are MIT-BIH symbols outside the four AAMI
classes (e.g. Q / f / other symbols). They were already excluded upstream when
notebook 02 built `aami_record_counts.csv`, so they are **not** part of the
23/10/12 difference.

## Independent verification from raw annotations

Recomputed directly from `wfdb.rdann` on all 48 extracted MITDB records, using the
AAMI symbol map from notebook 02 cell 22 and the same window
(126 before / 162 after R-peak), with split labels from
`record_split_assignment.csv`:

| Split | Recomputed boundary beats | Observed difference |
|---|---:|---:|
| Train | 23 | 23 |
| Validation | 10 | 10 |
| Test | 12 | 12 |
| **Total** | **45** | **45** |

The per-split numbers match exactly. The split-summary totals count *all* AAMI
annotations in each patient group; the processed arrays contain only beats whose
full 288-sample window lies inside the record.

## Conclusion

**RESOLVED — not a data corruption or leakage issue.** The discrepancy is the
expected consequence of the documented boundary check in notebook 03 cell 16.
It does not affect patient independence: group membership is identical in both
counting stages.

Recommended documentation action (not yet applied to historical files): annotate
`patient_independent_split_summary.csv` in a NEW companion note or in the research
audit to state that its totals are pre-extraction AAMI annotation counts and that
45 boundary beats (23/10/12) were subsequently removed.

## Integrity

No dataset was modified or regenerated. No historical CSV or notebook was edited.
All values above were derived by reading existing files and raw annotations.
