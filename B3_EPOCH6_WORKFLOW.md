# B3 Epoch 6 — exact future workflow

This document defines the only supported order of operations. Run everything from
the project root with `.venv` active:

```powershell
.\.venv\Scripts\Activate.ps1
```

**Confirmed reference state**

| Item | Value |
|---|---|
| Start weights | `latest_B3_resnet.keras` = Epoch 5 (SHA256 `f26d0a5f…`) |
| Best checkpoint | `best_B3_resnet.keras` = Epoch 3 (SHA256 `610caade…`) |
| Historical best mean noisy Macro-F1 | `0.3644898279927664` |
| Epoch 5 mean noisy Macro-F1 | `0.3542619613487781` |

---

## Step 0 — Safe preflight (no writes)

```powershell
python train_b3_epoch6.py --smoke
python train_b3_epoch6.py --dry-run
```

Both must print all PASS lines. They never write files.

## Step 1 — Train Epoch 6 on a suitable GPU (staging only)

```powershell
python train_b3_epoch6.py --train
```

Writes **only**:
- `models/B3_CAM_Consistency/epoch6_latest.keras`
- `reports/B3_training_history_epoch6.csv`
- `models/B3_CAM_Consistency/epoch6_best_candidate.keras` (only if the mean noisy
  Macro-F1 exceeds `0.3644898279927664`)

It does **not** touch `latest_B3_resnet.keras`, `best_B3_resnet.keras`, the
Epoch 4 backups or `reports/B3_training_history.csv`.
Without a visible GPU the command is refused unless `--allow-cpu` is passed.

## Step 2 — Evaluate the STAGED checkpoint (clean and noisy)

These use the same six noisy conditions (BW/MA × 18/12/6 dB) and noise seed 2027
as the original notebook, and write only **new timestamped** files in
`reports/evaluation/`:

```powershell
# Noisy validation (six conditions + mean Macro-F1):
python evaluate_b3.py --checkpoint models/B3_CAM_Consistency/epoch6_latest.keras

# Clean validation (separate summary):
python evaluate_b3.py --clean --checkpoint models/B3_CAM_Consistency/epoch6_latest.keras
```

Do **not** use `--split test` or `--approved-test` at this stage.
Optionally evaluate the best candidate too, for a like-for-like comparison:

```powershell
python evaluate_b3.py --checkpoint models/B3_CAM_Consistency/epoch6_best_candidate.keras
```
(only if that file exists).

## Step 3 — Review metrics before any promotion

Check the staged summary CSVs in `reports/evaluation/`:

- `MEAN_NOISY_6_CONDITIONS` Macro-F1 — the **official selection metric**.
- Per-condition Macro-F1 for BW/MA at 18/12/6 dB.
- Clean summary (accuracy, macro P/R/F1, weighted F1, per-class, confusion matrix).

Decision rule:
- If mean noisy Macro-F1 **≤ 0.3644898279927664** → **do not promote a new best**;
  `best_B3_resnet.keras` must stay as the Epoch 3 checkpoint. A non-improving
  Epoch 6 can still be promoted as `latest`, but only with explicit approval.
- If mean noisy Macro-F1 **> 0.3644898279927664** → a new best is justified.

## Step 4 — Commit (only after review; no training)

```powershell
python train_b3_epoch6.py --commit
```

Before promoting, `--commit`:
1. re-verifies all checkpoint hashes and the 5-row official history;
2. verifies the staged history has exactly 6 rows;
3. checks that the staged score and the presence of
   `epoch6_best_candidate.keras` agree (blocks stale candidates);
4. copies `latest_B3_resnet.keras`, `best_B3_resnet.keras` and
   `B3_training_history.csv` to
   `backups/*_pre_epoch6_<timestamp>.*`;
5. atomically promotes the staged latest and history, and promotes the best
   checkpoint only when the score threshold was exceeded.

Re-running `--commit` after success is blocked by the precondition checks
(history would have 6 rows, not 5).

---

## What is deliberately NOT done

- No Epoch 5 re-run, no full notebook execution, no test-set evaluation.
- No modification of notebooks, datasets, historical CSVs or Epoch 4 backups.
- No automatic promotion: `--train` and `--commit` are separate commands.
