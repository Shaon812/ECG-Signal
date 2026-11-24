# Safe checkpoint transfer to the GPU environment

Read-only with respect to the Windows originals. **Copy, never move.** Never write to
`latest_B3_resnet.keras`, `best_B3_resnet.keras`, the `backups/` folder, or
`reports/B3_training_history.csv` on the source machine.

## 1. Expected values (from `reports/checkpoint_registry.csv`)

| File | Expected SHA256 |
|---|---|
| `latest_B3_resnet.keras` (Epoch 5) | `f26d0a5fd8dacaa2c81a2b386f6189bcefadfbac475a356fb1b2b441462c2c32` |
| `best_B3_resnet.keras` (Epoch 3) | `610caadeba6fe31d396efacfd802eac3a156a0671a66baa8fe89f9f42b71ac3c` |
| `initial_B3_from_B2.keras` | `cbd39b6934b4504e893515b61168c77e4b50dbcb42295c8e7d9017f4ccf4fb21` |
| `backups/latest_epoch4_20261121_163837.keras` | `722502595f28ef8c5b63afac37815b27dd896f8ea2c74a6c68cc32f513c36298` |
| `backups/best_epoch4_20261121_163837.keras` | `610caadeba6fe31d396efacfd802eac3a156a0671a66baa8fe89f9f42b71ac3c` |

## 2. Transfer

Copy the **whole project tree** (data, models, reports, notebooks, src, scripts) to
the GPU machine — the training script resolves paths relative to its own location
and requires `src/ecg_qpain/`, `data/processed/` and `reports/*.json`.
Do not duplicate the 409 MB datasets more than necessary; a direct copy of the
project folder is simplest.

If transferring checkpoints individually, use `scp`/workspace upload and preserve
the exact relative paths under `models/B3_CAM_Consistency/`.

## 3. Verify on the GPU machine (Linux / Colab)

```bash
cd /path/to/ECG_QPAIN_2027
bash gpu_training/verify_transfer.sh
```

The script prints `PASS <file> <sha256>` for each checkpoint and exits non-zero on
any mismatch or missing file. It does not modify anything.

## 4. If verification fails

- **Do not train.** A mismatch means the checkpoint is not the audited Epoch 5 /
  Epoch 3 artifact.
- Re-copy the affected file from the source and re-run verification.
- If it still fails, stop and report the exact expected/actual hashes; do not
  "fix" the registry or overwrite the source file.

## 5. Additional read-only load check

After hash verification, the setup script runs:

```bash
python -c "import tensorflow as tf; \
m=tf.keras.models.load_model('models/B3_CAM_Consistency/latest_B3_resnet.keras', compile=False); \
print(m.input_shape, m.output_shape, m.count_params())"
```

Expected: `(None, 288, 1)`, `(None, 4)`, `194020`. The checkpoints were saved with
Keras 3.13.2 and load correctly with Keras 3.15.1 (verified locally on 2026-11-22).
