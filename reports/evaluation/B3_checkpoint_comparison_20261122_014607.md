# B3 checkpoint comparison - validation only

Generated: 2026-11-22 01:46:07
Validation split only (19,530 beats). No test data used. No training performed.

Checkpoints compared:
- `latest_B3_resnet.keras` (SHA256 `f26d0a5f…`) — Epoch 5
- `best_B3_resnet.keras` (SHA256 `610caade…`) — Epoch 3

## 1. Clean validation (full, 19,530 beats)

| Metric | latest (E5) | best (E3) | latest − best |
|---|---:|---:|---:|
| Accuracy | 0.561393 | 0.593600 | −0.032207 |
| Macro Precision | 0.401388 | 0.398863 | +0.002526 |
| Macro Recall | 0.399815 | 0.377636 | +0.022179 |
| Macro-F1 | 0.351511 | 0.349438 | +0.002073 |
| Weighted F1 | 0.686968 | 0.714666 | −0.027698 |

Per-class F1 (latest / best): N 0.7067 / 0.7412 · S 0.0302 / 0.0312 ·
V 0.6669 / 0.6239 · F 0.0023 / 0.0014.

Confusion matrix — latest (rows true N,S,V,F; cols pred N,S,V,F):
```
[[9779 5750  648 1356]
 [ 356   96    1    9]
 [   4   36 1087  391]
 [   4    5    6    2]]
```
Confusion matrix — best:
```
[[10555  4074   601 2303]
 [  376    72     0   14]
 [    9     8   964  537]
 [    7     1     7    2]]
```

## 2. Noisy validation, all six conditions (19,530 beats each)

| Condition | latest Acc | latest MacroP | latest MacroR | latest Macro-F1 | latest W-F1 | best Acc | best MacroP | best MacroR | best Macro-F1 | best W-F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BW@18dB | 0.557552 | 0.400615 | 0.396715 | 0.349636 | 0.683818 | 0.595545 | 0.399392 | 0.378628 | 0.351135 | 0.716075 |
| BW@12dB | 0.560369 | 0.395678 | 0.371274 | 0.348679 | 0.684949 | 0.612289 | 0.404180 | 0.391187 | 0.361450 | 0.728835 |
| BW@6dB  | 0.632258 | 0.387341 | 0.430750 | 0.365316 | 0.736866 | 0.710753 | 0.400869 | 0.429732 | 0.387122 | 0.796199 |
| MA@18dB | 0.570763 | 0.402350 | 0.398211 | 0.353279 | 0.694974 | 0.603072 | 0.400224 | 0.379444 | 0.353481 | 0.721984 |
| MA@12dB | 0.579519 | 0.398026 | 0.402000 | 0.355132 | 0.700509 | 0.618024 | 0.401391 | 0.390374 | 0.361753 | 0.732534 |
| MA@6dB  | 0.622990 | 0.375895 | 0.403997 | 0.353530 | 0.728413 | 0.676805 | 0.386479 | 0.437905 | 0.371999 | 0.769891 |
| **MEAN** | — | — | — | **0.354262** | — | — | — | — | **0.364490** | — |

The best checkpoint has higher noisy Macro-F1 in **all six** conditions.
Full per-class metrics and all six confusion matrices are in the timestamped
`*_per_class.csv` and `*_confusion_matrices.csv` files alongside this report.

## 3. Comparison with historical best validation Macro-F1

| Checkpoint | Measured mean noisy Macro-F1 | Historical record | Match |
|---|---:|---:|---|
| latest (E5) | 0.3542619613487781 | `B3_training_history.csv` row 5 = 0.3542619613487781 | **exact** |
| best (E3) | 0.3644898279927664 | required best = 0.3644898279927664 | **exact** |

This numerically confirms: `latest_B3_resnet.keras` is the Epoch 5 model and
`best_B3_resnet.keras` is the Epoch 3 best. The earlier association, previously
inferential (timestamps + weights + history + notebook code), is now directly
verified by reproducing both saved Macro-F1 values from the actual weights.

## 4. Interpretation

Per the original methodology, the selection metric is the **mean noisy-validation
Macro-F1**. Epoch 5 (0.354262) is **0.010228 below** the Epoch 3 best (0.364490),
which is exactly why the original epoch-5 cell printed `BEST MODEL PRESERVED`.
Epoch 5 shows slightly better clean Macro-F1 and better macro recall, but worse
accuracy, weighted F1 and all six noisy Macro-F1 scores.

**Recommendation:** keep `best_B3_resnet.keras` unchanged. For Epoch 6, start from
`latest_B3_resnet.keras` (the true last-trained weights) as already configured in
`train_b3_epoch6.py`; promotion of any Epoch 6 result should only occur if its
mean noisy Macro-F1 exceeds 0.3644898279927664.
