# ECG QPAIN 2027 — reproducibility checklist

Use this checklist before claiming a result is reproducible. Item status reflects
the audit in `RESEARCH_REPRODUCIBILITY_AUDIT.md` (2026-11-22).

## A. Environment

- [x] Python version recorded: 3.12.16 (`LOCAL_ENVIRONMENT_REPORT.md`)
- [x] TensorFlow version recorded: 2.21.0; Keras 3.15.1; NumPy 2.5.5
- [x] Hardware recorded: i5-8265U, 8 GB RAM, no GPU (CPU-only)
- [x] Isolated `.venv` at project root
- [ ] **Pinned dependency lock file** — `requirements.txt` is unpinned; no lock file exists
- [x] VS Code interpreter and Jupyter kernel documented (`.vscode/`, `EPOCH6_SETUP.md`)

## B. Data and splits

- [x] Raw datasets identified: MITDB 1.0.0, NSTDB 1.0.0 (zip + extracted)
- [x] Processed arrays verified: 59,720 / 19,530 / 22,156 beats, 288 samples, 360 Hz
- [x] No NaN/Inf in any split (`dataset_quality_report.csv`)
- [x] Patient-independent grouping: 29 train / 9 validation / 9 test groups
- [x] Groups are **disjoint** across all splits (verified from `patient_group_split.csv`)
- [x] Records 201+202 deliberately grouped as one patient (`patient_201_202`)
- [x] Class mapping documented: N=0, S=1, V=2, F=3 (notebook 03 cell 14; metadata verified)
- [ ] **Reconcile split-count discrepancy**: split summary 59,743/19,540/22,168 vs
      processed arrays 59,720/19,530/22,156 (23/10/12 beats)
- [ ] **Dataset citations / license / PhysioNet version** not recorded in README

## C. Preprocessing and noise

- [x] Channel selection per record recorded (`ecg_channel_audit.csv`)
- [x] Bandpass parameters explicit: 0.5–40 Hz, 4th order (notebook 03 cell 11)
- [x] Beat length 288 samples (0.8 s at 360 Hz), recorded in config/report
- [x] Noise records BW/MA/EM from NSTDB; statistics recorded (`noise_statistics.csv`)
- [x] Noise split regions explicit: train 0–390k, val 390k–520k, test 520k–650k
- [x] Training SNRs [24,18,12,6]; validation SNRs [18,12,6]
- [x] Noise seed 2027 for validation set (notebook 07; `train_b3_epoch6.py`; `evaluate_b3.py`)
- [ ] **Noise seed not recorded in `noise_generation_config.json`**
- [ ] Scope clarification: config lists EM and 50/60 Hz powerline noise, but B3 training uses only BW/MA channel 0

## D. Model and training

- [x] Architecture: ResNet (Conv1D 32/64/128 residual blocks, GAP, Dense 128, Dropout 0.4, softmax 4)
- [x] B3 = clone of B2 + weights from `initial_B3_from_B2.keras`
- [x] Parameters: 194,020; input `(None,288,1)`; output `(None,4)`
- [x] Loss: weighted sparse CE + 0.1 × CAM consistency
- [x] Class weights: balanced, from `y_train` = `[0.281067, 7.632924, 3.533728, 35.547619]`
- [x] Learning rate 0.0001; fresh Adam (no saved optimizer state)
- [x] Batch size actually used: **128** (467 batches); config JSON says 32 — stale
- [x] Total planned epochs 10; completed epochs 5 (history)
- [x] Global seeds 2027 in notebooks 05/06/07 and Epoch 6 script (after audit fix)
- [x] `tf.data` shuffle buffer 10,000 with op-level seed 2027
- [ ] **B3 config JSON lacks seed, class weights, actual batch size, filter and noise-seed metadata**

## E. Checkpoints and provenance

- [x] All B3/B4/B2/B1/B0 checkpoints hashed in `MIGRATION_MANIFEST.csv`
- [x] `latest_B3_resnet.keras` = Epoch 5 (SHA256 `f26d0a5f…`), verified by exact
      reproduction of 0.3542619613487781
- [x] `best_B3_resnet.keras` = Epoch 3 (SHA256 `610caade…`), verified by exact
      reproduction of 0.3644898279927664
- [x] Epoch 4 backups preserved with timestamps and hashes
- [x] Embedded `date_saved` metadata and internal weight hashes analysed
- [ ] **Single machine-readable checkpoint registry** (epoch ↔ SHA ↔ timestamp ↔ score) not present;
      provenance is spread across several Markdown reports

## F. Evaluation and reporting

- [x] Six noisy conditions BW/MA × 18/12/6 dB, fixed seed 2027
- [x] Mean noisy Macro-F1 computed as unweighted mean over six conditions
- [x] Clean and noisy evaluations saved separately with timestamps
- [x] Full metric set: accuracy, macro P/R/F1, weighted F1, per-class P/R/F1/support, confusion matrices
- [x] Patient-independent test split remains sealed; no test evaluation run
- [x] `evaluate_b3.py` refuses test evaluation without `--approved-test`
- [ ] **Evaluation CSVs do not record checkpoint SHA256 or config version**
- [ ] **No unified clean-vs-noisy comparison table in a single machine-readable file**

## G. Governance

- [x] No training, no promotion, no test evaluation performed during audits
- [x] All 30 non-notebook research files verified unchanged after every audit
- [x] Original notebooks preserved; path porting verified
- [x] Staged Epoch 6 workflow documented (`B3_EPOCH6_WORKFLOW.md`)
- [ ] Epoch 6 not yet executed (correct — awaiting suitable GPU)

---

## Minimum requirements before paper submission

1. Produce a pinned environment lock file and record exact package versions.
2. Create a machine-readable checkpoint registry and evaluation provenance columns.
3. Publish the corrected/annotated experiment config (seed, batch 128, class weights,
   filter params, noise seed, scope).
4. Reconcile or explain the split-count discrepancy.
5. Add dataset citations, version and license.
6. Run the sealed test evaluation exactly once, after final model selection, with
   the explicit `--approved-test` flag and a new timestamped report.
