"""
Noise generation, SNR mixing and augmentation helpers (notebooks 04/06/07).

Reusable helper module created during the local VS Code migration.
Functions below are copied verbatim from the original notebooks; the notebooks
remain self-contained and are the source of truth for the research methodology.
"""

import numpy as np
try:
    import tensorflow as tf
except ImportError:  # optional: install requirements.txt to enable training helpers
    tf = None

from .config import TRAIN_SNRS, BEAT_LENGTH, TRAIN_START, TRAIN_END

# Runtime object supplied by the training notebook before calling augment_training_beat:
#   noise_bank : tf.Tensor of concatenated NSTDB noise records
# Noise/SNR functions from 04_ECG_Noise_Generation_and_SNR.ipynb and 07

def generate_powerline_noise(
    length,
    fs=360,
    frequency=50,
    amplitude=1.0,
    phase=None
):

    if phase is None:
        phase = np.random.uniform(0, 2 * np.pi)

    t = np.arange(length) / fs

    noise = amplitude * np.sin(
        2 * np.pi * frequency * t + phase
    )

    return noise

def extract_noise_segment(
    noise_type,
    split,
    length=BEAT_LENGTH,
    channel=0,
    seed=None
):

    if noise_type not in noise_signals:
        raise ValueError("Unknown noise type")

    if split not in NOISE_SPLIT_RANGES:
        raise ValueError("Unknown split")

    signal = noise_signals[noise_type][:, channel]

    start_region, end_region = NOISE_SPLIT_RANGES[split]

    if end_region - start_region < length:
        raise ValueError("Noise region is too short")

    rng = np.random.default_rng(seed)

    start = rng.integers(
        start_region,
        end_region - length + 1
    )

    segment = signal[start:start + length]

    return segment, start

def add_noise_at_snr(clean_signal, noise_segment, snr_db):

    clean_signal = np.asarray(
        clean_signal,
        dtype=np.float64
    )

    noise_segment = np.asarray(
        noise_segment,
        dtype=np.float64
    )

    if len(clean_signal) != len(noise_segment):
        raise ValueError("Signal and noise lengths must match")

    signal_power = np.mean(clean_signal ** 2)

    noise_power = np.mean(noise_segment ** 2)

    if signal_power <= 0 or noise_power <= 0:
        raise ValueError("Signal and noise power must be positive")

    target_noise_power = (
        signal_power / (10 ** (snr_db / 10))
    )

    scale = np.sqrt(
        target_noise_power / noise_power
    )

    scaled_noise = noise_segment * scale

    noisy_signal = clean_signal + scaled_noise

    return noisy_signal, scaled_noise

def add_powerline_noise(
    clean_signal,
    frequency,
    snr_db,
    fs=360,
    seed=None
):

    rng = np.random.default_rng(seed)

    phase = rng.uniform(0, 2 * np.pi)

    powerline = generate_powerline_noise(
        length=len(clean_signal),
        fs=fs,
        frequency=frequency,
        amplitude=1.0,
        phase=phase
    )

    noisy_signal, scaled_noise = add_noise_at_snr(
        clean_signal,
        powerline,
        snr_db
    )

    return noisy_signal, scaled_noise

def add_validation_noise(clean_signal, noise_segment, snr_db):

    clean_signal = np.asarray(clean_signal, dtype=np.float32)
    noise_segment = np.asarray(noise_segment, dtype=np.float32)

    noise_segment = noise_segment - np.mean(noise_segment)

    signal_power = np.mean(clean_signal ** 2)
    noise_power = np.mean(noise_segment ** 2)

    if signal_power <= 0 or noise_power <= 0:
        raise ValueError("Signal or noise power is zero!")

    target_noise_power = signal_power / (10 ** (snr_db / 10))

    scale = np.sqrt(target_noise_power / noise_power)

    noisy_signal = clean_signal + noise_segment * scale

    return noisy_signal

# Augmentation function from 06_Noise_Augmented_ResNet.ipynb

def augment_training_beat(ecg, label):

    ecg = tf.cast(ecg, tf.float32)

    # Convert (288, 1) to (288,)
    ecg = tf.squeeze(ecg, axis=-1)

    # Random noise type: 0=BW, 1=MA
    noise_index = tf.random.uniform(
        shape=[],
        minval=0,
        maxval=2,
        dtype=tf.int32
    )

    # Random noise segment
    start = tf.random.uniform(
        shape=[],
        minval=TRAIN_START,
        maxval=TRAIN_END - BEAT_LENGTH + 1,
        dtype=tf.int32
    )

    indices = tf.range(
        start,
        start + BEAT_LENGTH
    )

    noise = tf.gather(
        noise_bank[noise_index],
        indices
    )

    noise = noise - tf.reduce_mean(noise)

    # Random SNR
    snr_index = tf.random.uniform(
        shape=[],
        minval=0,
        maxval=len(TRAIN_SNRS),
        dtype=tf.int32
    )

    snr_db = tf.gather(
        tf.constant(TRAIN_SNRS, dtype=tf.float32),
        snr_index
    )

    signal_power = tf.reduce_mean(tf.square(ecg))
    noise_power = tf.reduce_mean(tf.square(noise))

    target_noise_power = (
        signal_power /
        tf.pow(10.0, snr_db / 10.0)
    )

    scale = tf.sqrt(
        target_noise_power /
        tf.maximum(noise_power, 1e-12)
    )

    noisy_ecg = ecg + noise * scale

    # Convert back to (288, 1)
    noisy_ecg = tf.expand_dims(noisy_ecg, axis=-1)

    return noisy_ecg, label
