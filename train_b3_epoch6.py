"""
=============================================================================
 B3 EPOCH 6 CONTINUATION - SAFETY-GUARDED TRAINING SCRIPT
=============================================================================

Project: ECG_QPAIN_2027
Purpose: Continue B3 (ResNet + CAM Consistency) from the current
         latest_B3_resnet.keras, which the read-only readiness assessment
         identified as the Epoch 5 checkpoint.

*** THIS SCRIPT DOES NOT START TRAINING BY DEFAULT. ***

Usage (from the project root, inside .venv):

  1) Smoke test (SAFE, no writes, one in-memory step on batch 4):
        python train_b3_epoch6.py --smoke

  2) Show the exact configuration without training (no writes):
        python train_b3_epoch6.py --dry-run

  3) On a SUITABLE GPU - full Epoch 6 writing STAGING files only:
        python train_b3_epoch6.py --train

  4) After reviewing staging results - promote them to official files:
        python train_b3_epoch6.py --commit

Safety properties:
  * Modes --smoke and --dry-run never write any file.
  * --train writes ONLY new staging files:
        models/B3_CAM_Consistency/epoch6_latest.keras
        reports/B3_training_history_epoch6.csv
    It NEVER overwrites latest_B3_resnet.keras, best_B3_resnet.keras,
    the Epoch 4 backups, or reports/B3_training_history.csv.
  * --commit does NOT train. It verifies the staging results, creates a
    timestamped backup of all official files, and only then promotes the
    staging results via atomic os.replace().
  * best_B3_resnet.keras is only promoted by --commit if validation
    Macro-F1 improves on the historical best (0.3644898279927664).
  * Full training is REFUSED unless a GPU is visible or --allow-cpu is given.
  * Optimizer state was not saved in the checkpoints; Adam is intentionally
    re-created fresh (learning_rate=0.0001). This is a weight-only warm start.

Methodology is copied from notebook 07 (cells 9, 15/19, 65/67, 133/135,
175, 178, 179). The original notebooks are unchanged.
=============================================================================
"""

import argparse
import hashlib
import json
import os
import random
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import numpy as np
import tensorflow as tf
import wfdb
from sklearn.utils.class_weight import compute_class_weight

from ecg_qpain import paths, config, cam, noise

# Global seeds, matching notebook 07 (SEED = 2027). Required for reproducible
# tf.random noise augmentation in addition to the op-level tf.data shuffle seed.
random.seed(config.SEED)
np.random.seed(config.SEED)
tf.random.set_seed(config.SEED)

# ------------------------------------------------------------------ constants
CANONICAL_CONFIG = Path(paths.REPORTS_DIR) / "B3_training_config_canonical.json"
BATCH_SIZE = 128                 # actual epochs 4-5 value (config JSON says 32)
LEARNING_RATE = 0.0001
LAMBDA_CAM = 0.1
EPOCH_NUMBER = 6
HISTORY_PATH = Path(paths.REPORTS_DIR) / "B3_training_history.csv"
LATEST_PATH = Path(paths.B3_DIR) / "latest_B3_resnet.keras"
BEST_PATH = Path(paths.B3_DIR) / "best_B3_resnet.keras"

STAGING_LATEST = Path(paths.B3_DIR) / "epoch6_latest.keras"
STAGING_HISTORY = Path(paths.REPORTS_DIR) / "B3_training_history_epoch6.csv"
STAGING_BEST = Path(paths.B3_DIR) / "epoch6_best_candidate.keras"

EXPECTED = {
    "latest_B3_resnet.keras": "f26d0a5fd8dacaa2c81a2b386f6189bcefadfbac475a356fb1b2b441462c2c32",
    "best_B3_resnet.keras": "610caadeba6fe31d396efacfd802eac3a156a0671a66baa8fe89f9f42b71ac3c",
    "backups/latest_epoch4_20261121_163837.keras": "722502595f28ef8c5b63afac37815b27dd896f8ea2c74a6c68cc32f513c36298",
    "backups/best_epoch4_20261121_163837.keras": "610caadeba6fe31d396efacfd802eac3a156a0671a66baa8fe89f9f42b71ac3c",
}
EXPECTED_HISTORY_ROWS = 5
EXPECTED_TRAIN_BATCHES = 467
BEST_F1_THRESHOLD = 0.3644898279927664   # verified Epoch 3 best (noisy 6-condition mean)
VAL_SNRS = [18, 12, 6]
VAL_START, VAL_END = 390000, 520000


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_save(model, target):
    """Save to a temporary sibling then atomically replace the target."""
    tmp = str(target).replace(".keras", "_temp.keras")
    model.save(tmp)
    os.replace(tmp, str(target))


def check(condition, label):
    print(("  PASS  " if condition else "  FAIL  ") + label)
    if not condition:
        raise RuntimeError("Precondition failed: " + label)


# ------------------------------------------------------------------ verification
def verify_canonical_config():
    """Fail fast if this script's settings drift from the canonical B3 config."""
    check(CANONICAL_CONFIG.is_file(), "canonical config exists")
    cfg = json.loads(CANONICAL_CONFIG.read_text(encoding="utf-8"))
    check(cfg["config_version"] == "B3-canonical-v1", "config_version == B3-canonical-v1")
    check(cfg["batch_size"] == BATCH_SIZE, f"canonical batch_size == {BATCH_SIZE}")
    check(abs(cfg["learning_rate"] - LEARNING_RATE) < 1e-12, "canonical learning_rate == 0.0001")
    check(abs(cfg["lambda_cam"] - LAMBDA_CAM) < 1e-12, "canonical lambda_cam == 0.1")
    check(cfg["random_seed"] == config.SEED == 2027, "canonical random_seed == 2027")
    check(cfg["noise_seed"] == 2027, "canonical noise_seed == 2027")
    check(cfg["noise_types"] == ["BW", "MA"], "canonical noise_types == BW/MA")
    check(cfg["noise_snr_db_validation"] == VAL_SNRS == [18, 12, 6], "canonical validation SNRs == 18/12/6")
    check(cfg["optimizer"]["state_restored"] is False, "canonical optimizer state_restored == False")
    check(cfg["bandpass_filter"] == {"lowcut_hz": 0.5, "highcut_hz": 40.0, "order": 4},
          "canonical bandpass filter == 0.5-40 Hz order 4")


def verify_preconditions(verbose=True):
    print("=" * 78)
    print("EPOCH 6 PRECONDITION VERIFICATION")
    print("=" * 78)

    verify_canonical_config()

    for name, expected in EXPECTED.items():
        p = Path(paths.B3_DIR) / name
        check(p.is_file(), f"exists: {name}")
        actual = sha256(p)
        check(actual == expected, f"SHA256 of {name} == {expected[:12]}...")
        if verbose:
            print(f"          actual: {actual}")

    check(HISTORY_PATH.is_file(), "history file exists")
    with open(HISTORY_PATH, encoding="utf-8") as f:
        lines = [l for l in f.read().splitlines() if l.strip()]
    rows = lines[1:]
    check(len(rows) == EXPECTED_HISTORY_ROWS, f"history has {EXPECTED_HISTORY_ROWS} rows (got {len(rows)})")
    last_epoch = int(rows[-1].split(",")[0])
    check(last_epoch == 5, f"last recorded epoch is 5 (got {last_epoch})")
    check(config.LAMBDA_CAM == LAMBDA_CAM, "config LAMBDA_CAM == 0.1")
    check(config.LEARNING_RATE == LEARNING_RATE, "config LEARNING_RATE == 0.0001")

    # architecture / function checks
    model = tf.keras.models.load_model(str(LATEST_PATH), compile=False)
    check(tuple(model.input_shape[1:]) == (288, 1), "model input (None, 288, 1)")
    check(tuple(model.output_shape[1:]) == (4,), "model output (None, 4)")
    check(model.count_params() == 194020, "model has 194020 parameters")
    check(any(l.name == "activation_6" for l in model.layers), "layer activation_6 exists")
    for fn in ["create_cam_components", "differentiable_cam_for_model",
               "weighted_ce_loss", "calculate_b3_loss", "train_b3_step",
               "evaluate_noisy_validation"]:
        check(callable(getattr(cam, fn, None)), f"cam function available: {fn}")
    check(callable(getattr(noise, "add_validation_noise", None)),
          "noise.add_validation_noise available")
    for rel in ["data/processed/train_beats.npz", "data/processed/validation_beats.npz",
                "data/processed/test_beats.npz", "reports/noise_generation_config.json",
                "reports/B3_B4_experiment_config.json",
                "data/raw/nstdb/mit-bih-noise-stress-test-database-1.0.0"]:
        check((PROJECT_ROOT / rel).exists(), f"path exists: {rel}")
    print("=" * 78)
    return model


# ------------------------------------------------------------------ runtime setup
def build_runtime(model, include_validation=True):
    """Build datasets, noise bank, validation sets and original loss/training state."""
    train = np.load(Path(paths.PROCESSED_DIR) / "train_beats.npz")
    val = np.load(Path(paths.PROCESSED_DIR) / "validation_beats.npz")

    X_train = train["X"].astype(np.float32)[..., np.newaxis]
    y_train = train["y"].astype(np.int64)
    X_val = val["X"].astype(np.float32)[..., np.newaxis]
    y_val = val["y"].astype(np.int64)
    check(X_train.shape[1:] == (288, 1) and X_val.shape[1:] == (288, 1), "dataset shapes (N,288,1)")

    train_dataset = (tf.data.Dataset.from_tensor_slices((X_train, y_train))
                     .shuffle(10000, seed=2027)
                     .batch(BATCH_SIZE)
                     .prefetch(tf.data.AUTOTUNE))
    check(len(train_dataset) == EXPECTED_TRAIN_BATCHES,
          f"dataset has {EXPECTED_TRAIN_BATCHES} batches (got {len(train_dataset)})")

    # Noise bank exactly as notebook 07: BW and MA, channel 0, float32
    signals = {}
    for rid in ["bw", "ma"]:
        sig, _ = wfdb.rdsamp(str(Path(paths.NSTDB_EXTRACTED) / rid))
        signals[rid] = sig[:, 0].astype(np.float32)
    noise_bank = tf.constant(np.stack([signals["bw"], signals["ma"]]), dtype=tf.float32)
    check(tuple(noise_bank.shape) == (2, 650000), "noise bank shape (2, 650000)")

    # Fixed noisy validation sets, seed 2027 (notebook 07 cell 67).
    # Skipped in smoke mode to conserve RAM; training mode builds all 6 copies.
    X_val_noisy = {}
    if include_validation:
        rng = np.random.default_rng(2027)
        for name in ["bw", "ma"]:
            for snr in VAL_SNRS:
                chunks = []
                for beat in X_val:
                    start = rng.integers(VAL_START, VAL_END - 288 + 1)
                    seg = signals[name][start:start + 288]
                    chunks.append(noise.add_validation_noise(beat.squeeze(), seg, snr))
                X_val_noisy[(name, snr)] = np.asarray(chunks, dtype=np.float32)[..., np.newaxis]
        check(len(X_val_noisy) == 6, "6 noisy validation conditions")

    cw = compute_class_weight(class_weight="balanced", classes=np.array([0, 1, 2, 3]), y=y_train)
    class_weights_tensor = tf.constant(cw, dtype=tf.float32)

    # Runtime globals expected by the original helper functions
    cam.class_weights_tensor = class_weights_tensor
    cam.noise_bank = noise_bank
    cam.b3_model = model
    cam.b3_optimizer = tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE)  # FRESH
    cam.b3_feature_extractor, cam.b3_classifier_head = cam.create_cam_components(model)
    cam.X_val_noisy = X_val_noisy
    cam.y_val = y_val

    print(f"  class weights: {np.round(cw, 6).tolist()}")
    print(f"  train batches: {len(train_dataset)} | batch size: {BATCH_SIZE}")
    print(f"  Adam iterations at construction: {int(cam.b3_optimizer.iterations.numpy())}")
    return train_dataset, X_train, y_train, X_val, y_val, X_val_noisy


# ------------------------------------------------------------------ modes
def run_smoke():
    base_hashes = {p: sha256(p) for p in
                   [LATEST_PATH, BEST_PATH, HISTORY_PATH] +
                   [Path(paths.B3_DIR) / "backups" / n for n in
                    ["latest_epoch4_20261121_163837.keras",
                     "best_epoch4_20261121_163837.keras",
                     "history_epoch4_20261121_163837.csv"]]}

    model = verify_preconditions()
    print("\nSMOKE MODE: loading model + one in-memory step on batch 4 (NO WRITES)")
    temp_model = tf.keras.models.clone_model(model)
    temp_model.set_weights(model.get_weights())
    del model
    build_runtime(temp_model, include_validation=False)  # fresh optimizer; no 135 MB validation copies

    val = np.load(Path(paths.PROCESSED_DIR) / "validation_beats.npz")
    x = tf.constant(val["X"][:4][..., None].astype(np.float32))
    y = tf.constant(val["y"][:4].astype(np.int32))
    del val
    before = [v.numpy().copy() for v in temp_model.trainable_variables]
    total, ce, cl = cam.train_b3_step(x, y)
    changed = sum(int(np.any(a != b)) for a, b in zip(before, [v.numpy() for v in temp_model.trainable_variables]))
    for name, v in [("total", total), ("ce", ce), ("cam", cl)]:
        val = float(v.numpy())
        check(np.isfinite(val), f"smoke {name} loss finite ({val:.8f})")
    check(changed > 0, f"temporary model weights updated ({changed}/{len(before)} arrays)")

    for p, h in base_hashes.items():
        check(sha256(p) == h, f"unchanged after smoke: {p.name}")
    print("\nSMOKE TEST COMPLETE - official artifacts untouched.")


def run_dry_run():
    verify_preconditions()
    print("\nDRY RUN - EPOCH 6 CONFIGURATION (no writes, no training)")
    print(json.dumps({
        "epoch": EPOCH_NUMBER,
        "start_weights": str(LATEST_PATH),
        "start_weights_sha256": EXPECTED["latest_B3_resnet.keras"],
        "batch_size": BATCH_SIZE,
        "learning_rate": LEARNING_RATE,
        "lambda_cam": LAMBDA_CAM,
        "optimizer": "Adam (FRESH - no saved optimizer state)",
        "train_batches": EXPECTED_TRAIN_BATCHES,
        "train_samples": 59720,
        "validation_conditions": ["bw@18", "bw@12", "bw@6", "ma@18", "ma@12", "ma@6"],
        "initial_history_rows": EXPECTED_HISTORY_ROWS,
        "staging_outputs": [str(STAGING_LATEST), str(STAGING_HISTORY)],
        "official_files_modified": False,
    }, indent=2))


def run_training(allow_cpu=False):
    gpu = tf.config.list_physical_devices("GPU")
    if not gpu and not allow_cpu:
        raise RuntimeError(
            "No GPU detected. Full Epoch 6 requires a suitable GPU. "
            "Re-run on a GPU machine, or pass --allow-cpu only if you accept a very long runtime."
        )
    model = verify_preconditions()
    train_dataset, X_train, y_train, X_val, y_val, _ = build_runtime(model)

    import csv
    with open(HISTORY_PATH, encoding="utf-8") as f:
        history = list(csv.DictReader(f))
    check(len(history) == 5 and int(history[-1]["epoch"]) == 5, "history ready for epoch 6")
    best_f1 = max(float(r["val_macro_f1"]) for r in history)
    print(f"  historical best Macro-F1: {best_f1:.16f}")

    print(f"\nSTARTING EPOCH {EPOCH_NUMBER} (batch={BATCH_SIZE}, lr={LEARNING_RATE}, lambda={LAMBDA_CAM})")
    start = time.time()
    losses = cam.train_one_epoch(cam.train_b3_step, train_dataset, model, "B3")
    train_minutes = (time.time() - start) / 60
    val_f1 = cam.evaluate_noisy_validation(model)

    history.append({
        "epoch": EPOCH_NUMBER,
        "train_loss": losses["train_loss"],
        "train_ce_loss": losses["train_ce_loss"],
        "train_cam_loss": losses["train_cam_loss"],
        "training_time_min": train_minutes,
        "val_macro_f1": val_f1,
    })
    print(f"Epoch 6 val Macro-F1: {val_f1:.16f}")

    # ALWAYS write staging outputs; official files are NEVER touched by --train.
    atomic_save(model, STAGING_LATEST)
    with open(STAGING_HISTORY, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(history[0].keys()))
        w.writeheader()
        w.writerows(history)
    if val_f1 > best_f1:
        atomic_save(model, STAGING_BEST)
    print("Staging files written:", STAGING_LATEST.name, STAGING_HISTORY.name)
    print("\nOfficial checkpoints and history were NOT modified.")
    print("Review staging results, then run: python train_b3_epoch6.py --commit")


def run_commit():
    """Promote verified staging outputs to official files. Does NOT train."""
    print("=" * 78)
    print("COMMIT MODE - promoting Epoch 6 staging outputs (NO training)")
    print("=" * 78)
    check(STAGING_LATEST.is_file(), "staging latest exists")
    check(STAGING_HISTORY.is_file(), "staging history exists")

    # Re-verify official preconditions before replacing them.
    verify_preconditions(verbose=False)

    import csv
    with open(STAGING_HISTORY, encoding="utf-8") as f:
        staged = list(csv.DictReader(f))
    check(len(staged) == 6 and int(staged[-1]["epoch"]) == 6,
          "staging history has 6 rows ending at epoch 6")
    epoch6_score = float(staged[-1]["val_macro_f1"])
    improved = epoch6_score > BEST_F1_THRESHOLD
    print(f"  Epoch 6 mean noisy Macro-F1: {epoch6_score:.16f}")
    print(f"  Historical best threshold  : {BEST_F1_THRESHOLD:.16f}")
    # Guards against a stale epoch6_best_candidate.keras from an earlier run.
    check(STAGING_BEST.is_file() == improved,
          "best-candidate presence matches the score threshold")
    staged_model = tf.keras.models.load_model(str(STAGING_LATEST), compile=False)
    check(staged_model.count_params() == 194020, "staging model has 194020 params")
    del staged_model

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bdir = Path(paths.B3_DIR) / "backups"
    for p in [LATEST_PATH, BEST_PATH, HISTORY_PATH]:
        shutil.copy2(p, bdir / f"{p.stem}_pre_epoch6_{stamp}{p.suffix}")
    print("Pre-epoch6 backups created in", bdir)

    os.replace(str(STAGING_LATEST), str(LATEST_PATH))
    os.replace(str(STAGING_HISTORY), str(HISTORY_PATH))
    print("Official latest_B3_resnet.keras and B3_training_history.csv promoted.")
    if improved:
        os.replace(str(STAGING_BEST), str(BEST_PATH))
        print("New best checkpoint promoted (validation improved).")
    else:
        print("best_B3_resnet.keras preserved (no improvement).")


def main():
    ap = argparse.ArgumentParser(description="Safety-guarded B3 Epoch 6 continuation")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--smoke", action="store_true", help="SAFE: verify + one in-memory step, no writes (default)")
    mode.add_argument("--dry-run", action="store_true", help="verify + print config, no writes, no training")
    mode.add_argument("--train", action="store_true", help="FULL Epoch 6 -> staging outputs only")
    mode.add_argument("--commit", action="store_true", help="promote verified staging outputs (NO training)")
    ap.add_argument("--allow-cpu", action="store_true", help="allow full training without a GPU (slow)")
    args = ap.parse_args()

    if args.commit:
        run_commit()
    elif args.train:
        run_training(allow_cpu=args.allow_cpu)
    elif args.dry_run:
        run_dry_run()
    else:
        run_smoke()


if __name__ == "__main__":
    main()
