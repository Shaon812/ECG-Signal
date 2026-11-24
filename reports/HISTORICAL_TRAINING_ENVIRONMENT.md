# Historical training environment — confirmed vs unknown

Generated: 2026-11-22. Derived only from evidence stored inside the original
notebooks and checkpoint metadata. Anything not evidenced is marked **UNKNOWN**;
no hardware or software specification has been invented.

---

## CONFIRMED — B3 training sessions (notebook 07)

Evidence: stored outputs of notebook 07 cells 117, 128, 176 and 177; checkpoint
`metadata.json` files; Colab-specific setup code (`google.colab.drive`, `/content/...`).

| Item | Confirmed value | Evidence |
|---|---|---|
| Execution platform | **Google Colab** | `from google.colab import drive`, `/content/drive`, `/content/gdrive_mount` paths throughout notebooks 01–07 |
| GPU model | **NVIDIA Tesla T4** | cell 00 output `GPU Name: Tesla T4`; cell 177 `nvidia-smi` and `{'device_name': 'Tesla T4'}` |
| GPU memory | **15,360 MiB** total; ~12,683 MiB in use at snapshot | cell 177 `nvidia-smi` |
| GPU driver / CUDA | NVIDIA-SMI 580.82.07, Driver 580.82.07, CUDA Version 13.0 | cell 177 `nvidia-smi` |
| Compute capability | (7, 5) | cell 177 TensorFlow GPU details |
| TensorFlow version | 2.21.0 | cells 117/128, checkpoint metadata |
| Keras version at save time | 3.13.2 | `metadata.json` in all B3 `.keras` files |
| Training batch size | 128; 467 batches | cells 135/175/177/179 and their outputs |
| Recorded epoch times | ~55.0/55.1/54.9 min (epochs 1–3), ~9.79/9.76 min (epochs 4–5) | `reports/B3_training_history.csv` |

**Note on the epoch-time change:** the drop from ~55 min to ~9.8 min coincides with
the batch-size change from 32 to 128 (4× fewer optimisation steps). This is an
observation, not an additional hardware claim.

## CONFIRMED — clean baselines (notebook 05)

- Notebook 05 cell 2 output reports `GPU available: False`.
- Therefore **do not assume** B0/B1 were trained on the T4. Their actual execution
  device is **UNKNOWN**; only the printed flag is known.

## UNKNOWN / NOT RECORDED

- Colab host CPU model, core count and clock speed.
- System RAM available to the Colab sessions.
- Python version and full package list used in the original Colab sessions
  (only TensorFlow 2.21.0 and Keras 3.13.2 are evidenced).
- Exact Colab runtime/region, disk type, or whether GPU was shared/context-switched.
- Whether any run used mixed precision or XLA (no evidence found).
- The exact reason for the `GPU available: False` flag in notebook 05.

## LOCAL ENVIRONMENT (this machine, NOT the historical training machine)

Recorded in `LOCAL_ENVIRONMENT_REPORT.md`: Windows 11 Pro, Intel i5-8265U (4C/8T),
7.79 GB RAM, Intel UHD 620 (no NVIDIA GPU), Python 3.12.16, TensorFlow 2.21.0,
Keras 3.15.1, CPU-only execution.

This local machine was used **only** for migration, audits, read-only evaluations
and safe smoke tests — **not** for any historical training run.

## Reporting guidance

When writing the paper, state that B3 experiments were run on Google Colab with an
NVIDIA Tesla T4 (15 GB), and report the exact epoch times from
`B3_training_history.csv`. Do **not** report CPU/RAM figures for the Colab host,
since they were never recorded.
