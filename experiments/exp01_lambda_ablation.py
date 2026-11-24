#!/usr/bin/env python
"""
EXP-01: B3 CAM Consistency Lambda Ablation — LOW-MEMORY, STAGING-ONLY RUNNER.

Branches (all start from the SAME verified E3 best checkpoint):
  EXP-A: lambda = 0.10
  EXP-B: lambda = 0.05
  EXP-C: lambda = 0.20

Low-memory design:
  * --branch all launches each branch as a SEPARATE Python process, sequentially.
    The parent process stays lightweight (no TensorFlow/numpy imported).
  * Each branch process loads exactly ONE model (no in-memory clone).
  * Training data is used in-place (no redundant float32 copy); validation noisy
    sets are generated ONE CONDITION AT A TIME instead of all six at once.
  * Evaluation uses small prediction batches (--eval-batch-size, default 64)
    via a direct batched forward pass (no model.predict scratch buffers).
  * Each noisy condition is written into ONE preallocated array (no per-beat
    list and no second contiguous copy); RNG order is unchanged.
  * Training-only TF objects (noise bank, optimizer, class-weight tensor,
    feature extractor, classifier head) are deleted immediately after training.
  * TensorFlow session and large arrays are released before the child exits.
  * Estimated minimum realistic peak for one branch: ~1.3-1.7 GB RSS.
    The 3.0 GB safety gate is intentionally retained.

Safety (unchanged):
  * Requires >= 3.0 GB available RAM (--ram-min), checked in parent and child.
  * E3 SHA256 verified before every branch.
  * Canonical config never modified; lambda overridden in memory only.
  * No official checkpoint, history or config write. No test-set evaluation.
  * No promotion/commit. All outputs are new staging files guarded against overwrite.

Usage (from project root, .venv active):
  python experiments/exp01_lambda_ablation.py --branch all
  python experiments/exp01_lambda_ablation.py --branch A
"""

import argparse
import csv
import ctypes
import gc
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E3_PATH = ROOT / "models" / "B3_CAM_Consistency" / "best_B3_resnet.keras"
E3_SHA = "610caadeba6fe31d396efacfd802eac3a156a0671a66baa8fe89f9f42b71ac3c"
BRANCHES = {"A": 0.10, "B": 0.05, "C": 0.20}
CLASS_NAMES = ["N", "S", "V", "F"]

MODEL_ROOT = ROOT / "models" / "experiments" / "EXP01_LAMBDA_ABLATION"
REPORT_ROOT = ROOT / "reports" / "experiments" / "EXP01_LAMBDA_ABLATION"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def available_ram_gb():
    if os.name == "nt":
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]
        m = MEMORYSTATUSEX()
        m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return m.ullAvailPhys / (1024 ** 3)
    try:
        with open("/proc/meminfo", encoding="utf-8") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) * 1024 / (1024 ** 3)
    except OSError:
        pass
    return -1.0


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite: {path}")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def run_branch(name, lam, ram_min, eval_batch):
    # Heavy imports are confined to the isolated branch process.
    import csv
    import numpy as np
    import tensorflow as tf
    import wfdb
    from sklearn.metrics import (
        accuracy_score, confusion_matrix, f1_score,
        precision_recall_fscore_support, precision_score, recall_score,
    )
    from sklearn.utils.class_weight import compute_class_weight

    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "src"))
    import train_b3_epoch6 as t
    from ecg_qpain import cam, noise, paths

    print(f"\n=== EXP-{name} lambda={lam} ===")
    avail = available_ram_gb()
    print(f"available RAM = {avail:.3f} GB (minimum {ram_min} GB)")
    if avail < ram_min:
        raise RuntimeError(f"STOP: available RAM {avail:.3f} GB < {ram_min} GB")

    actual = sha(E3_PATH)
    if actual != E3_SHA:
        raise RuntimeError(f"E3 SHA256 mismatch: {actual}")
    print("E3 SHA256 VERIFIED:", actual)
    t.verify_canonical_config()

    mdir = MODEL_ROOT / f"EXP-{name}_lambda{lam:.2f}"
    rdir = REPORT_ROOT / f"EXP-{name}_lambda{lam:.2f}"
    mdir.mkdir(parents=True, exist_ok=False)
    rdir.mkdir(parents=True, exist_ok=False)

    # ---- ONE model copy only ----
    model = tf.keras.models.load_model(str(E3_PATH), compile=False)

    # ---- low-memory training data (no astype copy) ----
    train = np.load(ROOT / "data" / "processed" / "train_beats.npz")
    X_train = train["X"]
    if X_train.ndim == 2:
        X_train = X_train[..., np.newaxis]          # view, no copy
    if X_train.dtype != np.float32:
        X_train = X_train.astype(np.float32)
    y_train = train["y"].astype(np.int64)
    train.close()
    if X_train.shape[1:] != (288, 1) or len(X_train) != 59720:
        raise RuntimeError("unexpected training data shape")
    train_dataset = (tf.data.Dataset.from_tensor_slices((X_train, y_train))
                     .shuffle(10000, seed=2027)
                     .batch(t.BATCH_SIZE)
                     .prefetch(tf.data.AUTOTUNE))
    if len(train_dataset) != t.EXPECTED_TRAIN_BATCHES:
        raise RuntimeError("unexpected batch count")

    # ---- noise bank (kept small, reused for evaluation) ----
    signals = {}
    for rid in ["bw", "ma"]:
        sig, _ = wfdb.rdsamp(os.path.join(paths.NSTDB_EXTRACTED, rid))
        signals[rid] = sig[:, 0].astype(np.float32)
    noise_bank = tf.constant(np.stack([signals["bw"], signals["ma"]]), dtype=tf.float32)

    cw = compute_class_weight(class_weight="balanced", classes=np.array([0, 1, 2, 3]), y=y_train)

    # ---- runtime globals expected by the original training function ----
    cam.class_weights_tensor = tf.constant(cw, dtype=tf.float32)
    cam.noise_bank = noise_bank
    cam.b3_model = model
    cam.b3_optimizer = tf.keras.optimizers.Adam(learning_rate=t.LEARNING_RATE)  # FRESH
    cam.b3_feature_extractor, cam.b3_classifier_head = cam.create_cam_components(model)
    cam.LAMBDA_CAM = lam                     # in-memory only; canonical config untouched
    print(f"cam.LAMBDA_CAM = {lam}; Adam iterations = {int(cam.b3_optimizer.iterations.numpy())}")

    start = time.time()
    losses = cam.train_one_epoch(cam.train_b3_step, train_dataset, model, f"EXP-{name}")
    minutes = (time.time() - start) / 60
    print(f"training minutes: {minutes:.3f} | losses: {losses}")

    ckpt = mdir / "checkpoint.keras"
    model.save(str(ckpt))
    ckpt_sha = sha(ckpt)

    hist = [{
        "branch": f"EXP-{name}", "lambda": lam, "epoch": 1,
        "train_loss": losses["train_loss"], "train_ce_loss": losses["train_ce_loss"],
        "train_cam_loss": losses["train_cam_loss"], "training_time_min": minutes,
        "checkpoint_sha256": ckpt_sha,
    }]
    write_csv(rdir / "history.csv", hist)
    del train_dataset, X_train, y_train
    gc.collect()

    # Release training-only objects now; evaluation only needs `model`, `signals`
    # and the validation arrays. This removes the duplicate TF noise bank and
    # the sub-model/optimizer/weight-tensor scratch state before evaluation.
    del cam.class_weights_tensor, cam.noise_bank, cam.b3_optimizer
    del cam.b3_feature_extractor, cam.b3_classifier_head
    if hasattr(cam, "b3_model"):
        del cam.b3_model
    del noise_bank
    gc.collect()

    # ---- memory-efficient evaluation: one condition at a time ----
    val = np.load(ROOT / "data" / "processed" / "validation_beats.npz")
    X_val = val["X"]
    if X_val.ndim == 2:
        X_val = X_val[..., np.newaxis]
    y_val = val["y"].astype(np.int64)
    val.close()

    def metric_rows(y_true, y_pred, cond):
        p, r, f, s = precision_recall_fscore_support(
            y_true, y_pred, labels=[0, 1, 2, 3], zero_division=0)
        summary = {
            "Condition": cond, "Branch": f"EXP-{name}", "N": len(y_true),
            "Accuracy": float(accuracy_score(y_true, y_pred)),
            "Macro_Precision": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
            "Macro_Recall": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
            "Macro_F1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
            "Weighted_F1": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
            "checkpoint_sha256": ckpt_sha, "config_version": "B3-canonical-v1",
        }
        pc = []
        for i, c in enumerate(CLASS_NAMES):
            pc.append({"Condition": cond, "Branch": f"EXP-{name}", "Class": c,
                       "Precision": float(p[i]), "Recall": float(r[i]), "F1": float(f[i]),
                       "Support": int(s[i]), "checkpoint_sha256": ckpt_sha,
                       "config_version": "B3-canonical-v1"})
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1, 2, 3])
        cmr = []
        for i, c in enumerate(CLASS_NAMES):
            row = {"Condition": cond, "Branch": f"EXP-{name}", "True_Class": c,
                   "checkpoint_sha256": ckpt_sha, "config_version": "B3-canonical-v1"}
            row.update({f"Pred_{q}": int(cm[i, j]) for j, q in enumerate(CLASS_NAMES)})
            cmr.append(row)
        return summary, pc, cmr

    def predict_batches(x):
        """Direct batched forward pass; avoids model.predict's extra buffers."""
        out = np.empty((len(x), 4), dtype=np.float32)
        for i in range(0, len(x), eval_batch):
            j = min(i + eval_batch, len(x))
            out[i:j] = model(x[i:j], training=False).numpy()
        return out

    summaries, per_all, cm_all = [], [], []
    clean_pred = np.argmax(predict_batches(X_val), axis=1)
    s, pc, cmr = metric_rows(y_val, clean_pred, "clean")
    summaries.append(s); per_all.extend(pc); cm_all.extend(cmr)
    del clean_pred
    gc.collect()

    rng = np.random.default_rng(2027)
    for nname in ["bw", "ma"]:
        for snr in t.VAL_SNRS:
            # Preallocate ONE buffer and fill it beat-by-beat: no per-beat list,
            # no second contiguous copy, identical RNG sequence and values.
            cond = np.empty((len(X_val), 288, 1), dtype=np.float32)
            for k, beat in enumerate(X_val):
                start = rng.integers(t.VAL_START, t.VAL_END - 288 + 1)
                seg = signals[nname][start:start + 288]
                cond[k, :, 0] = noise.add_validation_noise(beat.squeeze(), seg, snr)
            pred = np.argmax(predict_batches(cond), axis=1)
            cond_label = f"{nname.upper()}@{snr}dB"
            s, pc, cmr = metric_rows(y_val, pred, cond_label)
            summaries.append(s); per_all.extend(pc); cm_all.extend(cmr)
            del cond, pred
            gc.collect()

    write_csv(rdir / "evaluation_summary.csv", summaries)
    write_csv(rdir / "evaluation_per_class.csv", per_all)
    write_csv(rdir / "evaluation_confusion_matrices.csv", cm_all)

    mean_noisy = float(np.mean([s["Macro_F1"] for s in summaries if s["Condition"] != "clean"]))
    result = {"branch": f"EXP-{name}", "lambda": lam, "mean_noisy_macro_f1": mean_noisy,
              "checkpoint_sha256": ckpt_sha, "training_time_min": minutes}
    (rdir / "branch_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    manifest = [{"file": str(p.relative_to(ROOT)).replace("\\", "/"),
                 "sha256": sha(p), "size_bytes": p.stat().st_size}
                for p in sorted(list(mdir.rglob("*")) + list(rdir.rglob("*"))) if p.is_file()]
    write_csv(rdir / "manifest_sha256.csv", manifest)

    print(f"EXP-{name} DONE | SHA256={ckpt_sha} | mean noisy Macro-F1={mean_noisy:.16f}")

    # release remaining TF resources before process exit
    del model, signals, X_val, y_val
    tf.keras.backend.clear_session()
    gc.collect()


def build_comparison(results):
    lines = ["# EXP-01 Lambda Ablation comparison", "",
             f"Generated: {datetime.now().isoformat(timespec='seconds')}", "",
             "| Branch | Lambda | Mean noisy Macro-F1 | Checkpoint SHA256 |",
             "|---|---:|---:|---|"]
    for r in results:
        lines.append(f"| {r['branch']} | {r['lambda']:.2f} | "
                     f"{r['mean_noisy_macro_f1']:.16f} | {r['checkpoint_sha256']} |")
    lines += ["", "Reference: E3 best 0.3644898279927664, E5 0.3542619613487781, "
              "E6 staged 0.3490763717675494.", "",
              "No checkpoint promoted. Test split sealed.", ""]
    p = REPORT_ROOT / "EXP01_comparison.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(lines), encoding="utf-8")
    print("comparison written:", p)


def main():
    ap = argparse.ArgumentParser(description="EXP-01 low-memory lambda ablation runner")
    ap.add_argument("--branch", choices=["A", "B", "C", "all"], default="all")
    ap.add_argument("--ram-min", type=float, default=3.0)
    ap.add_argument("--eval-batch-size", type=int, default=64)
    args = ap.parse_args()

    avail = available_ram_gb()
    print(f"Parent available RAM: {avail:.3f} GB (minimum {args.ram_min} GB)")
    if avail < args.ram_min:
        raise SystemExit(f"STOP: insufficient RAM ({avail:.3f} GB < {args.ram_min} GB). No branch executed.")

    if args.branch == "all":
        for b in ["A", "B", "C"]:
            cmd = [sys.executable, str(Path(__file__).resolve()),
                   "--branch", b, "--ram-min", str(args.ram_min),
                   "--eval-batch-size", str(args.eval_batch)]
            print("launching isolated process:", " ".join(cmd))
            subprocess.run(cmd, cwd=str(ROOT), check=True)
            gc.collect()
        results = []
        for b in ["A", "B", "C"]:
            lam = BRANCHES[b]
            rp = REPORT_ROOT / f"EXP-{b}_lambda{lam:.2f}" / "branch_result.json"
            results.append(json.loads(rp.read_text(encoding="utf-8")))
        build_comparison(results)
    else:
        run_branch(args.branch, BRANCHES[args.branch], args.ram_min, args.eval_batch)


if __name__ == "__main__":
    main()
