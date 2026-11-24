"""
ECG channel selection, filtering and beat extraction helpers (notebook 03).

Reusable helper module created during the local VS Code migration.
Functions below are copied verbatim from the original notebooks; the notebooks
remain self-contained and are the source of truth for the research methodology.
"""

import numpy as np

try:
    import wfdb
except ImportError:  # optional locally
    wfdb = None

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

from scipy.signal import butter, sosfiltfilt

from .config import LOWCUT, HIGHCUT, FILTER_ORDER

# Functions extracted from 03_ECG_Preprocessing_Beat_Extraction.ipynb

def select_ecg_channel(channels):

    channel_list = [ch.strip() for ch in channels.split(",")]

    if "MLII" in channel_list:
        return "MLII"
    elif "V5" in channel_list:
        return "V5"
    else:
        return None

def plot_selected_ecg(record_id):

    record_path = os.path.join(MITDB_DIR, str(record_id))

    signal, fields = wfdb.rdsamp(record_path)

    row = channel_audit_df[
        channel_audit_df["Record"].astype(str) == str(record_id)
    ].iloc[0]

    selected_channel = row["Selected_Channel"]
    channel_index = fields["sig_name"].index(selected_channel)

    ecg_signal = signal[:, channel_index]

    samples = 10 * FS

    plt.figure(figsize=(14, 4))

    plt.plot(
        np.arange(samples) / FS,
        ecg_signal[:samples]
    )

    plt.title(f"Record {record_id} - {selected_channel}")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude (mV)")
    plt.grid(True)
    plt.show()

def bandpass_filter(signal, fs=360):

    nyquist = fs / 2

    sos = butter(
        FILTER_ORDER,
        [LOWCUT, HIGHCUT],
        btype="bandpass",
        fs=fs,
        output="sos"
    )

    filtered_signal = sosfiltfilt(sos, signal)

    return filtered_signal.astype(np.float32)
