"""
=============================================================================
 CPU FEASIBILITY BENCHMARK for B3 Epoch 6 - READ-ONLY / NO WRITES
=============================================================================

Runs a small number of REAL training steps (real B3 model, real batch size 128,
real cam.train_b3_step, real tf.data pipeline) on an IN-MEMORY COPY of the
official latest checkpoint, then reports per-batch timing and process peak RAM.

SAFETY:
  * No file is written. No checkpoint, history, dataset or report is modified.
  * Uses a cloned in-memory model; official weights on disk are never touched.
  * No validation of the test split. No evaluation at all.
  * Does not start a full epoch (default 5 measured batches).

Usage (from project root, after activating .venv):
    python benchmark_cpu_epoch6.py --batches 5 --warmup 1
=============================================================================
"""

import argparse
import itertools
import os
import sys
import time

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

import numpy as np
import tensorflow as tf

import train_b3_epoch6 as t
from ecg_qpain import cam


def peak_rss_mb():
    """Peak resident set of this process in MB (Windows psapi, Linux fallback)."""
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        class PMC(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        pmc = PMC()
        pmc.cb = ctypes.sizeof(PMC)
        ok = psapi.GetProcessMemoryInfo(kernel32.GetCurrentProcess(),
                                        ctypes.byref(pmc), pmc.cb)
        if not ok:
            return None
        return pmc.PeakWorkingSetSize / (1024 ** 2)
    try:
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    except ImportError:
        return None


def main():
    ap = argparse.ArgumentParser(description="Read-only CPU benchmark for B3 Epoch 6")
    ap.add_argument("--batches", type=int, default=5, help="measured batches (default 5)")
    ap.add_argument("--warmup", type=int, default=1, help="untimed warmup batches (default 1)")
    args = ap.parse_args()
    if args.batches < 1 or args.warmup < 0:
        raise SystemExit("--batches must be >=1 and --warmup >=0")

    print("=" * 78)
    print("B3 EPOCH 6 - CPU FEASIBILITY BENCHMARK (NO WRITES)")
    print("=" * 78)
    print("TensorFlow:", tf.__version__, "| GPUs:", tf.config.list_physical_devices("GPU"))
    print("Batch size:", t.BATCH_SIZE, "| measured batches:", args.batches,
          "| warmup:", args.warmup)

    official = t.verify_preconditions()          # hash + config checks, load only
    model = tf.keras.models.clone_model(official)
    model.set_weights(official.get_weights())
    del official                                 # never touch official weights on disk

    train_dataset, _, _, _, _, _ = t.build_runtime(model, include_validation=False)

    measured = []
    all_nonfinite = []
    batches = itertools.islice(train_dataset, args.warmup + args.batches)
    for i, (x, y) in enumerate(batches):
        start = time.perf_counter()
        losses = cam.train_b3_step(x, y)
        elapsed = time.perf_counter() - start
        values = [float(v.numpy()) for v in losses]
        if not all(np.isfinite(v) for v in values):
            all_nonfinite.append((i, values))
        if i >= args.warmup:
            measured.append(elapsed)
            print(f"  batch {i - args.warmup + 1:>3}/{args.batches}: "
                  f"{elapsed:7.3f} s | losses " +
                  " ".join(f"{v:.6f}" for v in values))

    if not measured:
        raise SystemExit("No measured batches; increase --batches")

    mean_s = float(np.mean(measured))
    median_s = float(np.median(measured))
    print("\n--- timing ---")
    print(f"  mean   : {mean_s:.3f} s/batch")
    print(f"  median : {median_s:.3f} s/batch")
    print(f"  min/max: {min(measured):.3f} / {max(measured):.3f} s/batch")
    print(f"  non-finite loss batches: {len(all_nonfinite)}")
    peak = peak_rss_mb()
    print(f"  process peak working set: {peak:.1f} MB" if peak else "  peak RAM: unavailable")

    full_batches = t.EXPECTED_TRAIN_BATCHES
    est_train_min = mean_s * full_batches / 60
    print("\n--- ESTIMATE ONLY (not a measurement) ---")
    print(f"  {full_batches} batches x {mean_s:.3f} s = {est_train_min:.1f} min "
          f"({est_train_min/60:.2f} h) of training steps")
    print("  ADD validation time (6 noisy conditions x 19,530 beats) - measure separately.")
    print("  CPU/GPU numerics may differ slightly; methodology is unchanged.")

    # hash re-check proves no official file changed
    for p in [t.LATEST_PATH, t.BEST_PATH, t.HISTORY_PATH]:
        print(f"  unchanged: {os.path.basename(str(p))} = "
              f"{t.sha256(str(p))[:12]}...")
    print("\nBENCHMARK COMPLETE - no files written, no checkpoint modified.")


if __name__ == "__main__":
    main()
