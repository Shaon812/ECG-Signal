"""
Research constants shared across notebooks (values taken from reports/*.json).

Reusable helper module created during the local VS Code migration.
Functions below are copied verbatim from the original notebooks; the notebooks
remain self-contained and are the source of truth for the research methodology.
"""

SEED = 2027

INPUT_SHAPE = (288, 1)
BEAT_LENGTH = 288
SAMPLING_FREQUENCY = 360
# Bandpass filter from notebook 03 cell 11
LOWCUT = 0.5
HIGHCUT = 40.0
FILTER_ORDER = 4
NUM_CLASSES = 4
CLASS_NAMES = ["N", "S", "V", "F"]

BATCH_SIZE = 32
LEARNING_RATE = 0.0001
LAMBDA_CAM = 0.1
EPOCHS_B3 = 10
EPOCHS_B4 = 10

TRAIN_SNRS = [24, 18, 12, 6]
VALIDATION_SNRS = [18, 12, 6]
TEST_SEEN_SNRS = [24, 18, 12, 6, 0]
TEST_UNSEEN_SNRS = [18, 12, 6, 0]
TEST_MIXED_SNRS = [12, 6, 0]
NOISE_TYPES = ["BW", "MA", "EM"]
POWERLINE_FREQUENCIES = [50, 60]
NOISE_CHANNEL = 0

SPLIT_RANGES = {
    "train": [0, 390000],
    "validation": [390000, 520000],
    "test": [520000, 650000],
}
TRAIN_START, TRAIN_END = SPLIT_RANGES["train"]
