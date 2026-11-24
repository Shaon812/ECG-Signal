#!/usr/bin/env bash
# Safe checkpoint transfer verification. Read-only: computes SHA256 and compares
# with values from reports/checkpoint_registry.csv. Does not copy, move or write.
# Run from the PROJECT ROOT: bash gpu_training/verify_transfer.sh
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

check_hash () {
  local file="$1" expected="$2"
  if [ ! -f "$file" ]; then
    echo "FAIL missing: $file"; exit 1
  fi
  local actual
  actual="$(sha256sum "$file" | awk '{print $1}')"
  if [ "$actual" != "$expected" ]; then
    echo "FAIL hash mismatch: $file"
    echo "  expected $expected"
    echo "  actual   $actual"
    exit 1
  fi
  echo "PASS $file  $actual"
}

echo "=== checkpoint SHA256 verification ==="
check_hash "models/B3_CAM_Consistency/latest_B3_resnet.keras" \
  "f26d0a5fd8dacaa2c81a2b386f6189bcefadfbac475a356fb1b2b441462c2c32"
check_hash "models/B3_CAM_Consistency/best_B3_resnet.keras" \
  "610caadeba6fe31d396efacfd802eac3a156a0671a66baa8fe89f9f42b71ac3c"
check_hash "models/B3_CAM_Consistency/initial_B3_from_B2.keras" \
  "cbd39b6934b4504e893515b61168c77e4b50dbcb42295c8e7d9017f4ccf4fb21"
check_hash "models/B3_CAM_Consistency/backups/latest_epoch4_20261121_163837.keras" \
  "722502595f28ef8c5b63afac37815b27dd896f8ea2c74a6c68cc32f513c36298"
check_hash "models/B3_CAM_Consistency/backups/best_epoch4_20261121_163837.keras" \
  "610caadeba6fe31d396efacfd802eac3a156a0671a66baa8fe89f9f42b71ac3c"
echo "ALL CHECKPOINT HASHES VERIFIED"
