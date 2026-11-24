# B3_TRAINING_RESUME_READINESS_REPORT

Generated: 2026-11-22
Project root: `C:\Users\Lenovo\Downloads\ECG_QPAIN_2027`

**This is a read-only assessment. No training was started. No checkpoint, backup,
history file, dataset or methodology was modified.**

---

## Executive conclusion

The on-disk evidence converges on a clear picture: **the current
`latest_B3_resnet.keras` is almost certainly the Epoch 5 model**, while
`best_B3_resnet.keras` is still the Epoch 3 (best) model. The folder named
`backups/` captures the state **after Epoch 4 and before Epoch 5**. The checkpoint
files contain **no optimizer state**, so any future "resume" would be a
weight-only warm start with a freshly initialised Adam optimizer, not a true
resume of Epoch 5's optimizer moments.

Given 8 GB RAM (0.91 GB free at assessment time), a CPU-only TensorFlow 2.21 with
no GPU support on native Windows, ~467 batches per epoch and a recorded
9.76–9.79 min/epoch from the original (accelerated) runs, **full B3 training on
this laptop is not practical or recommended**. See Tasks 8–10.

---

## Task 1 — B3 checkpoints and backups inspected

| File | Size | Role |
|---|---:|---|
| `models/B3_CAM_Consistency/initial_B3_from_B2.keras` | 895,863 | Initial weights from B2 |
| `models/B3_CAM_Consistency/best_B3_resnet.keras` | 895,863 | "Best" checkpoint |
| `models/B3_CAM_Consistency/latest_B3_resnet.keras` | 895,863 | "Latest" checkpoint |
| `models/B3_CAM_Consistency/backups/best_epoch4_20261121_163837.keras` | 895,863 | Epoch-4-time best backup |
| `models/B3_CAM_Consistency/backups/latest_epoch4_20261121_163837.keras` | 895,863 | Epoch-4-time latest backup |
| `models/B3_CAM_Consistency/backups/history_epoch4_20261121_163837.csv` | 462 | 4-row history backup |
| `reports/B3_training_history.csv` | 561 | Current 5-row history |

No other B3 history/backup files exist in the project (verified by recursive search).

## Task 2 — B3 training history files inspected

**`reports/B3_training_history.csv` (current, 5 rows):**

| epoch | train_loss | train_ce_loss | train_cam_loss | training_time_min | val_macro_f1 |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.4024671060703096 | 0.4014683047475447 | 0.009988015743035 | 55.0454 | 0.3036416111401026 |
| 2 | 0.346453770432479 | 0.3454974999897711 | 0.0095627024435118 | 55.1040 | 0.3434358233246588 |
| 3 | 0.3279334781615953 | 0.3270652158315588 | 0.0086826235670086 | 54.8838 | **0.3644898279927664** |
| 4 | 0.29901446319909114 | 0.2981343682121477 | 0.008800946865569825 | 9.7876 | 0.34801116820149897 |
| 5 | 0.29190398723174216 | 0.2910846733992692 | 0.008193133974236454 | 9.7600 | 0.3542619613487781 |

SHA256: `c69acbed88060830deca8b9eefb0b89ed6b4fb5a0425d010430163c0715f51d5`

**`backups/history_epoch4_20261121_163837.csv` (4 rows):** byte-for-byte identical
to rows 1–4 of the current history.
SHA256: `bdaf8e6b921432882dbc6cfabcc445a6169cf36fdaa342017108ef68dfdc2608`

## Task 3 — Checkpoint SHA256 comparison

| Checkpoint | SHA256 (full) | Equivalent to |
|---|---|---|
| `initial_B3_from_B2.keras` | `cbd39b6934b4504e893515b61168c77e4b50dbcb42295c8e7d9017f4ccf4fb21` | `initial_B4_from_B2.keras` |
| `backups/best_epoch4_…keras` | `610caadeba6fe31d396efacfd802eac3a156a0671a66baa8fe89f9f42b71ac3c` | **`best_B3_resnet.keras` (identical)** |
| `backups/latest_epoch4_…keras` | `722502595f28ef8c5b63afac37815b27dd896f8ea2c74a6c68cc32f513c36298` | unique |
| `best_B3_resnet.keras` | `610caadeba6fe31d396efacfd802eac3a156a0671a66baa8fe89f9f42b71ac3c` | backup best_epoch4 |
| `latest_B3_resnet.keras` | `f26d0a5fd8dacaa2c81a2b386f6189bcefadfbac475a356fb1b2b441462c2c32` | **no backup matches** |

All files are Keras-v3 `.keras` archives containing exactly
`metadata.json`, `config.json`, `model.weights.h5`.

## Task 4 — Exact relationships (evidence-based)

### Embedded save timestamps and weight hashes

| Checkpoint | `date_saved` (embedded) | weights hash (internal) |
|---|---|---|
| `initial_B3_from_B2` | 2026-11-20@12:56:03 | `8677c2daac1f0556a000` |
| `best_B3` = backup `best_epoch4` | 2026-11-20@15:53:22 | `99ebb883e6b35d0be211` |
| backup `latest_epoch4` | 2026-11-21@16:28:09 | `bfd9f85fd5669531e0b9` |
| current `latest_B3` | **2026-11-21@16:49:15** | `06089c6728b9fe4dad68` |

Backup filename timestamp: `20261121_163837` = 2026-11-21 16:38:37.

### Reconstructed timeline

| Time | Event | Supporting evidence |
|---|---|---|
| 11-20 12:56 | B3 initialised from B2 | `initial_B3_from_B2` timestamp |
| 11-20 ~13:51 / 14:46 / 15:41 | Epochs 1, 2, 3 (~55 min each) | history durations |
| 11-20 15:53 | **Best model saved (Epoch 3)** | `best_B3` timestamp + best F1 at epoch 3 |
| 11-21 16:28 | **Epoch 4 latest saved** | backup `latest_epoch4` timestamp |
| 11-21 16:38:37 | **Backup taken** (best, latest, 4-row history) | backup filenames |
| 11-21 ~16:39–16:49 | Epoch 5 ran (~9.76 min) | history row 5 + save at 16:49 |
| 11-21 16:49 | **Current `latest_B3` saved**; best left unchanged | current latest timestamp; best hash unchanged |

### Weight-level comparison (epoch-4 latest vs current latest)

- 49 weight arrays in each; **31 differ** — exactly the 31 trainable variables.
- Max absolute weight delta: `0.016828399151563644`.
- Non-trainable BatchNorm statistics are identical.
- This is the signature of one additional training pass, not a reload or cosmetic change.

### Notebook logic matches the on-disk state exactly

- **Cell 113 / 175 (Epoch 4):** trains, appends to history, **always saves `latest`**, saves `best` only if F1 improves, writes history.
- **Cell 178 (STEP 40):** backs up `latest`, `best`, `history` with names
  `{name}_epoch4_{timestamp}` — producing exactly the three backup files present.
- **Cell 179 (STEP 41, Epoch 5):** asserts `len(b3_history) == 4` and last epoch == 4,
  trains epoch 5, appends row 5, **saves `latest`**, and prints `BEST MODEL PRESERVED`
  because 0.35426 < 0.36449, then overwrites history with 5 rows.
- On disk: history has 5 rows, latest changed, best unchanged. **Consistent in full.**

## Task 5 — Can the current latest be reliably associated with Epoch 5?

**Assessment: HIGH CONFIDENCE (inferential, not direct metadata proof).**

Supporting evidence:
1. Current history contains exactly 5 epochs; epoch 5 F1 = 0.3542619613487781.
2. The epoch-5 notebook cell saves `latest` but not `best`; on disk `latest` changed
   and `best` is byte-identical to the epoch-4 backup best.
3. Current latest was saved 2026-11-21@16:49:15 — 10m38s after the 16:38:37
   backup, and 21m06s after the epoch-4 latest (16:28:09). Epoch 5's recorded
   duration is 9.76 min, which fits the interval between backup and final save.
4. 31/49 arrays (exactly the trainable ones) differ from the epoch-4 latest.

**Caveat (why not absolute proof):** the `.keras` file contains no epoch number,
no step counter and no optimizer iteration. The association is a convergence of
file timestamps, weights, history rows and notebook code — strong, but not an
embedded ground truth. No checkpoint epoch number was assumed without this evidence.

**Implication:** if training ever resumes, the weight-only starting point for
"Epoch 6" should be `latest_B3_resnet.keras` (the true last trained weights), while
`best_B3_resnet.keras` remains the Epoch-3 best for comparison/reporting.

## Task 6 — Optimizer-state availability

**None of the B3 checkpoints contain optimizer state.**

- Archive members are only `metadata.json`, `config.json`, `model.weights.h5`.
- `config.json` has **`compile_config: None`** for latest, best and backup-latest.
- Loading with `compile=True` yields no optimizer object; only weights are restored.

Consequences for any future resume:
- Adam must be re-created with `learning_rate=0.0001` (original value).
- Adam's first/second moments and iteration count are **lost** — a warm start, not a
  true continuation of Epoch 5. Early steps may behave differently from the
  original trajectory; this should be documented if training is ever resumed.
- BatchNorm moving statistics *are* stored in `model.weights.h5` and will be restored.

## Task 7 — Original B3 training configuration (verified)

From `reports/B3_B4_experiment_config.json` and notebook 07 cells 34/36/135/179:

| Setting | Value | Source |
|---|---|---|
| Learning rate | 0.0001 | config JSON, cells 34, 46 |
| Lambda CAM | 0.1 | config JSON, cells 34, 45 |
| Total planned epochs | 10 (B3), 10 (B4) | config JSON |
| Training SNRs | [24, 18, 12, 6] | config JSON, cells 20, 41 |
| Validation SNRs | [18, 12, 6] | notebook cell 65 |
| Noise sources | BW, MA (channel 0), `noise_bank` shape (2, 650000) | cells 15/19 |
| Noise split ranges | train 0–390000, val 390000–520000, test 520000–650000 | noise config JSON |
| Initial weights | B2 trained weights | config JSON |
| Test set used for training | false | config JSON |
| Loss | weighted CE + 0.1 × CAM consistency | cells 45, 165 |
| Class weights | balanced, computed from `y_train` | cells 88, 1240 |
| Shuffle | buffer 10000, seed 2027 | cell 135 |
| Optimizer | Adam(0.0001) | cell 46 |

**Important discrepancy:** `reports/B3_B4_experiment_config.json` records
`batch_size: 32` (from cell 34), but the actual epoch 4/5 training cells use
`BATCH_SIZE = 128` (cell 135) with `len(train_dataset) == 467` and assert batch
shape `(128, 288, 1)` (cells 175, 179). The 55→9.8 min drop in the history after
epoch 3 is consistent with this 4× reduction in step count. **Do not rely on the
JSON's batch_size when reproducing epochs 4+.** No config file was modified.

## Task 8 — CPU training memory estimate

Theoretical breakdown from the real objects (float32):

| Object | Size |
|---|---:|
| X_train (59,720 × 288) | 65.61 MB |
| y_train | 0.46 MB |
| X_val (19,530 × 288) | 21.46 MB |
| `noise_bank` tf (2 × 650,000) | 4.96 MB |
| `noise_signals` numpy dict (duplicate of above) | 4.96 MB |
| `X_val_noisy` (2 noise types × 3 SNRs = 6 copies) | 128.74 MB |
| tf.data shuffle buffer (10,000) | 11.06 MB |
| Model weights + BN vars | 0.83 MB |
| Adam moments (2 × trainable weights) | 1.48 MB |
| Per-batch activations/gradients (2 CAM passes, batch 128) | ~31–61 MB |
| Python + TF + Jupyter baseline (typical) | ~0.9–1.5 GB |

**Estimated process peak: ~1.2–3.7 GB**, depending on TF's allocator behaviour and
whether `X_val_noisy` is rebuilt while training tensors are live. The dataset
itself is small; the dominant cost is the TF runtime and the six noisy validation
copies.

Observed RAM at assessment time: **7.79 GB total, 0.91 GB free** (other applications
open). Disk: 4.74 GB free.

## Task 9 — Is full training practical on this laptop?

**Assessment: NOT practical / not recommended.**

- **Memory:** theoretical peak (1.2–3.7 GB) fits in 8 GB *in principle*, but with
  only ~0.91 GB currently free, there is no comfortable margin. Memory pressure
  or swapping is likely with a browser/VS Code open.
- **Compute:** 467 batches/epoch, each running two differentiable-CAM passes
  (clean + noisy) plus `tf.map_fn` noise augmentation. Original recorded epochs 4/5
  took **9.76–9.79 min each**, but those were produced in the Colab environment;
  on a 4-core i5-8265U with no AVX/FMA enabled in this TF build, expect a large
  slowdown — plausibly **1–3+ hours per epoch**. Five remaining epochs (6–10)
  would mean many hours of continuous CPU load.
- **GPU:** none. TensorFlow 2.21 on native Windows does not support CUDA; WSL2 or
  DirectML would be required, and there is no NVIDIA hardware to use either way.
- **Disk:** 4.74 GB free is sufficient for checkpoints but leaves little room for
  other large artifacts.

Safe local use is limited to the smoke tests already performed (single steps,
batch 4), not a full epoch.

## Task 10 — Recommended safe training environment

1. **Preferred — cloud GPU (Colab / Kaggle / equivalent).** Restore the desired
   starting weights (`latest_B3_resnet.keras` for a genuine continuation from
   Epoch 5, or `latest_epoch4_…keras` if you explicitly want the authoritative
   Epoch-4 state), re-create Adam(0.0001), and use batch 128 with the exact
   SNR/noise configuration above. Record the starting SHA256 and the fact that
   optimizer moments are reset.
2. **Alternative — WSL2 with an NVIDIA GPU** (not available on this machine): native
   Windows TF ≥2.11 cannot use CUDA.
3. **If local execution is unavoidable:** work only in a sandbox copy of the
   project; never point `B3_LATEST_PATH` / `B3_CHECKPOINT_PATH` /
   `B3_HISTORY_PATH` at the official files; close other applications; consider a
   reduced data subset for timing first; expect long runtimes and document any
   deviation from batch 128. Note that changing batch size changes optimisation
   dynamics — treat results as a new experiment, not a continuation of B3.
4. **Before any resume, decide explicitly which state is authoritative.** The
   evidence here says Epoch 5 was executed; the stated project target was Epoch 4.
   Do not silently overwrite either `latest_B3_resnet.keras` or the epoch-4 backup.

---

## Integrity statement

All 30 non-notebook research files (checkpoints, backups, histories, reports) were
read only; their SHA256 values are unchanged from the pre-assessment snapshot.
No training step, evaluation epoch, file write, rename or deletion occurred during
the preparation of this report.
