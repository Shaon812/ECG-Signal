# ECG_QPAIN_2027

Local, portable research environment for ECG arrhythmia classification under noise,
using MIT-BIH Arrhythmia DB (MITDB), MIT-BIH Noise Stress Test DB (NSTDB),
patient-independent splits, CNN/ResNet baselines, noise augmentation, and
CAM-consistency / gated CAM-consistency training.

This project was migrated from Google Colab / Google Drive. **No Google Colab or
Google Drive access is required for local execution.**

---

## 1. Open in VS Code

1. Open this folder (`ECG_QPAIN_2027`) as the workspace root.
2. Install the recommended extensions (Python, Jupyter, Pylance) when prompted.
3. Create an environment and install dependencies **from the project root**:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

   TensorFlow on Windows needs Python 3.10–3.12. Use that interpreter for
   notebooks 05–07. Select it in VS Code: *Python: Select Interpreter*.

4. Run all notebooks with the working directory set to the project root.
   Each notebook injects a portable path bootstrap that resolves the project
   root from `src/ecg_qpain/paths.py`, so no path edits are needed.

---

## 2. Pipeline (original execution order preserved)

| # | Notebook | Purpose | Key outputs |
|---|----------|---------|-------------|
| 00 | `00_Colab_Setup_and_Data_Smoke_Test.ipynb` | Environment/setup smoke test | `reports/environment.json` (when run) |
| 01 | `01_PhysioNet_Download_and_Data_Audit.ipynb` | Download/extract MITDB + NSTDB, audit | `reports/mitdb_audit.csv`, `reports/nstdb_audit.csv` |
| 02 | `02_Patient_Grouping_AAMI_Classification.ipynb` | AAMI mapping, patient-independent splits | `reports/aami_*.csv`, `reports/patient_*.csv`, `reports/record_split_assignment.csv` |
| 03 | `03_ECG_Preprocessing_Beat_Extraction.ipynb` | Channel selection, bandpass, beat extraction | `data/processed/{train,validation,test}_beats.npz` + `*_metadata.csv`, `reports/ecg_channel_audit.csv`, `reports/dataset_quality_report.csv` |
| 04 | `04_ECG_Noise_Generation_and_SNR.ipynb` | Noise/SNR definitions and statistics | `reports/noise_*.csv`, `reports/noise_generation_config.json` |
| 05 | `05_CNN_ResNet_Clean_Baselines.ipynb` | Clean B0 CNN / B1 ResNet | `models/B0_CNN_Clean.keras`, `models/B1_ResNet_Clean.keras`, `reports/clean_baseline_*` |
| 06 | `06_Noise_Augmented_ResNet.ipynb` | Noise-augmented B2 ResNet | `models/B2_Noise_Augmented_ResNet/best_B2_resnet.keras`, `reports/B2_*` |
| 07 | `07_CAM_Consistency_Models.ipynb` | B3 CAM consistency / B4 gated CAM | `models/B3_CAM_Consistency/*`, `models/B4_Gated_CAM_Consistency/*`, `reports/B3_training_history.csv`, `reports/B3_B4_experiment_config.json` |

Dependency chain: `00 → 01 → 02 → 03 → 04 → 05 → 06 → 07`.
Notebook 07 requires the B2 checkpoint from notebook 06. The existing processed
data, checkpoints, and reports are already present, so notebooks can be inspected
or re-run individually. **No training is started by this migration.**

---

## 3. Data inventory

- `data/raw/mitdb/` — MIT-BIH Arrhythmia DB (zip + extracted records, `mitdbdir/`, `x_mitdb/`).
- `data/raw/nstdb/` — Noise Stress Test DB (zip + extracted `bw/ma/em` noise,
  `118e*/119e*` noisy records, `old/`).
- `data/processed/` — `train_beats.npz` (59,720 beats), `validation_beats.npz`
  (19,530), `test_beats.npz` (22,156); each with `X.npy`/`y.npy`, length 288,
  360 Hz, plus `*_metadata.csv`. No separate noise files: noise is generated
  on the fly from NSTDB during notebooks 06/07.
- `models/` — B0, B1, B2, B3 (incl. `backups/`), B4 checkpoints.
- `reports/` — audit, split, configuration, and results tables (CSV/JSON).

---

## 4. Reusable modules (`src/ecg_qpain/`)

| Module | Contents | Origin |
|--------|----------|--------|
| `paths.py` | Portable project-root and directory constants | new (migration) |
| `config.py` | Seeds, shapes, SNRs, lambdas, split ranges | values from `reports/*.json` |
| `preprocessing.py` | `select_ecg_channel`, `bandpass_filter`, plotting | notebook 03 |
| `noise.py` | noise generation, SNR mixing, augmentation | notebooks 04/06/07 |
| `models.py` | `build_cnn_model`, `residual_block`, `build_resnet_model` | notebook 05 |
| `cam.py` | Grad-CAM, differentiable CAM, losses, training/eval steps | notebook 07 |

Functions are copied verbatim. The notebooks remain self-contained and are the
source of truth for the research methodology; import these modules only if you
want to reuse individual helpers elsewhere.

---

## 5. B3 checkpoint / training state (important)

Intended research state (per project specification):

- **Latest B3:** Epoch 4
- **Best B3:** Epoch 3
- **Best validation Macro-F1:** `0.3644898279927664` (Epoch 3)
- **Next intended training:** Epoch 5

Verification performed during migration:

- `models/B3_CAM_Consistency/backups/history_epoch4_20261121_163837.csv`
  contains exactly epochs 1–4, with the best Macro-F1 at epoch 3.
- `models/B3_CAM_Consistency/best_B3_resnet.keras` is byte-identical to
  `backups/best_epoch4_20261121_163837.keras` (epoch-3 weights). ✓
- `models/B3_CAM_Consistency/backups/latest_epoch4_20261121_163837.keras`
  is the epoch-4 "latest" snapshot (SHA256 `72250259…`).
- **However:** `reports/B3_training_history.csv` contains an additional 5th row
  (epoch 5, Macro-F1 `0.3542619613487781`), and the current
  `latest_B3_resnet.keras` has a different SHA256 (`F26D0A5F…`) than the
  epoch-4 backup. Notebook 07 also contains a "STEP 41: B3 EPOCH 5 TRAINING"
  cell. This indicates Epoch 5 was executed after the epoch-4 backup.

**Migration decision:** all checkpoints and history files were left
**byte-for-byte unchanged** and documented here (no research state was altered,
and no training was run). If you want the on-disk state restored to the
epoch-4 snapshot, do so explicitly and keep an archive of the current files.

> Caveat when re-running notebook 07: its recovery section contains
> `assert completed_epochs == 3`, which will fail against the current 5-row
> `B3_training_history.csv`. This is a pre-existing research artifact, not a
> migration change.

---

## 6. Verification summary

- Backup created before any change at
  `C:\Users\Lenovo\Downloads\ECG_QPAIN_2027_BACKUP_20261121_234617`
  (8 notebooks + `reports/` + `models/`, 38 files; datasets were not duplicated).
- All 8 notebooks: cell count, order, types, execution counts, and stored outputs
  identical to the backup; only setup/path cells changed. No `/content`,
  `google.colab`, `drive.mount`, or `!pip` remains in notebook source.
- All `src/ecg_qpain/*.py` modules compile successfully; `paths.py` resolves to
  this project root on Windows.
- Full file-level verification is recorded in `MIGRATION_MANIFEST.csv`.
