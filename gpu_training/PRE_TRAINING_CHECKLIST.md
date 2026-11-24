# Pre-training checklist — B3 Epoch 6 (GPU)

Do not run `--train` until every box is checked. Verified locally on 2026-11-22;
re-check items marked *(GPU)* on the GPU machine after transfer.

## Environment
- [x] Local Windows machine confirmed CPU-only; not used for training.
- [x] TensorFlow 2.21.0 GPU support requires Linux/WSL2 with NVIDIA CUDA GPU; native Windows >2.10 has no GPU support (official TensorFlow docs).
- [ ] *(GPU)* Python 3.10–3.13 active in `.venv_gpu`.
- [ ] *(GPU)* `python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"` returns a GPU.
- [ ] *(GPU)* GPU driver >= 525.60.13 (Linux) and supported compute capability (T4 = 7.5 verified historically).
- [ ] *(GPU)* `bash gpu_training/setup_gpu_environment.sh` completed without errors.

## Checkpoints and state
- [x] `latest_B3_resnet.keras` = Epoch 5, SHA256 `f26d0a5f…` (hash + exact Macro-F1 reproduction).
- [x] `best_B3_resnet.keras` = Epoch 3, SHA256 `610caade…`, best Macro-F1 0.3644898279927664.
- [x] Epoch 4 backups preserved and hashed in `reports/checkpoint_registry.csv`.
- [x] Checkpoints saved with Keras 3.13.2 load under Keras 3.15.1 (verified locally, hashes unchanged).
- [ ] *(GPU)* `bash gpu_training/verify_transfer.sh` prints PASS for all five checkpoints.
- [x] `reports/B3_training_history.csv` has 5 rows ending at epoch 5.

## Configuration and methodology
- [x] `reports/B3_training_config_canonical.json` = B3-canonical-v1 (seed 2027, batch 128, lr 0.0001, λ 0.1, BW/MA, SNRs 18/12/6, fresh Adam).
- [x] Epoch 6 script now verifies the canonical config at startup (fail-fast on drift).
- [x] No optimizer state in checkpoints → fresh Adam at iteration 0 (documented warm start).
- [x] Historical config with batch_size 32 retained unchanged as historical record.
- [x] Dataset split, class mapping, noise methodology and loss functions unchanged.

## Safety
- [x] `--train` writes only staging files; no official-path writes.
- [x] `--commit` requires timestamped backups before promotion and score-consistency check.
- [x] Test split sealed; `evaluate_b3.py` blocks it without `--approved-test`.
- [ ] *(GPU)* `python train_b3_epoch6.py --dry-run` and `--smoke` pass after transfer.

## Decision
- [ ] Review staged mean noisy Macro-F1 against 0.3644898279927664 before promotion.
- [ ] Promote only if justified; otherwise leave best checkpoint unchanged.

---

**Exact requirements to start Epoch 6:** a Linux GPU runtime with a CUDA-capable
NVIDIA GPU and Python 3.10–3.13; full project transferred; all checkpoint hashes
verified; canonical config verified; safe preflight passed; explicit human approval
after this checklist. Then run exactly:

```bash
python train_b3_epoch6.py --train
```
