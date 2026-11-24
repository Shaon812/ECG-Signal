"""
CAM consistency / gated CAM training and evaluation helpers (notebook 07).

Reusable helper module created during the local VS Code migration.
Functions below are copied verbatim from the original notebooks; the notebooks
remain self-contained and are the source of truth for the research methodology.
"""

import time
import numpy as np
try:
    import tensorflow as tf
except ImportError:  # optional: install requirements.txt to enable training helpers
    tf = None

try:
    from sklearn.metrics import f1_score
except ImportError:
    f1_score = None

from .config import (
    LAMBDA_CAM, TRAIN_START, TRAIN_END, BEAT_LENGTH, TRAIN_SNRS,
)

# Runtime objects supplied by notebook 07 before calling these helpers:
#   b3_model, b3_optimizer, b3_feature_extractor, b3_classifier_head
#   b4_model, b4_optimizer, b4_feature_extractor, b4_classifier_head
#   class_weights_tensor, X_val_noisy, y_val
# Functions extracted from 07_CAM_Consistency_Models.ipynb

def generate_gradcam(model, input_signal, class_index=None):

    input_signal = tf.convert_to_tensor(
        input_signal,
        dtype=tf.float32
    )

    if len(input_signal.shape) == 2:
        input_signal = tf.expand_dims(input_signal, axis=0)

    with tf.GradientTape() as tape:

        conv_outputs, predictions = model(
            input_signal,
            training=False
        )

        if class_index is None:
            class_index = tf.argmax(predictions[0])

        class_score = predictions[:, class_index]

    gradients = tape.gradient(
        class_score,
        conv_outputs
    )

    if gradients is None:
        raise ValueError("Grad-CAM gradients are None!")

    weights = tf.reduce_mean(
        gradients,
        axis=1,
        keepdims=True
    )

    cam = tf.reduce_sum(
        conv_outputs * weights,
        axis=-1
    )

    cam = tf.nn.relu(cam)

    # Normalize CAM
    cam_max = tf.reduce_max(
        cam,
        axis=1,
        keepdims=True
    )

    cam = cam / (cam_max + 1e-8)

    # Correct 1D CAM resizing
    cam = cam[:, :, tf.newaxis, tf.newaxis]

    cam = tf.image.resize(
        cam,
        size=(288, 1),
        method="bilinear"
    )

    cam = tf.squeeze(cam, axis=[2, 3])

    return cam.numpy(), predictions.numpy()

def differentiable_cam(x, labels):

    with tf.GradientTape() as inner_tape:

        # Extract intermediate features
        features = feature_extractor(
            x,
            training=True
        )

        # Watch features BEFORE classifier calculation
        inner_tape.watch(features)

        # Calculate predictions from features
        predictions = classifier_head(
            features,
            training=True
        )

        # Select true class scores
        class_scores = tf.gather(
            predictions,
            labels,
            axis=1,
            batch_dims=1
        )

        total_score = tf.reduce_sum(class_scores)

    gradients = inner_tape.gradient(
        total_score,
        features
    )

    if gradients is None:
        raise ValueError("CAM gradients are still None!")

    weights = tf.reduce_mean(
        gradients,
        axis=1,
        keepdims=True
    )

    cam = tf.reduce_sum(
        features * weights,
        axis=-1
    )

    cam = tf.nn.relu(cam)

    cam = cam / (
        tf.reduce_max(cam, axis=1, keepdims=True) + 1e-8
    )

    cam = cam[:, :, tf.newaxis, tf.newaxis]

    cam = tf.image.resize(
        cam,
        size=(288, 1),
        method="bilinear"
    )

    cam = tf.squeeze(cam, axis=[2, 3])

    return cam, predictions

def cam_consistency_loss(clean_cam, noisy_cam):

    return tf.reduce_mean(
        tf.square(clean_cam - noisy_cam)
    )

def noise_severity_gate(snr_db):

    severity = (24.0 - snr_db) / 18.0

    return tf.clip_by_value(
        severity, 0.0, 1.0
    )

def create_cam_components(model):

    feature_extractor = tf.keras.Model(
        inputs=model.inputs,
        outputs=model.get_layer("activation_6").output
    )

    classifier_head = tf.keras.Model(
        inputs=model.get_layer("activation_6").output,
        outputs=model.output
    )

    return feature_extractor, classifier_head

def differentiable_cam_for_model(
    x, labels, feature_extractor, classifier_head
):
    x = tf.cast(x, tf.float32)
    labels = tf.cast(labels, tf.int32)

    with tf.GradientTape() as tape:

        features = feature_extractor(x, training=False)
        tape.watch(features)

        predictions = classifier_head(
            features, training=False
        )

        indices = tf.stack(
            [
                tf.range(tf.shape(labels)[0]),
                labels
            ],
            axis=1
        )

        target_scores = tf.gather_nd(
            predictions, indices
        )

        # IMPORTANT: Keep this operation inside GradientTape
        target_score_sum = tf.reduce_sum(target_scores)

    gradients = tape.gradient(
        target_score_sum, features
    )

    if gradients is None:
        raise ValueError(
            "CAM gradients are None. Check model connectivity."
        )

    pooled_gradients = tf.reduce_mean(
        gradients, axis=1, keepdims=True
    )

    cam = tf.reduce_sum(
        features * pooled_gradients,
        axis=-1
    )

    cam = tf.nn.relu(cam)

    cam_max = tf.reduce_max(
        cam, axis=1, keepdims=True
    )

    cam = cam / tf.maximum(cam_max, 1e-8)

    # Resize while preserving batch dimension
    cam = cam[:, :, tf.newaxis, tf.newaxis]

    cam = tf.image.resize(
        cam,
        size=(288, 1)
    )

    cam = tf.squeeze(cam, axis=[2, 3])

    return cam, predictions

def weighted_ce_loss(labels, predictions):
    labels = tf.cast(labels, tf.int32)

    ce = tf.keras.losses.sparse_categorical_crossentropy(
        labels, predictions
    )

    sample_weights = tf.gather(
        class_weights_tensor, labels
    )

    return tf.reduce_mean(ce * sample_weights)

def calculate_b3_loss(
    labels,
    clean_predictions,
    noisy_predictions,
    clean_cam,
    noisy_cam
):
    clean_ce = weighted_ce_loss(
        labels, clean_predictions
    )

    noisy_ce = weighted_ce_loss(
        labels, noisy_predictions
    )

    ce_loss = (clean_ce + noisy_ce) / 2.0

    per_sample_cam_loss = tf.reduce_mean(
        tf.square(clean_cam - noisy_cam),
        axis=1
    )

    cam_loss = tf.reduce_mean(per_sample_cam_loss)

    total_loss = ce_loss + LAMBDA_CAM * cam_loss

    return total_loss, ce_loss, cam_loss

def calculate_b4_loss(
    labels,
    clean_predictions,
    noisy_predictions,
    clean_cam,
    noisy_cam,
    snr_values
):

    clean_ce = weighted_ce_loss(
        labels, clean_predictions
    )

    noisy_ce = weighted_ce_loss(
        labels, noisy_predictions
    )

    ce_loss = (clean_ce + noisy_ce) / 2.0

    per_sample_cam_loss = tf.reduce_mean(
        tf.square(clean_cam - noisy_cam),
        axis=1
    )

    gates = noise_severity_gate(snr_values)

    cam_loss = tf.reduce_mean(
        per_sample_cam_loss * gates
    )

    total_loss = ce_loss + LAMBDA_CAM * cam_loss

    return total_loss, ce_loss, cam_loss

def train_b3_step(clean_x, labels):

    noisy_x, snr_values = tf.map_fn(
        lambda x: add_random_noise_with_snr(x),
        clean_x,
        fn_output_signature=(
            tf.TensorSpec(shape=(288, 1), dtype=tf.float32),
            tf.TensorSpec(shape=(), dtype=tf.float32)
        )
    )

    with tf.GradientTape() as outer_tape:

        clean_cam, clean_predictions = differentiable_cam_for_model(
            clean_x,
            labels,
            b3_feature_extractor,
            b3_classifier_head
        )

        noisy_cam, noisy_predictions = differentiable_cam_for_model(
            noisy_x,
            labels,
            b3_feature_extractor,
            b3_classifier_head
        )

        total_loss, ce_loss, cam_loss = calculate_b3_loss(
            labels,
            clean_predictions,
            noisy_predictions,
            clean_cam,
            noisy_cam
        )

    gradients = outer_tape.gradient(
        total_loss,
        b3_model.trainable_variables
    )

    gradient_pairs = [
        (g, v)
        for g, v in zip(
            gradients,
            b3_model.trainable_variables
        )
        if g is not None
    ]

    b3_optimizer.apply_gradients(gradient_pairs)

    return total_loss, ce_loss, cam_loss

def train_b4_step(clean_x, labels):

    noisy_x, snr_values = tf.map_fn(
        lambda x: add_random_noise_with_snr(x),
        clean_x,
        fn_output_signature=(
            tf.TensorSpec(shape=(288, 1), dtype=tf.float32),
            tf.TensorSpec(shape=(), dtype=tf.float32)
        )
    )

    with tf.GradientTape() as outer_tape:

        clean_cam, clean_predictions = differentiable_cam_for_model(
            clean_x,
            labels,
            b4_feature_extractor,
            b4_classifier_head
        )

        noisy_cam, noisy_predictions = differentiable_cam_for_model(
            noisy_x,
            labels,
            b4_feature_extractor,
            b4_classifier_head
        )

        total_loss, ce_loss, cam_loss = calculate_b4_loss(
            labels,
            clean_predictions,
            noisy_predictions,
            clean_cam,
            noisy_cam,
            snr_values
        )

    gradients = outer_tape.gradient(
        total_loss,
        b4_model.trainable_variables
    )

    gradient_pairs = [
        (g, v)
        for g, v in zip(
            gradients,
            b4_model.trainable_variables
        )
        if g is not None
    ]

    b4_optimizer.apply_gradients(gradient_pairs)

    return total_loss, ce_loss, cam_loss

def benchmark_training(train_function, dataset, model, model_name):

    batches = list(dataset.take(10))

    start_time = time.time()

    for batch_x, batch_y in batches:
        loss, ce, cam = train_function(batch_x, batch_y)
        _ = loss.numpy()

    elapsed = time.time() - start_time

    print(model_name, "10-batch time:", round(elapsed, 2), "seconds")
    print(model_name, "Average batch time:", round(elapsed / 10, 2), "seconds")

def train_one_epoch(train_function, dataset, model, model_name):

    total_losses = []
    ce_losses = []
    cam_losses = []

    start_time = time.time()

    for step, (batch_x, batch_y) in enumerate(dataset):

        total, ce, cam = train_function(batch_x, batch_y)

        total_losses.append(float(total.numpy()))
        ce_losses.append(float(ce.numpy()))
        cam_losses.append(float(cam.numpy()))

        if (step + 1) % 1000 == 0:
            print(
                f"{model_name} | Batch {step+1}/{len(dataset)} "
                f"| Loss: {np.mean(total_losses):.4f}"
            )

    elapsed = time.time() - start_time

    return {
        "train_loss": np.mean(total_losses),
        "train_ce_loss": np.mean(ce_losses),
        "train_cam_loss": np.mean(cam_losses),
        "training_time_min": elapsed / 60
    }

def evaluate_noisy_validation(model):

    all_f1 = []

    for (noise_name, snr_db), noisy_data in X_val_noisy.items():

        predictions = model.predict(
            noisy_data,
            batch_size=128,
            verbose=0
        )

        predicted_labels = np.argmax(predictions, axis=1)

        macro_f1 = f1_score(
            y_val,
            predicted_labels,
            average="macro",
            zero_division=0
        )

        all_f1.append(macro_f1)

        print(
            f"{noise_name.upper()} | {snr_db} dB "
            f"| Macro-F1: {macro_f1:.4f}"
        )

    return float(np.mean(all_f1))

# Noise helper used by the B3/B4 training steps (notebook 07)

def add_random_noise_with_snr(ecg):

    ecg = tf.cast(ecg, tf.float32)
    ecg = tf.squeeze(ecg, axis=-1)

    # Select BW or MA noise
    noise_index = tf.random.uniform(
        [], 0, 2, dtype=tf.int32
    )

    # Select noise segment from training region
    start = tf.random.uniform(
        [],
        TRAIN_START,
        TRAIN_END - BEAT_LENGTH + 1,
        dtype=tf.int32
    )

    indices = tf.range(start, start + BEAT_LENGTH)

    noise = tf.gather(
        noise_bank[noise_index],
        indices
    )

    noise = noise - tf.reduce_mean(noise)

    # Select SNR
    snr_index = tf.random.uniform(
        [], 0, len(TRAIN_SNRS), dtype=tf.int32
    )

    snr_db = tf.gather(
        tf.constant(TRAIN_SNRS, dtype=tf.float32),
        snr_index
    )

    signal_power = tf.reduce_mean(tf.square(ecg))
    noise_power = tf.reduce_mean(tf.square(noise))

    target_noise_power = (
        signal_power / tf.pow(10.0, snr_db / 10.0)
    )

    scale = tf.sqrt(
        target_noise_power /
        tf.maximum(noise_power, 1e-12)
    )

    noisy_ecg = ecg + noise * scale

    return (
        tf.expand_dims(noisy_ecg, axis=-1),
        snr_db
    )
