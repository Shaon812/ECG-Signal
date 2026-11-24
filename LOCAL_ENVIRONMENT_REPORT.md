# LOCAL_ENVIRONMENT_REPORT

Generated: 2026-11-22
Project root: `C:\Users\Lenovo\Downloads\ECG_QPAIN_2027`

Scope: local environment setup, dependency verification, path verification and
read-only model recovery. **No training, dataset regeneration, checkpoint
overwriting, history modification or destructive file operations were performed.**

---

## 1. Hardware information

| Item | Value |
|---|---|
| OS | Microsoft Windows 11 Pro, version 10.0.26300 (build 26300), 64-bit |
| PowerShell | 5.1.26100.10068 |
| CPU | Intel(R) Core(TM) i5-8265U @ 1.60 GHz (max 1.80 GHz) |
| CPU cores / threads | 4 physical / 8 logical |
| RAM | 7.79 GB total (≈1.7 GB free at initial inspection) |
| Disk C: | 101.21 GB total; 7.19 GB free before setup, **4.78 GB free after** |
| Graphics | Intel(R) UHD Graphics 620 (driver 31.0.101.2137) |
| NVIDIA GPU | **None** — `nvidia-smi` not present, no NVIDIA device in WMI |
| CUDA / cuDNN | Not installed / not applicable (no NVIDIA GPU) |

## 2. Python version

- System Python: **3.15.2** (`C:\Python315\python.exe`), also 3.14.3 installed —
  **neither has TensorFlow wheels on Windows**, so neither could be used.
- Action taken (additive only): installed a managed **CPython 3.12.16** via `uv`
  under `%APPDATA%\uv\python`, and created the isolated virtual environment:
  `C:\Users\Lenovo\Downloads\ECG_QPAIN_2027\.venv` (Python 3.12.16).
- No system Python was changed, upgraded or removed. `uv` 0.13.9 was added to the
  user site of Python 3.15 as a provisioning tool.

## 3. TensorFlow version

- **TensorFlow 2.21.0** (Keras 3.15.1, protobuf 7.36.2), installed from PyPI.
- TensorFlow 2.21 provides Windows wheels for CPython 3.10–3.13, which is why
  Python 3.12 was selected.

## 4. Installed dependencies

Verified by direct import in `.venv`:

| Package | Version | Status |
|---|---|---|
| tensorflow | 2.21.0 | OK |
| keras | 3.15.1 | OK |
| numpy | 2.5.5 | OK |
| pandas | 3.1.1 | OK |
| scipy | 1.18.1 | OK |
| scikit-learn | 1.9.1 | OK |
| matplotlib | 3.11.2 | OK |
| seaborn | 0.13.2 | OK |
| wfdb | 4.3.1 | OK |
| tqdm | 4.70.1 | OK |
| jupyter | 1.1.1 | OK |
| ipykernel | 7.4.0 | OK |
| ipython | 9.18.1 | OK |
| notebook | 7.6.5 | OK |

## 5. GPU / CPU execution status

- Execution is **CPU-only**. TensorFlow reports zero physical GPU devices:
  `GPU devices: []`.
- TensorFlow also warns that native Windows builds (≥2.11) do not support CUDA
  GPU execution; GPU use would require WSL2 or the TensorFlow-DirectML plugin.
  With no NVIDIA hardware present, neither route is currently beneficial.
- A CPU instruction warning was emitted: the binary suggests it was not built
  with SSE3/SSE4.1/SSE4.2/AVX/AVX2/FMA enabled. This affects training speed only,
  not correctness. Full training on this 4-core CPU should be expected to be slow
  (the recorded B3 epochs took ~55 min each in Colab).

## 6. VS Code configuration

| Check | Result |
|---|---|
| VS Code version | 1.147.0 (x64) |
| Extensions | `ms-python.python`, `ms-python.vscode-pylance`, `ms-toolsai.jupyter`, `ms-python.debugpy`, `ms-python.vscode-python-envs` — installed |
| Interpreter setting | `.vscode/settings.json` → `${workspaceFolder}/.venv/Scripts/python.exe` — resolves correctly |
| Notebook kernel | Registered `ecg-qpain-312` ("Python 3.12 (ECG_QPAIN_2027 .venv)") inside `.venv/share/jupyter/kernels/`; discovered by `jupyter_client` |
| Kernel smoke test | Kernel started, executed imports and path checks; reported venv Python 3.12.16, TF 2.21.0, correct project root — **OK** |
| Integrated terminal | PowerShell 5.1; all commands in this report were run through it |
| Project root resolution | `src/ecg_qpain/paths.py` resolves to the project root both from the project root and from an unrelated CWD (`C:\`) — **OK** |

> In VS Code, select kernel **"Python 3.12 (ECG_QPAIN_2027 .venv)"** when opening
> a notebook. The pre-existing `python3` kernel points to Python 3.14 and lacks
> these packages; it is not a valid kernel for this project.

## 7. Dataset path verification

All checked paths exist and resolve on Windows (from both project root and `C:\`):

| Path | Status |
|---|---|
| `data/raw/mitdb/` | OK |
| `data/raw/nstdb/` | OK |
| `data/processed/` | OK (3 `.npz` + 3 metadata CSVs, sizes unchanged) |
| `models/` | OK |
| `reports/` | OK |
| `src/ecg_qpain/` | OK |
| MITDB / NSTDB extracted directories | OK |

## 8. Model loading verification

Read-only recovery test (checkpoints hashed before and after):

| Check | Result |
|---|---|
| `latest_B3_resnet.keras` | Loaded OK |
| `best_B3_resnet.keras` | Loaded OK |
| Input shape | `(None, 288, 1)` for both |
| Output shape | `(None, 4)` for both |
| Parameters | 194,020 for both |
| Layers | 33 for both |
| Prediction test | 32 beats from `validation_beats.npz` → output `(32, 4)`, rows sum to 1.0 — OK |
| Checkpoint integrity | SHA256 unchanged for both files (`f26d0a5f…`, `610caade…`) |

TensorFlow/Keras 3.15 loads these Keras-v3 files without custom objects (`compile=False`).

## 9. Notebook compatibility

| Notebook | Cells | Runtime dependencies | Status |
|---|---|---|---|
| 00 Colab setup / smoke test | 8 | `torch` (optional), numpy, pandas, scipy, sklearn, matplotlib, wfdb | All present **except `torch`** |
| 01 PhysioNet download / audit | 25 | wfdb, pandas | OK |
| 02 Patient grouping / AAMI | 42 | wfdb, numpy, pandas, sklearn | OK |
| 03 Preprocessing / beat extraction | 26 | wfdb, numpy, pandas, scipy, matplotlib, tqdm | OK |
| 04 Noise generation / SNR | 39 | wfdb, numpy, pandas, matplotlib, tqdm | OK |
| 05 Clean baselines | 26 | tensorflow, numpy, pandas, sklearn, matplotlib | OK |
| 06 Noise-augmented ResNet | 28 | tensorflow, numpy, pandas, sklearn, matplotlib, seaborn, wfdb | OK |
| 07 CAM consistency | 180 | tensorflow, numpy, pandas, sklearn, matplotlib, wfdb, datetime, shutil | OK |

Additional checks:

- **Zero** residual Colab setup lines (`/content`, `google.colab`, `drive.mount`,
  `!pip`) in notebook source across all eight notebooks.
- No complete pipeline was executed; only environment/import checks and one
  isolated kernel smoke test were run.
- Notebook 07 has **2 pre-existing cells** that are code fragments and do not
  parse standalone. This was already true before the migration; no new syntax
  errors were introduced.
- Notebook 07 contains a recovery cell with `assert completed_epochs == 3`.
  With the current 5-row `B3_training_history.csv`, that assertion would fail.
  This is the documented B3 Epoch-4/Epoch-5 discrepancy — no history was changed.
- **Epoch 5 was not started.**

## 10. Remaining problems / notes

1. **No GPU.** CPU-only execution; full training will be substantially slower
   than the original Colab runs. No action taken (no NVIDIA hardware).
2. **Python version change was required.** System Python 3.15/3.14 cannot run
   TensorFlow. An isolated Python 3.12.16 + `.venv` was provisioned; nothing
   system-wide was replaced. If you require a different TF version, select a
   compatible Python first (TF 2.21 supports 3.10–3.13 on Windows).
3. **`torch` is not installed** (optional, notebook 00 smoke test only; commented
   out in `requirements.txt`). Notebook 00's import cell will fail unless you
   install a CPU torch build. Left uninstalled to avoid a large, unnecessary
   download on a nearly-full disk.
4. **Disk space is now 4.78 GB free.** Adequate for normal use, but limited for
   additional large packages or regenerating processed data.
5. **PowerShell reports "exit code 1" for some Python commands** because native
   processes write warnings (oneDNN, absl) to stderr; this is benign — the Python
   scripts completed successfully and printed all expected results.
6. **Stored notebook outputs still show historical Colab paths.** These are
   preserved research artifacts, not runtime dependencies.
7. **B3 state unchanged:** latest/best checkpoints and training history remain
   byte-for-byte as found; see `README.md` §5 for the Epoch-4/Epoch-5 discrepancy.

---

### Integrity summary

- 38 pre-migration research files were re-hashed: the 30 non-notebook files
  (datasets metadata, reports and all checkpoints) are **unchanged**; the only
  differences are the 8 notebooks intentionally path-ported during migration.
- No model files, datasets, backups or history files were modified in this phase.
