"""
Portable project paths (Windows / Linux / Colab compatible).

Reusable helper module created during the local VS Code migration.
Functions below are copied verbatim from the original notebooks; the notebooks
remain self-contained and are the source of truth for the research methodology.
"""

from pathlib import Path

# This file lives at <project>/src/ecg_qpain/paths.py -> parents[2] is the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Path objects (use where the original notebooks do ``ROOT / "subdir"``)
ROOT = PROJECT_ROOT

# String aliases (use where the original notebooks do ``os.path.join(BASE_DIR, ...)``)
BASE_DIR = str(PROJECT_ROOT)
PROJECT_DIR = str(PROJECT_ROOT)
DRIVE_DIR = str(PROJECT_ROOT)      # local stand-in for Colab's "/content/drive/MyDrive"
MYDRIVE = str(PROJECT_ROOT)
MOUNT_POINT = str(PROJECT_ROOT)    # local stand-in for the old Colab mount point
mount_path = str(PROJECT_ROOT)

DATA_DIR = str(PROJECT_ROOT / "data")
RAW_DIR = str(PROJECT_ROOT / "data" / "raw")
PROCESSED_DIR = str(PROJECT_ROOT / "data" / "processed")
INTERIM_DIR = str(PROJECT_ROOT / "data" / "interim")
MODELS_DIR = str(PROJECT_ROOT / "models")
REPORTS_DIR = str(PROJECT_ROOT / "reports")

MITDB_DIR = str(PROJECT_ROOT / "data" / "raw" / "mitdb")
NSTDB_DIR = str(PROJECT_ROOT / "data" / "raw" / "nstdb")
MITDB_EXTRACTED = str(
    PROJECT_ROOT / "data" / "raw" / "mitdb" / "mit-bih-arrhythmia-database-1.0.0"
)
NSTDB_EXTRACTED = str(
    PROJECT_ROOT / "data" / "raw" / "nstdb" / "mit-bih-noise-stress-test-database-1.0.0"
)

B2_DIR = str(PROJECT_ROOT / "models" / "B2_Noise_Augmented_ResNet")
B3_DIR = str(PROJECT_ROOT / "models" / "B3_CAM_Consistency")
B4_DIR = str(PROJECT_ROOT / "models" / "B4_Gated_CAM_Consistency")


def ensure_project_folders():
    """Create the standard project folders if they are missing (safe/idempotent)."""
    for p in (DATA_DIR, RAW_DIR, PROCESSED_DIR, INTERIM_DIR, MODELS_DIR,
              REPORTS_DIR, B3_DIR, B4_DIR):
        Path(p).mkdir(parents=True, exist_ok=True)
