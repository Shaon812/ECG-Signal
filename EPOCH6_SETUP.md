# Epoch 6 preparation (B3 continuation)

The file `train_b3_epoch6.py` at the project root is the dedicated, safety-guarded
Epoch 6 continuation script. **It does not train by default.**

## Why this exists

The readiness assessment concluded that `latest_B3_resnet.keras` is very likely the
Epoch 5 checkpoint (embedded save time 2026-11-21 16:49:15, after the Epoch-4
backup at 16:38:37, with 31/49 weight arrays changed). The official target of
"Epoch 4" was therefore already surpassed on disk; `best_B3_resnet.keras` remains
the Epoch-3 best. Nothing was changed to "roll back" that state.

## Exact configuration (matches original notebook 07)

| Setting | Value | Note |
|---|---|---|
| Starting weights | `latest_B3_resnet.keras` (SHA256 `f26d0a5f…`) | presumed Epoch 5 |
| Batch size | **128** | notebook cell 135; the config JSON's `32` is stale |
| Learning rate | **0.0001** | notebook cells 34/46 |
| Lambda CAM | **0.1** | notebook cells 34/45 |
| Optimizer | **fresh Adam(lr=0.0001)** | no optimizer state exists in `.keras` files |
| Loss | weighted CE + 0.1 × CAM consistency | original `cam.calculate_b3_loss` |
| Train batches | 467 (59,720 beats, shuffle 10000 seed 2027) | notebook cell 135 |
| Noise | BW/MA channel 0, SNRs [24,18,12,6], region 0–390000 | notebook cells 15/19/20 |
| Validation | BW/MA × [18,12,6], seed 2027, region 390000–520000 | notebook cell 67 |
| Class weights | balanced, from `y_train` | notebook cell 88 |
| Features / CAM | layer `activation_6`, `differentiable_cam_for_model` | notebook cells 10/26+ |

Because no optimizer moments were saved, this is a **weight-only warm start**, not a
true optimizer-state resume.

## Commands (run from project root, with `.venv` active)

```powershell
# 1. SAFE: verify everything + ONE in-memory step on batch 4. Writes NOTHING.
python train_b3_epoch6.py --smoke

# 2. SAFE: verify + print the exact configuration. Writes NOTHING.
python train_b3_epoch6.py --dry-run

# 3. ON A SUITABLE GPU: full Epoch 6 -> STAGING outputs only.
#    Official checkpoints and history are NOT touched.
python train_b3_epoch6.py --train

# 4. AFTER reviewing staging results: promote them to official files.
#    Does NOT train. Creates timestamped backups first.
python train_b3_epoch6.py --commit
```

Full training is refused without a visible GPU unless `--allow-cpu` is passed
(expect 1–3+ hours per epoch on this laptop — not recommended).

## Safety guards built into the script

- Hashes of `latest_B3`, `best_B3`, both Epoch-4 checkpoint backups and the
  Epoch-4 history backup are verified before any mode runs.
- History must have exactly 5 rows ending at epoch 5.
- Model must have input `(None,288,1)`, output `(None,4)`, 194020 params, and
  layer `activation_6`.
- `_smoke` and `_dry-run` never call `.save()`, `to_csv()` or `os.replace()`.
- `--train` writes only `epoch6_latest.keras`, `B3_training_history_epoch6.csv`
  and (only if improved) `epoch6_best_candidate.keras`.
- `--commit` re-verifies all preconditions, copies official files to
  `backups/*_pre_epoch6_<timestamp>.*`, then atomically promotes staging files.
- `best_B3_resnet.keras` is promoted only if Epoch 6 validation Macro-F1 exceeds
  the historical best `0.3644898279927664`.

## Files created during preparation

- `train_b3_epoch6.py` (this script)
- `EPOCH6_SETUP.md` (this document)
- `EPOCH6_PREPARATION_REPORT.md` (verification results)

No staging output files are created until `--train` is explicitly executed.
