# EVALUATION_PIPELINE_VERIFICATION_REPORT

Generated: 2026-11-22
Project root: `C:\Users\Lenovo\Downloads\ECG_QPAIN_2027`

Read-only inspection and preparation. **No training, no full evaluation run, no
modification of any checkpoint, dataset, history CSV, notebook or existing report.**

---

## Summary

| # | Task | Status |
|---|---|---|
| 1 | Inspect existing B3 evaluation functions and notebooks | **PASS** |
| 2 | Verify validation / test evaluation procedures | **PARTIAL** — validation verified; no test evaluation exists (deliberate) |
| 3a | Accuracy calculation | **PASS (B0/B1/B2)** / **FAIL (B3 not reported)** |
| 3b | Macro precision / recall | **PASS (B2 only)** / **FAIL (B0/B1/B3)** |
| 3c | Macro-F1 | **PASS** (all models) |
| 3d | Per-class precision / recall / F1 | **PASS (B0/B1/B2 via classification_report)** / **FAIL (B3)** |
| 3e | Confusion matrix | **PASS (B0/B1/B2)** / **FAIL (B3)** |
| 4 | Label mapping 0=N, 1=S, 2=V, 3=F | **PASS** |
| 5 | Noisy validation at 18/12/6 dB | **PASS** |
| 6 | Clean and noisy results reported separately | **FAIL** |
| 7 | Patient-independent test not used in training/selection | **PASS** |
| 8 | Best checkpoint selected by validation Macro-F1 | **PASS** |
| 9 | Load staged Epoch 6 checkpoint without overwriting | **FAIL (original pipeline)** → **PASS (new `evaluate_b3.py`)** |
| 10 | Missing metrics / bugs / duplication / inconsistencies | findings below |

---

## Task 1 — Existing evaluation code inspected — PASS

Sources examined:
- `05_CNN_ResNet_Clean_Baselines.ipynb` cells 5, 12–14, 19–21, 23: clean validation with
  `model.evaluate`, `predict`+`argmax`, `f1_score(macro)`, `classification_report`,
  `confusion_matrix(labels=[0,1,2,3])`, saved to `clean_baseline_validation_results.csv`.
- `06_Noise_Augmented_ResNet.ipynb` cells 19–23: noisy validation with `model.evaluate`,
  `classification_report`, `accuracy_score`, macro/weighted F1, and a labelled
  confusion matrix saved to `B2_noise_augmented_confusion_matrix.csv`.
- `07_CAM_Consistency_Models.ipynb` cells 108 and 163 define `evaluate_noisy_validation`,
  used at cells 109/111/112/113/175/179. Cells 129/136 restore best F1 from history.

## Task 2 — Validation / test procedures — PARTIAL

- Validation procedure is fully deterministic: `X_val_noisy` is rebuilt with
  `np.random.default_rng(2027)` over BW/MA × [18,12,6] (cells 67/102/104/147/155),
  giving 6 fixed noisy copies. Macro-F1 is computed on `y_val` with
  `zero_division=0` and averaged — this is the `val_macro_f1` written to history.
- **Test set:** notebook 07 cell 133 loads `test_beats.npz`, prints shape and class
  distribution, and **never calls `predict` or `evaluate` on it**. No test metrics
  are produced anywhere in the project. This is intentional and consistent with
  `"test_data_used_for_training": false` in `B3_B4_experiment_config.json`.
- Full validation / test evaluation was **not executed** (inspection only).

## Task 3 — Metric calculations

| Metric | B0/B1 (nb05) | B2 (nb06) | B3 (nb07) | Verdict |
|---|---|---|---|---|
| Accuracy | `model.evaluate` → saved | `accuracy_score` → saved | **not computed** | PASS / **FAIL** |
| Macro precision | absent | absent (only macro/weighted F1) | absent | **FAIL** outside new script |
| Macro recall | absent | absent | absent | **FAIL** outside new script |
| Macro-F1 | `f1_score(macro, zero_division=0)` | `f1_score(macro)` | `f1_score(macro, zero_division=0)` | **PASS** |
| Weighted F1 | absent | `f1_score(weighted)` | absent | PARTIAL |
| Per-class P/R/F1 | `classification_report(target_names=N,S,V,F)` printed only | same, printed only | **absent** | PASS (printed) / **FAIL (B3)** |
| Confusion matrix | plotted, not saved | saved with labelled index/columns | **absent** | PASS / **FAIL** |

Note: macro-F1 is computed identically across B0/B1/B2/B3, so checkpoint-selection
metrics are comparable. Per-class results and confusion matrices for B0/B1/B2 exist
only in notebook outputs or one B2 CSV, not in a unified B3 report.

## Task 4 — Class label mapping — PASS

- `03_...Beat_Extraction.ipynb` cell 14: `CLASS_TO_LABEL = {"N":0,"S":1,"V":2,"F":3}`.
- `02_...AAMI_Classification.ipynb` cell 22: AAMI groups N/S/V/F from MIT-BIH symbols.
- `class_names = ["N","S","V","F"]` used in nb05 cell 5 and nb06/nb07 reports.
- Verified all 3 processed metadata CSVs: zero mismatches between `Class` and `Label`
  (train, validation and test each map N→0, S→1, V→2, F→3).

## Task 5 — Noisy validation SNRs — PASS

`VAL_SNRS = [18, 12, 6]` with noise types `bw` and `ma` → 6 conditions. New script
smoke test confirmed each condition differs from clean and noise increases as SNR
drops (mean |noisy−clean|: BW 0.0177 / 0.0357 / 0.0707; MA 0.0170 / 0.0336 / 0.0677
for 18/12/6 dB), all finite.

## Task 6 — Clean vs noisy reporting — FAIL

- nb05 reports **clean** validation for B0/B1.
- nb06 reports **noisy** validation only for B2 (`X_val_noisy`).
- nb07 reports **noisy** validation only for B3; `B3_training_history.csv` contains
  only the *mean* of the 6 noisy macro-F1 values, not per-condition values and not
  a clean score.
- No existing report places clean and noisy results side by side for B3.

## Task 7 — Patient-independent test not used in training/selection — PASS

- `X_test`/`y_test` appear only in notebook 07 cell 133 (load + distribution print)
  and in notebook 04's file-existence check. No `predict`/`evaluate` call uses them.
- Training uses `X_train`/`y_train` only; model selection uses `val_macro_f1` from
  noisy validation only (cells 111/112/113/175/179).
- Config explicitly records `test_data_used_for_training: false`.

## Task 8 — Best checkpoint selection — PASS

- Each epoch cell computes `val_macro_f1 = evaluate_noisy_validation(b3_model)` and
  saves `best_B3_resnet.keras` only when
  `val_macro_f1 > best_b3_macro_f1` (cells 111–113, 175, 179).
- On recovery, `best_b3_macro_f1 = float(history_df["val_macro_f1"].max())`
  (cells 129/136), so selection is reproducible from history.
- On-disk state is consistent: best = Epoch 3 (0.3644898279927664), Epoch 5's
  0.35426 did not overwrite it.

## Task 9 — Staged Epoch 6 checkpoint evaluation — FAIL (original) → PASS (new)

- **Original pipeline:** notebook 07 hardcodes `B3_LATEST_PATH` and its epoch cells
  save official checkpoints/history. It cannot evaluate an arbitrary staged
  checkpoint without editing the notebook, and re-running those cells risks
  overwriting official artifacts. **FAIL.**
- **Mitigation added:** new `evaluate_b3.py` accepts `--checkpoint <any path>`, never
  trains, never writes official files, and writes only to a new timestamped folder
  `reports/evaluation/` while refusing to overwrite an existing file.
  Verified by loading `best_B3_resnet.keras` (a different checkpoint from the
  default) on an 8-beat subset with `--no-write` — correct architecture, metrics
  and confusion matrix, no files created. **PASS.**
- No staged Epoch 6 checkpoint exists yet; the same command will accept
  `models/B3_CAM_Consistency/epoch6_latest.keras` once `--train` produces it.

## Task 10 — Missing metrics, duplication and inconsistencies

1. **Missing B3 metrics (high priority):** no accuracy, macro precision, macro
   recall, weighted F1, per-class P/R/F1/support, confusion matrix, clean validation
   score, or per-condition noisy results are persisted for B3.
2. **Per-condition results not saved:** notebook 07 prints BW/MA × SNR macro-F1 to
   stdout; only the mean survives in CSV. This prevents auditing the 0.36449 figure.
3. **Clean vs noisy incomparable:** B0/B1 clean, B2/B3 noisy; no unified table.
4. **Duplicated definitions:** `train_one_epoch`, `evaluate_noisy_validation`,
   data/noise setup appear multiple times in notebook 07 (cells 108 vs 163, 15 vs 18
   vs 81, 65 vs 85 vs 147 vs 155). They are identical in effect but create
   maintenance risk. Not a numerical bug.
5. **Minor inconsistency:** nb06 confusion matrix calls `confusion_matrix(y,pred)`
   without `labels=[0,1,2,3]`; all four classes are present so the saved B2 matrix
   is correct, but the call is fragile if a class is absent.
6. **Small-support caveat:** validation has only 17 F beats; per-class F1 for F is
   high-variance. Recording per-condition per-class metrics is important.
7. **`zero_division=0`** used for B0/B1/B3 but not explicitly in B2's `f1_score` —
   no difference here because all classes are present.

No numerical bug was found in metric calculation or best-checkpoint selection.

---

## New file created

`evaluate_b3.py` — checkpoint-agnostic B3 evaluator:

```powershell
# SAFE subset check, no files written:
python evaluate_b3.py --limit 32 --no-write

# Full noisy validation on an arbitrary checkpoint (writes to reports/evaluation/):
python evaluate_b3.py --checkpoint models/B3_CAM_Consistency/epoch6_latest.keras

# Clean validation:
python evaluate_b3.py --clean --checkpoint <path>

# Test evaluation is blocked unless explicitly approved:
python evaluate_b3.py --split test --approved-test --checkpoint <path>
```

Outputs: `<timestamp>_summary.csv`, `<timestamp>_per_class.csv` inside
`reports/evaluation/`. Existing reports are never overwritten.

---

## Recommendations for the next stage

1. After a staged Epoch 6 checkpoint exists, run
   `python evaluate_b3.py --checkpoint models/B3_CAM_Consistency/epoch6_latest.keras`
   on a suitable machine to obtain the missing full metric set.
2. Compare Epoch 6's mean noisy Macro-F1 against the historical best
   `0.3644898279927664` before deciding whether to promote `--commit`.
3. If a paper/report table is needed, add a single consolidated clean-vs-noisy
   summary in a NEW file (do not edit `B3_training_history.csv`).
4. Keep the patient-independent test split sealed until final model selection is
   complete; use the `--approved-test` flag only with explicit sign-off.
5. Do not edit notebook 07's epoch cells to add evaluation — they write official
   artifacts; use `evaluate_b3.py` instead.

---

## Integrity statement

All 30 non-notebook research files were re-hashed after inspection: **0 changed**.
No checkpoint, backup, dataset, history CSV, notebook or existing report was
modified. No report files were created during the smoke tests (`--no-write` was
used); `reports/evaluation/` does not yet exist. No training and no full evaluation
were run.
