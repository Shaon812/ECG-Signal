# GPU_TRAINING_READINESS_AUDIT — B3 Epoch 6

Generated: 2026-11-22
Scope: read-only audit plus additive preparation files. No training, promotion,
test evaluation, dataset change or historical-result change.

---

## Summary

| # | Task | Status |
|---|---|---|
| 1 | Audit complete Epoch 6 workflow | **PASS** |
| 2 | Checkpoint loading compatibility (Keras 3.13.2 / 3.15.1) | **PASS** |
| 3 | TensorFlow GPU compatibility requirements | **PASS** (documented) |
| 4 | Suitable cloud GPU environment identified | **PASS** |
| 5 | Environment setup script prepared | **PASS** |
| 6 | Checkpoint transfer + SHA256 procedure prepared | **PASS** |
| 7 | Epoch 6 uses canonical B3 configuration | **FAIL → FIXED → PASS** |
| 8 | Staging-only output and commit safety | **PASS** |
| 9 | Exact GPU training/evaluation/promotion workflow documented | **PASS** |
| 10 | Pre-training checklist prepared | **PASS** |

---

## 1. Epoch 6 workflow audit — PASS

Reviewed `train_b3_epoch6.py` end-to-end:
`--smoke` (in-memory batch-4 step, no writes) → `--dry-run` (config print, no writes)
→ `--train` (full epoch, staging outputs) → external evaluation → `--commit`
(promotion with backups). Modes are mutually exclusive; `--commit` contains no
training call. Verified earlier: `--smoke` passed with all artifacts unchanged.

## 2. Checkpoint loading compatibility — PASS

- Both checkpoints embed `keras_version: 3.13.2` (`metadata.json`), saved
  2026-11-20@15:53:22 (best / Epoch 3) and 2026-11-21@16:49:15 (latest / Epoch 5).
- Loaded locally under TensorFlow 2.21.0 / Keras 3.15.1 with `compile=False`:
  both give `(None,288,1) → (None,4)`, 194,020 parameters.
- SHA256 of both files unchanged after loading.
- Conclusion: Keras 3.13.2 → 3.15.1 forward compatibility is verified for these
  artifacts. No checkpoint rewrite is needed or performed.

## 3. TensorFlow GPU compatibility — PASS

From the official TensorFlow GPU installation documentation (fetched 2026-11-22):
- TensorFlow ≥2.11 has **no GPU support on native Windows**; Linux or WSL2 is
  required (or the optional DirectML plugin, not recommended here).
- TF 2.21 supports Python 3.10–3.13; NVIDIA drivers ≥525.60.13 (Linux); GPU with
  CUDA compute capability ≥3.5; `pip install tensorflow[and-cuda]` installs bundled
  CUDA/cuDNN libraries.
- The historical T4 has compute capability 7.5 (verified in notebook output) — supported.
- Colab's `nvidia-smi` showed CUDA 13.0, whereas the generic docs cite CUDA 12.3;
  Colab manages this runtime itself. This is a managed-environment difference, not a
  project change. A GPU run must record its own resolved versions.

Local Windows machine: Intel i5-8265U, no NVIDIA GPU → **cannot** run Epoch 6.

## 4. Suitable cloud GPU environment — PASS

**Recommended: Google Colab with a T4 GPU runtime.** It is the same platform and GPU
class used for the original B3 runs (notebook 00: `GPU Name: Tesla T4`; notebook 07
`nvidia-smi`: Tesla T4 15 GB, driver 580.82.07, CUDA 13.0, TF 2.21.0). Use a Python
3.12 runtime, install `gpu_training/requirements_gpu.txt`, select GPU hardware
acceleration, and verify with `tf.config.list_physical_devices("GPU")` before training.

Other NVIDIA Linux environments with a supported GPU are technically viable, but
T4/Colab is the closest match to the historical setup and therefore the safest
choice for comparability. No unverified claims are made about specific quotas or
current hardware availability of any provider.

## 5. Environment setup script — PASS

New file `gpu_training/setup_gpu_environment.sh` (bash `-n` syntax verified) creates
`.venv_gpu`, installs pinned POSIX requirements, asserts Python 3.10–3.13, refuses to
continue if no GPU is visible, verifies checkpoint hashes and runs the two safe
preflight modes. It does not train or promote.
`gpu_training/requirements_gpu.txt` pins the top-level versions verified locally.
**Important:** `requirements.lock.txt` is Windows-specific (contains `pywinpty`) and
must not be used on Linux — this is stated in both files.

## 6. Checkpoint transfer and SHA256 verification — PASS

New files:
- `gpu_training/CHECKPOINT_TRANSFER_PROCEDURE.md` — copy-not-move rules, expected
  SHA256 table, mismatch handling, read-only load check.
- `gpu_training/verify_transfer.sh` (bash `-n` verified) — checks all five B3
  checkpoints against hashes from `reports/checkpoint_registry.csv`, exits non-zero
  on any mismatch or missing file.

## 7. Canonical configuration — FAIL → FIXED → PASS

**Finding:** `train_b3_epoch6.py` used hardcoded constants (128 / 0.0001 / 0.1) that
matched the canonical config, but **never read or verified** the canonical file. A
future edit could silently drift from the recorded configuration.

**Fix (additive):** added `CANONICAL_CONFIG` path and `verify_canonical_config()` to
the script, called at the start of `verify_preconditions()`. It asserts config
version, batch size, learning rate, λ, seed 2027, noise seed/types/SNRs, fresh-Adam
flag and bandpass parameters. `--dry-run` now prints 11 new PASS lines; the script
compiles and the guard behaves correctly. No methodology value was changed.

## 8. Staging-only output and commit safety — PASS

- `--train` writes only `epoch6_latest.keras`, `B3_training_history_epoch6.csv`, and
  optionally `epoch6_best_candidate.keras`; it contains no official-path writes.
- `--commit` re-verifies hashes and the 5-row history, requires a 6-row staged history,
  checks best-candidate presence against the score threshold, copies official files
  to `backups/*_pre_epoch6_<timestamp>.*` before any `os.replace`, and preserves
  `best_B3_resnet.keras` unless the score exceeds 0.3644898279927664.

## 9. Exact workflow — PASS

`gpu_training/GPU_TRAINING_WORKFLOW.md` documents: environment setup → verify transfer
→ safe preflight → `--train` → two `evaluate_b3.py` runs (noisy and `--clean`) → review
→ `--commit` only if justified. Test evaluation is explicitly excluded.

## 10. Pre-training checklist — PASS

`gpu_training/PRE_TRAINING_CHECKLIST.md` separates locally verified items from
GPU-machine items marked *(GPU)*, and ends with the exact start command.

---

## New files (all additive)

- `gpu_training/requirements_gpu.txt`
- `gpu_training/setup_gpu_environment.sh`
- `gpu_training/verify_transfer.sh`
- `gpu_training/CHECKPOINT_TRANSFER_PROCEDURE.md`
- `gpu_training/GPU_TRAINING_WORKFLOW.md`
- `gpu_training/PRE_TRAINING_CHECKLIST.md`
- `GPU_TRAINING_READINESS_AUDIT.md`

Modified (additive safety guard only): `train_b3_epoch6.py`.

## Exact requirements to start Epoch 6

1. A Linux GPU runtime (recommended: Colab + T4) with Python 3.10–3.13 and an
   NVIDIA GPU visible to TensorFlow; native Windows cannot be used.
2. Full project transferred to that environment; `bash gpu_training/verify_transfer.sh`
   must print PASS for all five checkpoints.
3. `bash gpu_training/setup_gpu_environment.sh` completed; `python train_b3_epoch6.py
   --dry-run` and `--smoke` passed on the GPU machine.
4. `reports/B3_training_history.csv` still has 5 rows ending at epoch 5.
5. Canonical config guard passes (11 PASS lines).
6. Human approval after the pre-training checklist, including the promotion decision
   rule (best preserved unless mean noisy Macro-F1 > 0.3644898279927664).
7. Then run exactly: `python train_b3_epoch6.py --train` — staging outputs only.

## Remaining blockers

- **No GPU on this laptop** — Epoch 6 cannot start locally.
- **No staged Epoch 6 checkpoint yet** — evaluation/promotion are future steps.
- Keras 3.13.2 (save) vs 3.15.1 (local) difference is verified harmless for loading;
  record the GPU environment's resolved versions after setup.

## Integrity statement

All 30 non-notebook research files remain byte-for-byte unchanged. No training,
promotion, test evaluation or dataset modification occurred during this audit.
