# Migration Manifest

Generated: 2026-11-21

Backup taken before changes: `C:\Users\Lenovo\Downloads\ECG_QPAIN_2027_BACKUP_20261121_234617` (8 notebooks + reports/ + models/, 38 files, 13,633,952 bytes). Large datasets were not duplicated.

Detailed machine-readable manifest: `MIGRATION_MANIFEST.csv` (60 rows).

## Summary

| Category | Count | Action | Verification |
|---|---:|---|---|
| config | 1 | new (created) | see CSV |
| csv | 3 | unchanged (not copied, not moved - no dataset duplication) | see CSV |
| csv | 18 | unchanged (not copied, not moved) | see CSV |
| dataset | 4 | unchanged (not copied, not moved - no dataset duplication) | see CSV |
| ipynb | 8 | in-place (original retained; external backup copy made) | see CSV |
| json | 2 | new (created) | see CSV |
| json | 3 | unchanged (not copied, not moved) | see CSV |
| keras | 9 | unchanged (not copied, not moved) | see CSV |
| md | 1 | new (created) | see CSV |
| npz | 3 | unchanged (not copied, not moved - no dataset duplication) | see CSV |
| py | 7 | new (created) | see CSV |
| txt | 1 | new (created) | see CSV |

## Notable decisions

- Notebooks were **not moved or renamed**; only their setup/path cells were rewritten to use `src/ecg_qpain/paths.py`. Cell order, execution counts and stored outputs are unchanged.
- All checkpoints, backups, history files and datasets were left **byte-for-byte unchanged** (SHA256 verified).
- The B3 Epoch-4 vs Epoch-5 discrepancy is documented in `README.md` section 5; no research state was altered.
- No training (including Epoch 5) was started.
