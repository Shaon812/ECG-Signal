# B3 Epoch 6 staged evaluation - comparison

Generated: 20261122_125946
Evaluation of staged `epoch6_latest.keras` only. No promotion, no official-file changes.

Staged checkpoint SHA256: `c9a23746518a2ec99daa8290a3ee8e2d20df6a66ac69eb4d23c2c1f7e99b9214`
Checkpoint SHA256 and `config_version=B3-canonical-v1` are embedded in every output row.

## Mean noisy-validation Macro-F1 (official selection metric)

| Checkpoint | Mean noisy Macro-F1 | Δ vs E6 |
|---|---:|---:|
| E3_best_noisy | 0.3644898279927664 | +0.015413456 |
| E5_latest_noisy | 0.3542619613487781 | +0.005185590 |
| E6_staged_noisy | 0.3490763717675494 | +0.000000000 |

## Clean validation (19,530 beats)

| Checkpoint | Accuracy | Macro Precision | Macro Recall | Macro-F1 | Weighted F1 |
|---|---:|---:|---:|---:|---:|
| E3_best_clean | 0.593600 | 0.398863 | 0.377636 | 0.349438 | 0.714666 |
| E5_latest_clean | 0.561393 | 0.401388 | 0.399815 | 0.351511 | 0.686968 |
| E6_staged_clean | 0.567896 | 0.396526 | 0.410576 | 0.354150 | 0.689988 |

## Noisy validation by condition (Macro-F1)

| Condition | E3 best | E5 latest | E6 staged |
|---|---:|---:|---:|
| BW@18dB | 0.351135 | 0.349636 | 0.351541 |
| BW@12dB | 0.361450 | 0.348679 | 0.346658 |
| BW@6dB | 0.387122 | 0.365316 | 0.353656 |
| MA@18dB | 0.353481 | 0.353279 | 0.356090 |
| MA@12dB | 0.361753 | 0.355132 | 0.350079 |
| MA@6dB | 0.371999 | 0.353530 | 0.336434 |

## Interpretation

- Epoch 6 mean noisy Macro-F1 = **0.3490763717675494**, reproducing the staged training-history value exactly.
- Historical best (Epoch 3) = 0.3644898279927664; Epoch 5 = 0.3542619613487781.
- Epoch 6 is **below** both Epoch 5 and Epoch 3 on the official selection metric.
- Therefore no new best is justified; `best_B3_resnet.keras` must remain the Epoch 3 checkpoint.
- No `--commit` or promotion has been performed.

## New staging files and hashes

- `B3_eval_epoch6_latest_20261122_125814_confusion_matrices.csv` — `f660a80f94cb855b47322df305ad88c385a4b12825cacd640af469390bdd6f74` — 2606 bytes
- `B3_eval_epoch6_latest_20261122_125814_per_class.csv` — `d346b17e8cb845a2e677b99a4dbf6b6f124a0afbc6aef26d4a48f8b69f5736cf` — 3819 bytes
- `B3_eval_epoch6_latest_20261122_125814_summary.csv` — `94340c45619bad324b63ac80c8b9ce8197a5799e65609c2f28811b4e6b1f13d3` — 1387 bytes
- `B3_eval_epoch6_latest_20261122_125915_confusion_matrices.csv` — `3351800a66a523b6420d9257776f180b8f0acfa61b63e13f3ba276f3e08a0227` — 495 bytes
- `B3_eval_epoch6_latest_20261122_125915_per_class.csv` — `3ad99c3aff2c0db5bcd33d6bf7f1e45b9274cfe46ffb329829011304d5ac4eee` — 692 bytes
- `B3_eval_epoch6_latest_20261122_125915_summary.csv` — `12aeb312d6ae55652ae2069587320241f87ee2e3ffe1b6606038d069836e22cc` — 295 bytes

## Integrity

- 21 pre-existing official/evaluation files checked; 0 changed.
- Official checkpoints, Epoch 4 backups, official training history: unchanged.

