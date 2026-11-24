"""
Keras model builders for the clean baselines (notebook 05).

Reusable helper module created during the local VS Code migration.
Functions below are copied verbatim from the original notebooks; the notebooks
remain self-contained and are the source of truth for the research methodology.
"""

try:
    import tensorflow as tf
except ImportError:  # optional: install requirements.txt to enable training helpers
    tf = None

from .config import INPUT_SHAPE, NUM_CLASSES

# Model builders extracted from 05_CNN_ResNet_Clean_Baselines.ipynb

def residual_block(x, filters, kernel_size=5, stride=1):

    shortcut = x

    x = tf.keras.layers.Conv1D(
        filters,
        kernel_size,
        strides=stride,
        padding="same",
        use_bias=False
    )(x)

    x = tf.keras.layers.BatchNormalization()(x)

    x = tf.keras.layers.Activation("relu")(x)

    x = tf.keras.layers.Conv1D(
        filters,
        kernel_size,
        padding="same",
        use_bias=False
    )(x)

    x = tf.keras.layers.BatchNormalization()(x)

    if shortcut.shape[-1] != filters or stride != 1:

        shortcut = tf.keras.layers.Conv1D(
            filters,
            kernel_size=1,
            strides=stride,
            padding="same",
            use_bias=False
        )(shortcut)

        shortcut = tf.keras.layers.BatchNormalization()(shortcut)

    x = tf.keras.layers.Add()([x, shortcut])

    x = tf.keras.layers.Activation("relu")(x)

    return x

def build_resnet_model():

    inputs = tf.keras.layers.Input(shape=INPUT_SHAPE)

    x = tf.keras.layers.Conv1D(
        32,
        kernel_size=7,
        padding="same",
        use_bias=False
    )(inputs)

    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Activation("relu")(x)

    x = residual_block(x, 32)
    x = residual_block(x, 64, stride=2)
    x = residual_block(x, 128, stride=2)

    x = tf.keras.layers.GlobalAveragePooling1D()(x)

    x = tf.keras.layers.Dense(128, activation="relu")(x)

    x = tf.keras.layers.Dropout(0.4)(x)

    outputs = tf.keras.layers.Dense(
        NUM_CLASSES,
        activation="softmax"
    )(x)

    model = tf.keras.Model(inputs, outputs)

    return model

def build_cnn_model():

    model = tf.keras.Sequential([

        tf.keras.layers.Input(shape=INPUT_SHAPE),

        tf.keras.layers.Conv1D(
            32, kernel_size=7,
            activation="relu",
            padding="same"
        ),

        tf.keras.layers.BatchNormalization(),

        tf.keras.layers.MaxPooling1D(pool_size=2),

        tf.keras.layers.Conv1D(
            64, kernel_size=5,
            activation="relu",
            padding="same"
        ),

        tf.keras.layers.BatchNormalization(),

        tf.keras.layers.MaxPooling1D(pool_size=2),

        tf.keras.layers.Conv1D(
            128, kernel_size=3,
            activation="relu",
            padding="same"
        ),

        tf.keras.layers.BatchNormalization(),

        tf.keras.layers.GlobalAveragePooling1D(),

        tf.keras.layers.Dense(128, activation="relu"),

        tf.keras.layers.Dropout(0.4),

        tf.keras.layers.Dense(
            NUM_CLASSES,
            activation="softmax"
        )

    ])

    return model
