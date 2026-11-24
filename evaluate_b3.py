"""
=============================================================================
 B3 EVALUATION UTILITY - separate, non-overwriting, checkpoint-agnostic
=============================================================================

Inspection/preparation only. This script NEVER trains, NEVER writes to any
existing checkpoint, history file, notebook or report. All outputs go to a NEW
timestamped folder under reports/evaluation/.

It reproduces the notebook 07 metric definition:
    val_macro_f1 = mean over 6 noisy validation conditions of
                   macro-F1 computed with sklearn f1_score(average="macro",
                   zero_division=0) on y_val.
and adds the metrics missing from the original B3 reporting:
    accuracy, macro/weighted precision, recall, F1,
    per-class precision/recall/F1/support, and confusion matrices.

Examples (run from project root with .venv active):

  # SAFE smoke check, tiny subset, NO files written:
  python evaluate_b3.py --limit 32 --no-write

  # Evaluate the official latest checkpoint on full noisy validation:
  python evaluate_b3.py --checkpoint models/B3_CAM_Consistency/latest_B3_resnet.keras

  # Evaluate a STAGED Epoch 6 checkpoint (no official file is touched):
  python evaluate_b3.py --checkpoint models/B3_CAM_Consistency/epoch6_latest.keras

  # Clean validation instead of noisy:
  python evaluate_b3.py --clean --checkpoint <path>

  # Patient-independent TEST evaluation requires explicit approval flag:
  python evaluate_b3.py --split test --approved-test --checkpoint <path>
=============================================================================
"""

import argparse
import csv
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import numpy as np
import tensorflow as tf
import wfdb
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
    precision_score,
    recall_score,
)

from ecg_qpain import paths, noise

CLASS_NAMES = ["N", "S", "V", "F"]      # 0=N, 1=S, 2=V, 3=F
VAL_SNRS = [18, 12, 6]
VAL_START, VAL_END = 390000, 520000
DEFAULT_CKPT = Path(paths.B3_DIR) / "latest_B3_resnet.keras"
CANONICAL_CONFIG = Path(paths.REPORTS_DIR) / "B3_training_config_canonical.json"


def checkpoint_sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def config_version():
    if CANONICAL_CONFIG.is_file():
        return json.loads(CANONICAL_CONFIG.read_text(encoding="utf-8"))["config_version"]
    return "UNKNOWN"


def load_split(name, limit=None):
    d = np.load(Path(paths.PROCESSED_DIR) / f"{name}_beats.npz")
    X = d["X"].astype(np.float32)
    y = d["y"].astype(np.int64)
    if X.ndim == 2:
        X = X[..., np.newaxis]
    if limit:
        X, y = X[:limit], y[:limit]
    return X, y


def build_noisy_validation(X_val, signals, snrs=VAL_SNRS):
    """Fixed noisy validation sets, seed 2027 (notebook 07 cell 67)."""
    rng = np.random.default_rng(2027)
    out = {}
    for name in ["bw", "ma"]:
        for snr in snrs:
            chunks = []
            for beat in X_val:
                start = rng.integers(VAL_START, VAL_END - 288 + 1)
                seg = signals[name][start:start + 288]
                chunks.append(noise.add_validation_noise(beat.squeeze(), seg, snr))
            out[(name, snr)] = np.asarray(chunks, dtype=np.float32)[..., np.newaxis]
    return out


def compute_metrics(y_true, y_pred):
    p, r, f, s = precision_recall_fscore_support(
        y_true, y_pred, labels=[0, 1, 2, 3], zero_division=0
    )
    return {
        "Accuracy": float(accuracy_score(y_true, y_pred)),
        "Macro_Precision": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "Macro_Recall": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "Macro_F1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "Weighted_F1": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        "per_class": [
            {"Class": CLASS_NAMES[i], "Precision": float(p[i]), "Recall": float(r[i]),
             "F1": float(f[i]), "Support": int(s[i])}
            for i in range(4)
        ],
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=[0, 1, 2, 3]),
    }


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing report: {path}")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description="B3 evaluation (no training, no overwrites)")
    ap.add_argument("--checkpoint", default=str(DEFAULT_CKPT), help="checkpoint to evaluate")
    ap.add_argument("--split", choices=["validation", "test"], default="validation")
    ap.add_argument("--approved-test", action="store_true", help="required for --split test")
    ap.add_argument("--clean", action="store_true", help="evaluate clean instead of noisy validation")
    ap.add_argument("--limit", type=int, default=None, help="use first N samples (smoke tests)")
    ap.add_argument("--no-write", action="store_true", help="print metrics only, write no files")
    args = ap.parse_args()

    if args.split == "test" and not args.approved_test:
        raise RuntimeError("Patient-independent TEST evaluation requires --approved-test.")
    ckpt = Path(args.checkpoint)
    if not ckpt.is_file():
        raise FileNotFoundError(ckpt)

    ckpt_sha = checkpoint_sha256(ckpt)
    cfg_ver = config_version()
    model = tf.keras.models.load_model(str(ckpt), compile=False)
    print(f"Checkpoint: {ckpt}")
    print(f"Checkpoint SHA256: {ckpt_sha}")
    print(f"Configuration version: {cfg_ver}")
    print(f"Input/Output: {model.input_shape} -> {model.output_shape}; params={model.count_params()}")

    X, y = load_split(args.split, args.limit)
    conditions = {}
    if args.clean or args.split == "test":
        conditions["clean"] = X
    else:
        signals = {}
        for rid in ["bw", "ma"]:
            sig, _ = wfdb.rdsamp(str(Path(paths.NSTDB_EXTRACTED) / rid))
            signals[rid] = sig[:, 0].astype(np.float32)
        conditions = build_noisy_validation(X, signals)

    results = []
    full_metrics = []
    for label, data in conditions.items():
        pred = np.argmax(model.predict(data, batch_size=128, verbose=0), axis=1)
        m = compute_metrics(y, pred)
        name = "clean" if label == "clean" else f"{label[0].upper()}@{label[1]}dB"
        row = {"Condition": name, "N": len(y),
               "Accuracy": m["Accuracy"], "Macro_Precision": m["Macro_Precision"],
               "Macro_Recall": m["Macro_Recall"], "Macro_F1": m["Macro_F1"],
               "Weighted_F1": m["Weighted_F1"],
               "checkpoint_sha256": ckpt_sha, "config_version": cfg_ver}
        results.append(row)
        full_metrics.append((row["Condition"], m))
        print("\n" + "=" * 70)
        print(name, row)
        print("per-class:", m["per_class"])
        print("confusion matrix (rows=true N,S,V,F; cols=pred N,S,V,F):")
        print(m["confusion_matrix"])

    mean_f1 = None
    if not args.clean and args.split == "validation" and not args.limit:
        mean_f1 = float(np.mean([r["Macro_F1"] for r in results]))
        print(f"\nMean noisy-validation Macro-F1 (notebook 07 definition): {mean_f1:.16f}")
        results.append({"Condition": "MEAN_NOISY_6_CONDITIONS", "N": sum(r["N"] for r in results),
                        "Accuracy": "", "Macro_Precision": "", "Macro_Recall": "",
                        "Macro_F1": mean_f1, "Weighted_F1": "",
                        "checkpoint_sha256": ckpt_sha, "config_version": cfg_ver})

    if args.no_write:
        print("\n--no-write: no report files created.")
        return

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outdir = Path(paths.REPORTS_DIR) / "evaluation"
    base = f"B3_eval_{ckpt.stem}_{stamp}"
    write_csv(outdir / f"{base}_summary.csv", results)
    per_class = []
    for label, m in full_metrics:
        for pc in m["per_class"]:
            per_class.append({"Condition": label, **pc,
                              "checkpoint_sha256": ckpt_sha, "config_version": cfg_ver})
    write_csv(outdir / f"{base}_per_class.csv", per_class)

    cm_rows = []
    for label, m in full_metrics:
        for i, true_name in enumerate(CLASS_NAMES):
            row = {"Condition": label, "True_Class": true_name,
                   "checkpoint_sha256": ckpt_sha, "config_version": cfg_ver}
            row.update({f"Pred_{pred_name}": int(m["confusion_matrix"][i, j])
                        for j, pred_name in enumerate(CLASS_NAMES)})
            cm_rows.append(row)
    write_csv(outdir / f"{base}_confusion_matrices.csv", cm_rows)
    print("\nReports written to", outdir)


if __name__ == "__main__":
    main()
