# RESEARCH_REPRODUCIBILITY_AUDIT

Generated: 2026-11-22
Project root: `C:\Users\Lenovo\Downloads\ECG_QPAIN_2027`

Read-only audit with three allowed additive changes (listed at the end).
No training, test evaluation, checkpoint promotion or historical-data change.
All 30 non-notebook research files verified unchanged after the audit.

---

## Task-by-task PASS/FAIL

### 1. Audit all B3 experiment configurations — PARTIAL

| Source | Status | Finding |
|---|---|---|
| `reports/B3_B4_experiment_config.json` | **FAIL** | Records lr 0.0001, λ 0.1, epochs 10, SNRs [24,18,12,6], initial weights B2, test not used — but `batch_size: 32` is **stale** (epochs 4–5 and Epoch 6 use 128), and seed, class weights, noise seed, filter parameters and optimizer-reset status are absent. |
| `reports/noise_generation_config.json` | **PARTIAL** | Sampling rate, beat length, SNR sets, noise types (BW/MA/EM), powerline frequencies, noise channel and split ranges are complete. **Noise seed (2027) is not recorded.** EM and 50/60 Hz powerline noise are listed but not used by B3 training (BW/MA channel 0 only) — scope ambiguity. |
| `reports/clean_baseline_training_config.json` | **PASS** | Seed 2027, input shape, class names, batch 128, 30 epochs, Adam 0.001, balanced weighting, patience 5, test_set_used false. |
| Notebook 07 config cells (34/36/135/175/179) | **PASS** | Authoritative values recovered: batch 128, lr 0.0001, λ 0.1, 467 batches. |
| `train_b3_epoch6.py` constants | **PASS** | Batch 128, lr 0.0001, λ 0.1, fresh Adam, threshold 0.3644898279927664. |

### 2. Random seeds and noise reproducibility — FAIL → FIXED

- Notebook 02: `SEED=2027`, split search seed 2027. **PASS**
- Notebooks 05/06/07: `SEED=2027`, `np.random.seed`, `random.seed`, `tf.random.set_seed`, `tf.data shuffle(seed=2027)`, `default_rng(2027)` for noise. **PASS**
- Noise validation construction identical in notebook 07, `train_b3_epoch6.py`, `evaluate_b3.py`: seed 2027, BW/MA, SNRs 18/12/6, region 390000–520000, shared `add_validation_noise`. **PASS** — empirically proven by exact reproduction of both historical Macro-F1 values.
- **Original finding:** `train_b3_epoch6.py` lacked global `np`/`random`/`tf` seeds, so `tf.random.uniform` inside `add_random_noise_with_snr` would not be reproducible. **FIXED** by adding `random.seed(2027)`, `np.random.seed(2027)`, `tf.random.set_seed(2027)` using `config.SEED`.
- Note: `generate_powerline_noise` uses unseeded global `np.random.uniform` when `phase=None`; not used in B3 (BW/MA only) but worth documenting.

### 3. Dataset split and patient-independent separation — PARTIAL

- Reports present: `patient_group_split.csv`, `record_split_assignment.csv`, `patient_independent_split_summary.csv`, `aami_record_counts.csv`. **PASS**
- Groups: 29 train / 9 validation / 9 test; **verified zero overlap** across all three pairs of splits. **PASS**
- Records 201+202 deliberately share `patient_201_202` group; 30 train records vs 29 train groups. **PASS**
- Notebook 02 cells 31/33/34 document `StratifiedGroupKFold` outer/inner splitting and print explicit overlap checks. **PASS**
- **FAIL (documentation):** `patient_independent_split_summary.csv` reports 59,743 / 19,540 / 22,168 beats, while processed arrays and `dataset_quality_report.csv` contain 59,720 / 19,530 / 22,156 (differences 23/10/12). The grouping-stage totals were not reconciled with post-extraction totals.

### 4. Class mapping and imbalance handling — PARTIAL

- `CLASS_TO_LABEL = {N:0, S:1, V:2, F:3}` in notebook 03 cell 14; `class_names` in notebooks 02/05/06; all 3 metadata CSVs verified with **0 mismatches**. **PASS**
- AAMI symbol groups documented in notebook 02 cell 22 (N:L,R,e,j / S:A,a,J,S / V:V,E / F:F; Q excluded). **PASS**
- Balanced class weights computed from `y_train`: `[0.281067, 7.632924, 3.533728, 35.547619]` (verified). **PASS**
- **FAIL (documentation):** these B3 class-weight values appear in **no** persistent config or report — only `clean_baseline_training_config.json` records `"class_weighting": "balanced"` for B0/B1. The extreme imbalance itself (F support 17 in validation) is visible only in evaluation per-class output.

### 5. Model architecture and training hyperparameters — PARTIAL

- B3 is `clone_model(b2_model)` with weights from `initial_B3_from_B2.keras` (notebook 07 cells 33/82/121/129). Architecture: Conv1D(32, k7) → residual blocks 32/64/128 (stride 2 on last two) → GAP → Dense 128 → Dropout 0.4 → Dense 4 softmax. **PASS**
- 194,020 parameters; input `(None,288,1)`; output `(None,4)`; layer `activation_6` used for CAM. **PASS**
- Loss = weighted sparse CE + 0.1 × differentiable-CAM consistency; fresh Adam(0.0001); batch 128; 467 batches; 10 planned epochs. **PASS**
- Filter parameters 0.5–40 Hz, 4th order, recorded in notebook 03 cell 11. **PASS**
- **FAIL (code defect in reusable module):** `src/ecg_qpain/preprocessing.py` referenced `LOWCUT`, `HIGHCUT`, `FILTER_ORDER` as undefined globals and imported `filtfilt` while calling `sosfiltfilt`. **FIXED** by adding the three constants to `config.py` and importing them, and correcting the scipy import. Verified `bandpass_filter()` now runs on a test signal.
- **FAIL (documentation):** the authoritative hyperparameters are not consolidated in one machine-readable config (see Task 1).

### 6. Checkpoint provenance and SHA256 documentation — PARTIAL

- `MIGRATION_MANIFEST.csv` contains full `sha256_before`/`sha256_after` for all 5 B3 `.keras` files (best, latest, initial, 2 backups). **PASS**
- `B3_TRAINING_RESUME_READINESS_REPORT.md` documents full SHA256, embedded `date_saved`, internal weight hashes and the reconstructed Epoch 4/5 timeline. **PASS**
- Validation evaluation **numerically confirmed** latest = Epoch 5 (0.3542619613487781) and best = Epoch 3 (0.3644898279927664). **PASS**
- Epoch 4 backups preserved and hashed. **PASS**
- **FAIL (governance):** provenance is distributed across several Markdown reports and a migration manifest; there is no single machine-readable **checkpoint registry** linking checkpoint ↔ epoch ↔ SHA256 ↔ timestamp ↔ validation score ↔ path.

### 7. Training history and evaluation report traceability — PARTIAL

- `reports/B3_training_history.csv`: 5 rows, epochs 1–5, with loss components, training time and `val_macro_f1`; epoch 3 best, epoch 5 latest. **PASS**
- `models/B3_CAM_Consistency/backups/history_epoch4_….csv`: epoch 1–4 snapshot. **PASS**
- Evaluation outputs: 12 timestamped CSVs in `reports/evaluation/` (clean/noisy summary, per-class, confusion matrices per checkpoint) plus a timestamped comparison Markdown. **PASS**
- **FAIL (traceability):** evaluation CSV filenames encode checkpoint *name* but not SHA256 or config version; a reader cannot prove which exact weights produced a given score from the CSV alone. Also no single machine-readable clean-vs-noisy comparison table.

### 8. Missing experiment metadata for a research paper — identified

Priority list (see recommendations):
1. Pinned dependency versions / lock file.
2. Corrected B3 config (seed, actual batch 128, class weights, filter params, noise seed, optimizer-reset note).
3. Checkpoint registry with SHA256 + epoch + score + timestamp.
4. Dataset citations, PhysioNet version and license.
5. Reconciliation of split-count discrepancy (23/10/12 beats).
6. Explicit statement that Epoch 5 was executed and Epoch 3 remains best; weight-only warm start for Epoch 6 (no optimizer state).
7. Hardware used for recorded training times (the ~55 min vs ~9.8 min epochs) — Colab hardware not documented.
8. Clarification that validation Macro-F1 is the mean over six fixed noisy conditions, and that F-class support is only 17.

### 9. Reproducibility checklist — PASS

`REPRODUCIBILITY_CHECKLIST.md` created with 40+ items across environment, data,
preprocessing/noise, model/training, provenance, evaluation and governance.

### 10. Separate audit report — PASS

This file. No original research artifact was modified.

---

## Additive changes made during this audit (all safe, no methodology change)

1. `src/ecg_qpain/config.py`: added `LOWCUT=0.5`, `HIGHCUT=40.0`, `FILTER_ORDER=4`.
2. `src/ecg_qpain/preprocessing.py`: imported those constants and fixed `filtfilt` → `sosfiltfilt`.
3. `train_b3_epoch6.py`: added `random.seed`, `np.random.seed`, `tf.random.set_seed` from `config.SEED` (2027).

After these changes, `compileall` succeeded, `bandpass_filter()` executed correctly,
and `train_b3_epoch6.py --smoke` passed all checks with official artifacts unchanged.

---

## Prioritized recommendations

**P0 — before any paper claim**
- Publish a corrected, machine-readable B3 experiment config (seed 2027, batch 128,
  lr 0.0001, λ 0.1, class weights, filter 0.5–40 Hz order 4, noise seed 2027,
  SNR sets, BW/MA channel 0, fresh Adam / no optimizer state).
- Create `checkpoint_registry.csv` with epoch, path, SHA256, date_saved, val Macro-F1,
  and role (latest/best/backup).
- Pin dependencies into a lock file.

**P1 — before final results**
- Reconcile the split-count discrepancy and document the reason (annotation filtering
  during beat extraction is the likely cause, but must be stated explicitly).
- Add dataset citations, PhysioNet release version and license.
- Extend evaluation CSVs with checkpoint SHA256 and config version columns; add a
  single clean-vs-noisy summary CSV.
- Document the hardware used for the original training runs.

**P2 — hygiene**
- Clarify that EM and powerline noise are configured but unused in B3.
- Note that `generate_powerline_noise` uses global RNG when `phase=None`.
- Keep the sealed test protocol: run exactly once with `--approved-test` only after
  final model selection.

---

## Remaining blockers

- No blocker to reproducibility documentation itself.
- Epoch 6 remains untrained by design; requires a suitable GPU.
- Full provenance and config gaps above are documentation issues, not numerical errors:
  all verified metrics, seeds, split separation and checkpoint identities passed.

## Integrity statement

No checkpoint, backup, dataset, notebook, historical CSV or existing report was
modified. All 30 non-notebook research files re-hashed after the audit: **0 changed**.
No training, promotion or test evaluation was performed.
