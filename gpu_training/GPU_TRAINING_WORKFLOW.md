# Exact Epoch 6 GPU workflow (train → evaluate → review → commit)

All commands are run on the **GPU machine** from the project root. Nothing here
starts training until step 4.

## 0. Prerequisites

- Linux / Colab GPU runtime, Python 3.10–3.13, NVIDIA GPU supported by TensorFlow
  (Tesla T4, compute capability 7.5, is the verified historical device).
- Full project copied as described in `CHECKPOINT_TRANSFER_PROCEDURE.md`.
- Pre-training checklist completed (`PRE_TRAINING_CHECKLIST.md`).

## 1. Environment

```bash
bash gpu_training/setup_gpu_environment.sh
# activates .venv_gpu, installs pinned Linux requirements, verifies GPU,
# verifies all checkpoint hashes, runs --dry-run and --smoke (no writes)
```

If using an already-prepared environment, run only:

```bash
source .venv_gpu/bin/activate
bash gpu_training/verify_transfer.sh
python train_b3_epoch6.py --dry-run
python train_b3_epoch6.py --smoke
```

## 2. Confirm start state

```bash
cat reports/checkpoint_registry.csv
cat reports/B3_training_config_canonical.json
cat reports/B3_training_history.csv   # must still have 5 rows, last epoch 5
```

## 3. (Already done locally) Safe preflight

The two safe modes were executed on Windows and passed; repeat them on the GPU
machine after transfer because driver/kernel differences can matter.

## 4. Train Epoch 6 — STAGING ONLY

```bash
python train_b3_epoch6.py --train
```

Writes only:
- `models/B3_CAM_Consistency/epoch6_latest.keras`
- `reports/B3_training_history_epoch6.csv`
- `models/B3_CAM_Consistency/epoch6_best_candidate.keras` (only if improved)

Official checkpoints, Epoch 4 backups and `B3_training_history.csv` are untouched.
GPU-less machines are refused unless `--allow-cpu` is passed (not recommended).

## 5. Evaluate the staged checkpoint (validation only)

```bash
python evaluate_b3.py --checkpoint models/B3_CAM_Consistency/epoch6_latest.keras
python evaluate_b3.py --clean --checkpoint models/B3_CAM_Consistency/epoch6_latest.keras
```

Both write new timestamped CSVs in `reports/evaluation/` with `checkpoint_sha256`
and `config_version` columns. **Do not use `--split test` or `--approved-test`.**

## 6. Review

- Read `MEAN_NOISY_6_CONDITIONS` Macro-F1 from the staged summary.
- Compare with the historical best **0.3644898279927664**.
- Inspect per-condition and clean summaries; confirm finite, plausible values.
- If a new-best candidate exists, evaluate it the same way before promotion.
- If results are anomalous, stop and keep staging files; do not commit.

## 7. Promote only if justified

```bash
python train_b3_epoch6.py --commit
```

`--commit` (no training) re-verifies all hashes and the 5-row official history,
requires the staged history to have 6 rows, checks that the best-candidate file
presence matches the score threshold, creates timestamped backups of all official
files, and only then atomically promotes. It preserves `best_B3_resnet.keras`
when the new mean noisy Macro-F1 is not above 0.3644898279927664.

## 8. After promotion

Re-run the reporting steps on the GPU machine if desired, and copy new reports back
to the Windows project using the same transfer/verify discipline. **Do not** modify
any pre-existing historical result file.
