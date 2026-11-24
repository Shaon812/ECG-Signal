# B3 E3 vs E5 vs E6 diagnostic analysis

Generated: 20261122_130728
Source: existing evaluation CSVs only. Read-only. No training, promotion, config or checkpoint change.

## Source file hashes

| File | SHA256 |
|---|---|
| `B3_eval_best_B3_resnet_20261122_014331_confusion_matrices.csv` | `3088f01c57b0a84000a36d289f7259b57ef97a1a18fffabcf6f560b71a9f8b34` |
| `B3_eval_best_B3_resnet_20261122_014331_per_class.csv` | `129d8ec4751903f38b0e63a1aedd15907d62311dfd63e14518647d690e75ae0a` |
| `B3_eval_best_B3_resnet_20261122_014331_summary.csv` | `9e7eb842e432b987409594378338be3d2279f4395c2fcd5630aa00f2524db81c` |
| `B3_eval_best_B3_resnet_20261122_014533_confusion_matrices.csv` | `a1893c604dd5a9506527bffdb35e40b4f584ef53654b92a5e4bc1d0a022c5769` |
| `B3_eval_best_B3_resnet_20261122_014533_per_class.csv` | `ee0b4e723ba864cb315942c9c300789826be074654760179b29ea0f1360cd362` |
| `B3_eval_best_B3_resnet_20261122_014533_summary.csv` | `a523e5f8da6e207568e5069c2a5457ae3f10b866074bfa2fdcb8228ae7897499` |
| `B3_eval_latest_B3_resnet_20261122_014307_confusion_matrices.csv` | `55b42ff3a039f16c539e548bb56a8542e847e0bcf2db0a88dc2b73dfb04be75f` |
| `B3_eval_latest_B3_resnet_20261122_014307_per_class.csv` | `a2459660e21f4cdb3cb9c4ee86123437a1876eee656c13545ac7340f35d5b9e7` |
| `B3_eval_latest_B3_resnet_20261122_014307_summary.csv` | `3d93ea6fe0560128be7568e92dfd76f7dd03ac0a068b78e553d4a631abb372f2` |
| `B3_eval_latest_B3_resnet_20261122_014432_confusion_matrices.csv` | `1f7400bd43a10d1961c653d4814ef2fb0ad47db7481e5b61ad8e5a0ab254e2de` |
| `B3_eval_latest_B3_resnet_20261122_014432_per_class.csv` | `bcdd32f57d9941c4d58f97ee992655b2e61f1008801e9199a8c70268f7a5a0a5` |
| `B3_eval_latest_B3_resnet_20261122_014432_summary.csv` | `06a294017803787acd6f91a4d01e4c46bbaf3b20b3c9e71bb9f65f9c09ffad0e` |
| `B3_eval_epoch6_latest_20261122_125915_confusion_matrices.csv` | `3351800a66a523b6420d9257776f180b8f0acfa61b63e13f3ba276f3e08a0227` |
| `B3_eval_epoch6_latest_20261122_125915_per_class.csv` | `3ad99c3aff2c0db5bcd33d6bf7f1e45b9274cfe46ffb329829011304d5ac4eee` |
| `B3_eval_epoch6_latest_20261122_125915_summary.csv` | `12aeb312d6ae55652ae2069587320241f87ee2e3ffe1b6606038d069836e22cc` |
| `B3_eval_epoch6_latest_20261122_125814_confusion_matrices.csv` | `f660a80f94cb855b47322df305ad88c385a4b12825cacd640af469390bdd6f74` |
| `B3_eval_epoch6_latest_20261122_125814_per_class.csv` | `d346b17e8cb845a2e677b99a4dbf6b6f124a0afbc6aef26d4a48f8b69f5736cf` |
| `B3_eval_epoch6_latest_20261122_125814_summary.csv` | `94340c45619bad324b63ac80c8b9ce8197a5799e65609c2f28811b4e6b1f13d3` |

## 1. Overall metrics (from summary CSVs)

| Checkpoint | Clean Macro-F1 | Noisy mean Macro-F1 | Clean accuracy | Noisy mean accuracy |
|---|---:|---:|---:|---:|
| E3 | 0.349438 | 0.364490 | 0.593600 | 0.636081 |
| E5 | 0.351511 | 0.354262 | 0.561393 | 0.587242 |
| E6 | 0.354150 | 0.349076 | 0.567896 | 0.584963 |

## 2. Per-class F1 (mean over 6 noisy conditions)

| Class | E3 | E5 | E6 | Δ E6−E3 | Δ E5−E3 |
|---|---:|---:|---:|---:|---:|
| N | 0.771517 | 0.727425 | 0.723437 | -0.048080 | -0.044092 |
| S | 0.029569 | 0.029309 | 0.030168 | +0.000599 | -0.000260 |
| V | 0.655182 | 0.658495 | 0.640970 | -0.014212 | +0.003313 |
| F | 0.001691 | 0.001818 | 0.001730 | +0.000039 | +0.000127 |

## 3. Per-class precision / recall (mean over 6 noisy conditions)

| Class | Metric | E3 | E5 | E6 | Δ E6−E3 |
|---|---|---:|---:|---:|---:|
| N | Precision | 0.965024 | 0.964147 | 0.964213 | -0.000811 |
| N | Recall | 0.643748 | 0.584593 | 0.579098 | -0.064650 |
| S | Precision | 0.016843 | 0.015948 | 0.016474 | -0.000369 |
| S | Recall | 0.124820 | 0.182540 | 0.179654 | +0.054834 |
| V | Precision | 0.612306 | 0.592255 | 0.546910 | -0.065395 |
| V | Recall | 0.708827 | 0.746596 | 0.781621 | +0.072793 |
| F | Precision | 0.000851 | 0.000919 | 0.000874 | +0.000022 |
| F | Recall | 0.127451 | 0.088235 | 0.088235 | -0.039216 |

## 4. Clean per-class F1

| Class | E3 | E5 | E6 | Δ E6−E3 |
|---|---:|---:|---:|---:|
| N | 0.741222 | 0.706677 | 0.709398 | -0.031824 |
| S | 0.031189 | 0.030241 | 0.031047 | -0.000143 |
| V | 0.623948 | 0.666871 | 0.674046 | +0.050098 |
| F | 0.001392 | 0.002254 | 0.002109 | +0.000716 |

## 5. Noise-condition Macro-F1 and degradation

| Condition | E3 | E5 | E6 | Δ E6−E3 | Δ E6−E5 |
|---|---:|---:|---:|---:|---:|
| BW@18dB | 0.351135 | 0.349636 | 0.351541 | +0.000406 | +0.001905 |
| BW@12dB | 0.361450 | 0.348679 | 0.346658 | -0.014791 | -0.002021 |
| BW@6dB | 0.387122 | 0.365316 | 0.353656 | -0.033465 | -0.011660 |
| MA@18dB | 0.353481 | 0.353279 | 0.356090 | +0.002609 | +0.002811 |
| MA@12dB | 0.361753 | 0.355132 | 0.350079 | -0.011673 | -0.005053 |
| MA@6dB | 0.371999 | 0.353530 | 0.336434 | -0.035565 | -0.017096 |

### BW vs MA robustness (mean Macro-F1 across SNRs)

| Noise | E3 | E5 | E6 | Δ E6−E3 |
|---|---:|---:|---:|---:|
| BW | 0.366569 | 0.354544 | 0.350618 | -0.015950 |
| MA | 0.362411 | 0.353980 | 0.347534 | -0.014877 |

## 6. Class-wise confusion (aggregated over 6 noisy conditions)

**E3** (rows=true, cols=pred)

| True\Pred | N | S | V | F |
|---|---:|---:|---:|---:|
| N | 67721 | 20288 | 4074 | 13115 |
| S | 2304 | 346 | 7 | 115 |
| V | 105 | 80 | 6456 | 2467 |
| F | 40 | 4 | 45 | 13 |

**E5** (rows=true, cols=pred)

| True\Pred | N | S | V | F |
|---|---:|---:|---:|---:|
| N | 61498 | 30850 | 4713 | 8137 |
| S | 2191 | 506 | 12 | 63 |
| V | 69 | 300 | 6800 | 1939 |
| F | 24 | 30 | 39 | 9 |

**E6** (rows=true, cols=pred)

| True\Pred | N | S | V | F |
|---|---:|---:|---:|---:|
| N | 60920 | 29345 | 5994 | 8939 |
| S | 2190 | 498 | 17 | 67 |
| V | 44 | 273 | 7119 | 1672 |
| F | 26 | 24 | 43 | 9 |

### Change in misclassifications E6 vs E3 (negative = fewer errors)

| True\Pred | N | S | V | F |
|---|---:|---:|---:|---:|
| N | -6801 | +9057 | +1920 | -4176 |
| S | -114 | +152 | +10 | -48 |
| V | -61 | +193 | +663 | -795 |
| F | -14 | +20 | -2 | -4 |

### Clean confusion E6 vs E3

| True\Pred | E3 | E6 |
|---|---:|---:|
| N correct | 10555 | 9839 |
| S correct | 72 | 93 |
| V correct | 964 | 1157 |
| F correct | 2 | 2 |

## 7. Decomposition of the Macro-F1 decline

Total Δ(E6−E3) = -0.015413456; Δ(E5−E3) = -0.010227867; Δ(E6−E5) = -0.005185590

By class (contribution = mean F1 change / 4, sums to total):

| Class | contribution to Δ(E6−E3) |
|---|---:|
| N | -0.012019934 |
| S | +0.000149768 |
| V | -0.003553018 |
| F | +0.000009727 |
| **sum** | **-0.015413456** |

By noise condition (contribution = ΔF1 / 6, sums to total):

| Condition | contribution to Δ(E6−E3) |
|---|---:|
| BW@18dB | +0.000067588 |
| BW@12dB | -0.002465210 |
| BW@6dB | -0.005577583 |
| MA@18dB | +0.000434859 |
| MA@12dB | -0.001945569 |
| MA@6dB | -0.005927540 |

## 8. Evidence-based interpretation

- E6 noisy mean Macro-F1 (0.349076) is below E5 (0.354262) and E3 (0.364490); the official best remains Epoch 3.
- E6 has the highest **clean** Macro-F1 (0.354150 vs 0.351511 E5 and 0.349438 E3) but is the only checkpoint whose noisy mean (0.349076) is **below** its clean score. E3 (0.364490 vs 0.349438) and E5 (0.354262 vs 0.351511) both score higher under noise than clean, so E6 alone shows a noise-specific degradation.
- The decline is driven by class **N**: mean noisy F1 drops 0.771517 → 0.723437 (Δ −0.048080), contributing −0.012020 of the total −0.015413 Macro-F1 decline (≈78%). Class V drops 0.655182 → 0.640970 (Δ −0.014212, contribution −0.003553, ≈23%). S and F are essentially flat/slightly positive. N's precision stays ~0.964, but its recall falls 0.643748 → 0.579098 (Δ −0.064650). V's precision falls 0.612306 → 0.546910 (Δ −0.065395) while its recall rises 0.708827 → 0.781621 (Δ +0.072793).
- Degradation is concentrated at the lowest SNR: MA@6dB Δ −0.035565 and BW@6dB Δ −0.033465, while 18 dB conditions are flat or slightly improved (BW@18dB +0.000406, MA@18dB +0.002609). Both noise families worsen overall (BW −0.015950, MA −0.014877).
- Aggregated noisy confusion E6 vs E3 shows more N→S (+9,057) and N→V (+1,920) errors but fewer N→F (−4,176); V becomes more often correct (+663) with fewer V→F (−795) and V→N (−61) errors. The dominant change is N being assigned to S/V under noise, not a broad increase in V errors.

## 9. Recommendations for the next training step

1. **Do not commit Epoch 6** and do not promote it as best; E3 remains the best checkpoint by the official metric. E6 also trails E5.
2. If another epoch is attempted, start from the checkpoint that is best under noise. Evidence here favours E3 weights (best noisy robustness) over E6 weights; E5 is intermediate. Any restart point is a research decision requiring explicit approval because it changes training lineage.
3. The pattern (clean up, noisy down) suggests the CAM-consistency objective is not preserving noise robustness at the current learning rate/lambda. Before Epoch 7, consider (with approval) evaluating whether λ_CAM or noise-severity sampling should be adjusted — this would change methodology and is **not** authorised by this diagnostic.
4. Because F and S have tiny support (17 and 462 validation beats), their metrics are high-variance. Do not base a major decision on F/S alone; the aggregate decline is broad across conditions and classes.
5. Keep the test split sealed. Any further evaluation remains validation-only until final model selection.

## Integrity

No file other than this new staging diagnostic was created. No checkpoint, config, history or existing evaluation result was modified.
