#!/usr/bin/env bash
# GPU environment setup for B3 Epoch 6 (Linux / Colab).
# SAFE: creates a NEW virtual environment and verifies GPU + checkpoint loading.
#       It DOES NOT train, promote, evaluate test data or modify research files.
# Run from the PROJECT ROOT:
#   bash gpu_training/setup_gpu_environment.sh
set -euo pipefail

echo "=== B3 Epoch 6 GPU environment setup ==="
echo "NOTE: This script does not start training."

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"
VENV="$PROJECT_ROOT/.venv_gpu"

PY="${PYTHON_BIN:-python3}"
echo "Python: $($PY --version 2>&1)"
VER=$($PY -c 'import sys; print("%d.%d" % sys.version_info[:2])')
case "$VER" in
  3.10|3.11|3.12|3.13) ;;
  *) echo "ERROR: TensorFlow 2.21 needs Python 3.10-3.13 (got $VER)."; exit 1 ;;
esac

if [ ! -d "$VENV" ]; then
  echo "Creating isolated environment: $VENV"
  $PY -m venv "$VENV"
else
  echo "Reusing existing environment: $VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"
python -m pip install --upgrade pip
python -m pip install -r gpu_training/requirements_gpu.txt

echo "--- GPU verification ---"
python - <<'PY'
import tensorflow as tf
import keras
print("TensorFlow:", tf.__version__, "Keras:", keras.__version__)
gpus = tf.config.list_physical_devices("GPU")
print("GPU devices:", gpus)
if not gpus:
    raise SystemExit("ERROR: no GPU visible. Do not start Epoch 6 on CPU.")
PY

echo "--- Checkpoint integrity + load verification ---"
bash gpu_training/verify_transfer.sh

echo "--- Safe preflight (no writes) ---"
python train_b3_epoch6.py --dry-run
python train_b3_epoch6.py --smoke

echo "SETUP COMPLETE. Do not start training until the pre-training checklist is signed off."
