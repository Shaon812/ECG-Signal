# LOCAL_PIPELINE_SMOKE_TEST_REPORT

Generated: 2026-11-22
Project root: `C:\Users\Lenovo\Downloads\ECG_QPAIN_2027`

Constraints honoured: batch size **4** (and 4-beat noise batches), one dataset
split loaded at a time, no complete notebook execution, **no Epoch 5, no full
training epoch, no checkpoint overwrite, no history change, no dataset
regeneration, no methodology changes**. Free disk after tests: 4.74 GB.

---

## Summary

| # | Test | Result |
|---|------|--------|
| 1 | Dataset verification (3 splits, metadata, quality) | **PASS** |
| 2 | Noise loading + augmentation + SNR (batch 4) | **PASS** |
| 3 | B3 feature extractor / classifier head / differentiable CAM (batch 4) | **PASS** |
| 3b | Legacy `generate_gradcam()` helper | **NOT TESTED** (incompatible with saved single-output model; not used by B3 path) |
| 4 | Weighted CE / CAM consistency / total B3 loss | **PASS** |
| 5 | Single training step on temporary in-memory model | **PASS** |
| 6 | Notebook static compatibility (all 8) | **PASS** (1 optional missing module) |
| 6b | Full notebook execution | **NOT TESTED** (per instruction) |

---

## Task 1 — Dataset verification — PASS

**Test performed:** Loaded each `.npz` separately with NumPy; checked shapes,
dtypes, min/max, NaN/Inf counts, class distribution via `bincount`; cross-checked
row counts and class labels against the three `*_metadata.csv` files and
`reports/dataset_quality_report.csv`. Nothing was written.

**Actual output:**

| Split | X shape | X dtype | y shape | y dtype | NaN/Inf (X,y) | Class counts (N,S,V,F) |
|---|---|---|---|---|---|---|
| train | (59720, 288) | float32 | (59720,) | int64 | 0/0, 0/0 | 53119, 1956, 4225, 420 |
| validation | (19530, 288) | float32 | (19530,) | int64 | 0/0, 0/0 | 17533, 462, 1518, 17 |
| test | (22156, 288) | float32 | (22156,) | int64 | 0/0, 0/0 | 19936, 363, 1492, 365 |

X ranges: train [-3.102609, 3.522208], val [-3.570740, 4.052188], test
[-3.177569, 3.328317]. All metadata CSV row counts and class tallies match the
arrays exactly; split labels are consistent (`Train` / `Validation` / `Test`).
Counts match `dataset_quality_report.csv` exactly.

**Error:** none.

**Notes / recommended correction:**
- The arrays are **2-D `(N, 288)`**, while the saved model declares input
  `(None, 288, 1)`. The earlier prediction test still succeeded, but for exact
  shape fidelity, feed `X[..., None]` (this was done in Tasks 3–5).
- `reports/patient_independent_split_summary.csv` lists 59743/19540/22168 beats,
  slightly higher than the final arrays (59720/19530/22156). This is a
  pre-existing artifact from the grouping stage; the processed arrays and the
  quality report agree. No correction made.

---

## Task 2 — Noise pipeline — PASS

**Test performed:** Loaded `bw`, `ma`, `em` from the original NSTDB directory with
`wfdb.rdsamp` (read-only); injected the notebook globals `noise_signals` and the
`split_ranges` from `reports/noise_generation_config.json`; called
`extract_noise_segment(seed=42)` for 3 noise types × 3 splits; verified
`add_noise_at_snr` achieved SNR at 24/18/12/6 dB on a 4-beat batch; verified
`add_powerline_noise` at 50/60 Hz; verified TF `augment_training_beat` and
`add_validation_noise` on a batch of 4.

**Actual output:**
- BW/MA/EM: shape `(650000, 2)`, dtype float64, fs 360, channels `noise1/noise2`, NaN=0, Inf=0 — matches `noise_record_audit.csv`.
- All 9 `extract_noise_segment` cases: shape `(288,)`, finite, start indices inside configured ranges (train 34782, validation 401577, test 531577).
- `add_noise_at_snr`: target 24/18/12/6 dB → achieved 24.000/18.000/12.000/6.000 dB (error 0.0000 dB); 4-beat batch `(4, 288)`, all finite.
- `add_powerline_noise`: 50 Hz and 60 Hz → 12.000 dB, all finite.
- `augment_training_beat` 4 samples → `(288, 1)`, all finite; `add_validation_noise` → `(288,)`, finite.

**Error:** none.

**Recommended correction:** none. Noise files and experimental config untouched.

---

## Task 3 — B3 CAM pipeline — PASS (legacy helper: NOT TESTED)

**Test performed:** Loaded `latest_B3_resnet.keras`; built feature extractor and
classifier head with the original `create_cam_components` helper (layer
`activation_6`); ran `differentiable_cam_for_model` on X `(4, 288, 1)` and y `(4,)`;
checked CAM/prediction shapes, finiteness, softmax row sums; explicitly computed
gradients of the target-class score w.r.t. features.

**Actual output:**
- Model I/O `(None, 288, 1) → (None, 4)`, 194020 params; `activation_6` present.
- Feature extractor `(None, 288, 1) → (None, 72, 128)`; classifier head `(None, 72, 128) → (None, 4)`.
- CAM output `(4, 288)` float32, all finite, range [0.0, 0.9908].
- Predictions `(4, 4)`, all finite, row sums exactly 1.0.
- Gradients w.r.t. features: **present**, shape `(4, 72, 128)`, all finite.

**Error (only for legacy helper):** `generate_gradcam(model, x[0])` raised
`ValueError: not enough values to unpack (expected 2, got 1)`.

**Recommended correction:** `generate_gradcam()` expects a **two-output** model
returning `(conv_outputs, predictions)`, but the saved B3 checkpoint is a
single-output classifier. This helper is a legacy artifact and is **not used by
the B3 training path**, which uses `differentiable_cam_for_model()`. No change
made; if needed, rewire it to use `create_cam_components()` instead of unpacking
model outputs.

---

## Task 4 — B3 loss pipeline — PASS

**Test performed:** Read original `B3_B4_experiment_config.json` (lr 0.0001,
λ_CAM 0.1), computed balanced class weights from `y_train` exactly as notebook 07
does, built noisy batch at 12 dB, ran `weighted_ce_loss`,
`cam_consistency_loss`, and `calculate_b3_loss` (plus `calculate_b4_loss`
informationally) on a batch of 4.

**Actual output:**
- Class weights `[0.281067, 7.632924, 3.533728, 35.547619]`.
- weighted CE (clean) = 0.01221825; (noisy) = 0.01754732.
- CAM consistency loss = 0.00045350.
- B3 total = 0.01492813; CE = 0.01488278; CAM = 0.00045350 — all finite.
- Reconciliation `CE + 0.1 × CAM = 0.01492813` matches total (diff 2.91e-11).
- B4 gated total (informational) = 0.01491301, finite.

**Error:** none.

**Recommended correction:** none. Config values and methodology unchanged.

---

## Task 5 — Single training-step validation — PASS

**Test performed:** Cloned the B3 model **in memory** (`clone_model` +
`set_weights`), created a **fresh temporary Adam optimizer** (lr 0.0001), set
temporary CAM module globals, ran **exactly one** `train_b3_step` on a 4-beat
validation batch. Hash-checked both B3 checkpoints and the history CSV before
and after.

**Actual output:**
- Temp clone 194020 params, `activation_6` present; noise bank `(2, 650000)`.
- `total_loss = 0.01550722`, `ce_loss = 0.01503754`, `cam_loss = 0.00469685` — all finite.
- 31/31 trainable variables changed; temp optimizer iterations = **1**.
- Checkpoint hashes unchanged (`latest_B3`, `best_B3`); `B3_training_history.csv` unchanged, still **5 rows**.

**Error encountered and resolved (test harness only):**
1. `TypeError: too many positional arguments` from `compute_class_weight` —
   scikit-learn 1.9.1 requires keyword arguments. The notebooks already use
   keywords, so they are unaffected; my test script was corrected.
2. `NameError: name 'TRAIN_START' is not defined` when calling
   `cam.train_b3_step` from the reusable module. This was a **migration bug I
   introduced** in `src/ecg_qpain/cam.py`: it used notebook globals
   `TRAIN_START/TRAIN_END/BEAT_LENGTH/TRAIN_SNRS` without importing them.
   I added the missing `from .config import ...` line (no methodology change) and
   re-ran the test successfully.

**Recommended correction:** none remaining. All heavy runtime objects
(`b3_model`, optimizer, feature extractor, classifier head, class weights, noise
bank) are supplied by the notebook at runtime by design; the reusable module
documents this.

---

## Task 6 — Notebook compatibility — PASS (static analysis only)

**Test performed:** Parsed every code cell of all 8 notebooks (105+ cells each
where applicable), collected imports and defined names in order, checked for
undefined names, Colab artifacts, absolute Windows paths, missing modules, and
existence of all referenced data/model/report files. Did **not** execute any
notebook.

**Actual output:**
- All 8 notebooks: **0** Colab artifacts (`google.colab`, `/content`, `drive.mount`, `!pip`, `%pip`) in source.
- 0 absolute Windows paths (the 4 regex hits were false positives such as `start:start` and literal `\n`).
- 0 possible undefined variables.
- Parse errors: notebook 07 has **2 pre-existing fragment cells** (unchanged from before migration); all other notebooks 0.
- Missing third-party module: **`torch`** only (notebook 00 smoke test; commented out in `requirements.txt`).
- All 17 referenced data/model/report paths exist.
- Aggregate missing modules: `['torch']`.

**Error:** none from the notebooks themselves.

**Recommended correction:** install a CPU-only `torch` build only if you intend
to run notebook 00's version-print cell; it is not required for notebooks 01–07.

**Not tested:** full notebook execution (explicitly excluded).

---

## Task 7 — Integrity / final state

- All 30 non-notebook research files re-hashed: **0 changed**.
- Both B3 checkpoints and `B3_training_history.csv` unchanged after all tests.
- Epoch 5 was **not** started; no new epoch, no history append, no checkpoint write.
- One source file was corrected: `src/ecg_qpain/cam.py` (missing config imports — see Task 5). This is a migration-created module, not an original research file.

## Overall conclusion

The complete local B3 pipeline is functional on CPU with batch-4 smoke tests:
data loads cleanly, noise/SNR math is exact, CAM and gradients are finite, losses
reconcile with the original λ=0.1 configuration, and a single training step
updates a temporary model without touching official artifacts. The only gaps are
the optional `torch` package (notebook 00) and the legacy two-output
`generate_gradcam()` helper, neither of which affects B3 training or inference.
