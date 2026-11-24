# B3 CPU TRAINING FEASIBILITY REPORT — Epoch 6

Generated: 2026-11-22
Status: **inspection and benchmark design only — benchmark NOT YET RUN** (awaiting explicit approval).

## RAM precondition check (2026-11-22)

| Measurement | Value |
|---|---:|
| Total physical RAM | 7.79 GB |
| **Available physical RAM at check** | **0.596 GB** |
| Required threshold | ≥ 3.0 GB |
| Decision | **STOP — benchmark NOT executed** |

The user-approved gate required at least 3 GB of available physical RAM before
running the benchmark. Only 0.596 GB was available, so `benchmark_cpu_epoch6.py`
was **not run**. No benchmark results (batch times, mean/median, peak RAM) exist yet.
The user should close other applications and re-check available RAM before
retrying.

---

## 0. Files inspected

| Requested file | Found at | Result |
|---|---|---|
| `train_b3_epoch6.py` | project root | inspected |
| `reports/B3_training_config_canonical.json` | as requested | inspected (B3-canonical-v1) |
| `reports/B3_EPOCH6_WORKFLOW.md` | **NOT PRESENT** — actual file is `B3_EPOCH6_WORKFLOW.md` at project root | inspected at actual location |
| `gpu_training/GPU_TRAINING_WORKFLOW.md` | as requested | inspected (GPU-only guidance) |
| `reports/checkpoint_registry.csv` | as requested | 5 B3 rows verified |
| `reports/B3_training_history.csv` | as requested | 5 rows, last epoch 5 |

No file was modified during this inspection.

---

## 1. Laptop specifications (verified locally)

| Item | Value |
|---|---|
| OS | Windows 11 Pro (10.0.26300, build 26300), 64-bit |
| CPU | Intel Core i5-8265U @ 1.60 GHz, 4 physical cores / 8 logical threads |
| RAM | 7.79 GB total; **0.58 GB free at inspection time** (other applications open) |
| GPU | None (Intel UHD 620 only); `tf.config.list_physical_devices("GPU")` → `[]` |
| Python | 3.12.16 (`C:\Users\Lenovo\Downloads\ECG_QPAIN_2027\.venv`) |
| TensorFlow | 2.21.0 CPU; Keras 3.15.1; NumPy 2.5.5 |
| Disk | 4.7 GB free on C: (from earlier audit) |

---

## 2. Task A — Does the script support CPU execution? — PASS

`train_b3_epoch6.py` line 396 defines `--allow-cpu`, and `run_training()` guards GPU
execution with:

```python
gpu = tf.config.list_physical_devices("GPU")
if not gpu and not allow_cpu:
    raise RuntimeError(...)
```

Therefore the CPU command is:

```powershell
python train_b3_epoch6.py --train --allow-cpu
```

`--allow-cpu` only bypasses the GPU guard. It does **not** change any hyperparameter,
seed, checkpoint path or methodology.

## 3. Task B — CPU execution preserves the experiment — PASS

| Requirement | Preserved? | Evidence in script / config |
|---|---|---|
| Batch size 128 | **PASS** | `BATCH_SIZE = 128`; verified against canonical config at startup |
| Learning rate 0.0001 | **PASS** | `LEARNING_RATE = 0.0001`; canonical guard checks equality |
| LAMBDA_CAM 0.1 | **PASS** | `LAMBDA_CAM = 0.1`; canonical guard checks equality |
| Canonical configuration | **PASS** | `verify_canonical_config()` asserts 11 fields (version, batch, lr, λ, seeds, noise types/SNRs, fresh Adam, filter) |
| Seed 2027 | **PASS** | `random.seed`, `np.random.seed`, `tf.random.set_seed` at module import; `shuffle(10000, seed=2027)`; `default_rng(2027)` |
| Epoch 5 latest as initialization | **PASS** | `LATEST_PATH` loaded in `verify_preconditions()`; SHA256 guard `f26d0a5f…` |
| Fresh Adam optimizer | **PASS** | `tf.keras.optimizers.Adam(learning_rate=0.0001)` at iteration 0 |
| Existing training methodology | **PASS** | `cam.train_b3_step`, `cam.train_one_epoch`, `cam.evaluate_noisy_validation` and original loss functions unchanged |

CPU execution changes only device placement. No mixed-precision or XLA flag is set.
Floating-point results may differ slightly from GPU; this is a numerical, not
methodological, difference.

## 4. Task C — CPU benchmark design — READY (not executed)

New additive file: `benchmark_cpu_epoch6.py` (separate script; **training script unchanged**).

What it does:
- Runs `t.verify_preconditions()` (hash/config checks, loads official model read-only).
- Clones the model **in memory** and applies `set_weights` — official files never written.
- Calls `t.build_runtime(model, include_validation=False)` → real 59,720-beat,
  batch-128, shuffled(seed 2027) `tf.data` pipeline and real noise bank.
- Runs `--warmup` untimed batches then `--batches` timed batches using the real
  `cam.train_b3_step` (same function as full training).
- Per batch: records elapsed seconds and checks all three losses are finite.
- Reports mean / median / min / max seconds per batch and process **peak working set**
  via Windows `psapi.GetProcessMemoryInfo` (Linux fallback via `resource`).
- Re-hashes latest, best and history at the end to prove no write occurred.
- No evaluation, no test data, no checkpoint save, no history append.

CLI verified with `--help`; script compiles. It has not been executed.

**Exact benchmark command (requires your approval before I run it):**

```powershell
python benchmark_cpu_epoch6.py --batches 5 --warmup 1
```

## 5. Task D — Full Epoch 6 duration estimate — PENDING MEASUREMENT

No defensible measured estimate exists until the benchmark runs. The calculation will be:

```
estimated_training_minutes = mean_seconds_per_batch × 467 / 60
estimated_epoch_minutes    = estimated_training_minutes + validation_minutes
```

(467 batches = 59,720 beats ÷ batch 128, as verified in the script.)

For context only — **not a measurement and not a prediction**: the historical T4 run
took ~9.76 min for 467 batches ≈ 1.25 s/batch. Multipliers of 10×/20×/40× would give
roughly 1.6 h / 3.3 h / 6.5 h of training steps on CPU, before validation. These
multipliers are illustrative assumptions, not benchmark results; the real number will
come from the benchmark output.

Validation adds six full noisy-condition predictions over 19,530 beats each. Its cost
on this CPU is not yet measured and must be added separately.

## 6. Task E — Can the benchmark fit in ~8 GB RAM? — LIKELY YES, WITH CAUTION

Estimated process working set during benchmark:

| Component | Estimate |
|---|---:|
| Python + TensorFlow + Keras baseline | ~900–1,500 MB |
| X_train (59,720×288 float32, with channel axis) | ~66 MB |
| validation arrays (loaded but not noisy-copied in benchmark) | ~21 MB |
| Noise bank + numpy noise signals | ~10 MB |
| Model weights + fresh Adam moments | ~2 MB |
| Per-batch activations/gradients (batch 128, two CAM passes) | ~31–61 MB |
| `X_val_noisy` six copies | **not built** in benchmark mode |

Expected peak ≈ **1.2–2.2 GB process working set**, well under 8 GB.

**Caution:** only **0.58 GB RAM is currently free** because other applications are
open. The benchmark should still complete (Windows can page), but close browsers /
VS Code extra windows before running to avoid heavy swapping. Full training is more
memory-demanding than the benchmark (it builds the six noisy validation copies,
~129 MB) — still small relative to 8 GB, but the same caution applies.

## 7. Task F — Script changes — NONE to training script

`train_b3_epoch6.py`, the canonical config, registry, history and all research files
are **unchanged**. The only new file is the standalone benchmark script.

## 8. CPU limitations

- No GPU: native Windows TensorFlow ≥2.11 cannot use CUDA. CPU-only execution is
  possible but far slower than the historical T4 runs.
- The TF build reports missing AVX/FMA optimizations (informational warning), which
  further limits throughput.
- 4 cores / 8 threads shared with the OS and VS Code.
- Very low current free RAM (0.58 GB) risks swapping.
- Thermal throttling on a laptop during multi-hour training is likely.
- Numerical differences vs GPU are possible; report them if results are borderline.

## 9. Recommendation

**DO NOT PROCEED with full Epoch 6 training yet.**

**PROCEED with the read-only CPU benchmark** once you approve the command above.
Only after reviewing measured seconds/batch, peak RAM and the resulting duration
estimate should a decision on full `--train --allow-cpu` be made. If the benchmark
shows multi-hour runtime or memory pressure, the recommendation will be to wait for
a GPU environment rather than start on this laptop.

---

## Required next step

Approve and run:

```powershell
python benchmark_cpu_epoch6.py --batches 5 --warmup 1
```

Then I will update this report with actual benchmark results and a measured estimate.

## Integrity statement

No checkpoint, history file, dataset, notebook, report or configuration was modified.
Only `benchmark_cpu_epoch6.py` and this report were created.
