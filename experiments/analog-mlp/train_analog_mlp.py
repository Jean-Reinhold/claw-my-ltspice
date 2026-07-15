"""Train an analog-constrained MLP on MNIST for the analog-mlp experiment.

The network is trained exactly as the op-amp hardware computes it:

- Hidden activation is ``clip(z, 0, VSAT)`` — a single-supply inverting
  summing amplifier saturates at its rails, so the op-amp itself is the
  activation function (bounded ReLU).
- Output neurons are linear summing amplifiers clipped at ``±VSAT`` (dual
  supply) followed by one comparator per digit against a shared threshold
  rail ``VTH``: digit k is "on" when ``z_k > VTH``.
- Weights become resistor ratios ``|w| = RF / Ri``. After training, weights
  below ``PRUNE_T`` are pruned (resistor removed) and the survivors are
  quantized to the E96 series, so the numpy model and the SPICE netlist
  share the exact same numbers.

Runs inside the claw-spice container via:

    ./claw-spice code build experiments/analog-mlp/train_analog_mlp.py \
        --output-dir experiments/analog-mlp
"""

from __future__ import annotations

import gzip
import json
import os
import struct
import tempfile
import urllib.request
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="mpl-"))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

VSAT = 4.8
VTH_TRAIN = 2.4
TEMPERATURE = 0.6
POS_WEIGHT = 2.0
RF = 100_000.0
PRUNE_T = 0.04
W_CLIP = 8.0
LAYER_SIZES = [64, 48, 32, 24, 16, 10]
EPOCHS = 40
FINETUNE_EPOCHS = 12
BATCH = 256
LR_MAX = 3e-3
LR_MIN = 1e-4
WEIGHT_DECAY = 1e-4
SEED = 7

MNIST_FILES = {
    "train_images": "train-images-idx3-ubyte.gz",
    "train_labels": "train-labels-idx1-ubyte.gz",
    "test_images": "t10k-images-idx3-ubyte.gz",
    "test_labels": "t10k-labels-idx1-ubyte.gz",
}
MNIST_MIRRORS = [
    "https://ossci-datasets.s3.amazonaws.com/mnist/",
    "https://storage.googleapis.com/cvdf-datasets/mnist/",
]

# dataviz reference palette (light mode)
C_BLUE = "#2a78d6"
C_AQUA = "#1baf7a"
C_RED = "#e34948"
C_VIOLET = "#4a3aa7"
GRID = "#d9d9d3"
INK = "#33322e"
INK_2 = "#63615a"

E96 = np.array(
    [
        1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30,
        1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74,
        1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32,
        2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09,
        3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
        4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49,
        5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32,
        7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76,
    ]
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def report_images_dir() -> Path:
    path = repo_root() / "reports" / "analog-mlp" / "imagens" / "generated"
    path.mkdir(parents=True, exist_ok=True)
    return path


# ---------------------------------------------------------------- MNIST data


def ensure_mnist(data_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    for filename in MNIST_FILES.values():
        target = data_dir / filename
        if target.exists():
            continue
        last_error: Exception | None = None
        for mirror in MNIST_MIRRORS:
            url = mirror + filename
            try:
                print(f"[data] downloading {url}")
                with urllib.request.urlopen(url, timeout=60) as response:
                    target.write_bytes(response.read())
                last_error = None
                break
            except Exception as error:  # noqa: BLE001 - try next mirror
                last_error = error
        if last_error is not None:
            raise RuntimeError(f"could not download {filename}: {last_error}")


def read_idx_images(path: Path) -> np.ndarray:
    with gzip.open(path, "rb") as handle:
        magic, count, rows, cols = struct.unpack(">IIII", handle.read(16))
        if magic != 2051:
            raise ValueError(f"bad magic {magic} in {path}")
        data = np.frombuffer(handle.read(), dtype=np.uint8)
    return data.reshape(count, rows, cols)


def read_idx_labels(path: Path) -> np.ndarray:
    with gzip.open(path, "rb") as handle:
        magic, count = struct.unpack(">II", handle.read(8))
        if magic != 2049:
            raise ValueError(f"bad magic {magic} in {path}")
        return np.frombuffer(handle.read(), dtype=np.uint8).copy()


def downsample_8x8(images: np.ndarray) -> np.ndarray:
    """28x28 uint8 -> crop to 24x24 -> 3x3 average pool -> 8x8 float in [0, 1]."""
    cropped = images[:, 2:26, 2:26].astype(np.float32) / 255.0
    pooled = cropped.reshape(-1, 8, 3, 8, 3).mean(axis=(2, 4))
    return pooled.reshape(-1, 64)


# ---------------------------------------------------------------- model


def init_params(rng: np.random.Generator) -> list[dict[str, np.ndarray]]:
    layers = []
    for fan_in, fan_out in zip(LAYER_SIZES[:-1], LAYER_SIZES[1:], strict=False):
        scale = np.sqrt(2.0 / fan_in)
        layers.append(
            {
                "W": rng.normal(0.0, scale, size=(fan_in, fan_out)).astype(np.float32),
                "b": np.zeros(fan_out, dtype=np.float32),
            }
        )
    return layers


def forward(layers: list[dict[str, np.ndarray]], x: np.ndarray) -> tuple[np.ndarray, list]:
    """Return output logits (pre-comparator, clipped to op-amp rails) and cache."""
    cache = []
    activation = x
    last = len(layers) - 1
    for index, layer in enumerate(layers):
        z = activation @ layer["W"] + layer["b"]
        if index == last:
            out = np.clip(z, -VSAT, VSAT)
        else:
            out = np.clip(z, 0.0, VSAT)
        cache.append((activation, z))
        activation = out
    return activation, cache


def bce_loss_and_grad(logits: np.ndarray, targets: np.ndarray) -> tuple[float, np.ndarray]:
    s = (logits - VTH_TRAIN) / TEMPERATURE
    p = 1.0 / (1.0 + np.exp(-s))
    eps = 1e-7
    loss = -(POS_WEIGHT * targets * np.log(p + eps) + (1 - targets) * np.log(1 - p + eps))
    grad_s = p * (1 - targets + POS_WEIGHT * targets) - POS_WEIGHT * targets
    grad_logits = grad_s / TEMPERATURE / logits.shape[0]
    return float(loss.mean()), grad_logits.astype(np.float32)


def backward(
    layers: list[dict[str, np.ndarray]],
    cache: list,
    grad_out: np.ndarray,
) -> list[dict[str, np.ndarray]]:
    grads = [None] * len(layers)
    last = len(layers) - 1
    grad = grad_out
    for index in range(last, -1, -1):
        activation_in, z = cache[index]
        if index == last:
            gate = ((z > -VSAT) & (z < VSAT)).astype(np.float32)
        else:
            gate = ((z > 0.0) & (z < VSAT)).astype(np.float32)
        grad_z = grad * gate
        grads[index] = {
            "W": activation_in.T @ grad_z,
            "b": grad_z.sum(axis=0),
        }
        if index > 0:
            grad = grad_z @ layers[index]["W"].T
    return grads


def adamw_step(layers, grads, state, lr, masks=None) -> None:
    beta1, beta2, eps = 0.9, 0.999, 1e-8
    state["t"] += 1
    t = state["t"]
    for index, (layer, grad) in enumerate(zip(layers, grads, strict=False)):
        for key in ("W", "b"):
            g = grad[key]
            m = state["m"][index][key]
            v = state["v"][index][key]
            m[:] = beta1 * m + (1 - beta1) * g
            v[:] = beta2 * v + (1 - beta2) * g * g
            m_hat = m / (1 - beta1**t)
            v_hat = v / (1 - beta2**t)
            update = lr * m_hat / (np.sqrt(v_hat) + eps)
            if key == "W":
                update = update + lr * WEIGHT_DECAY * layer[key]
            layer[key] -= update
            np.clip(layer[key], -W_CLIP, W_CLIP, out=layer[key])
            if masks is not None:
                layer[key] *= masks[index][key]


def init_adam(layers) -> dict:
    return {
        "t": 0,
        "m": [{k: np.zeros_like(layer[k]) for k in ("W", "b")} for layer in layers],
        "v": [{k: np.zeros_like(layer[k]) for k in ("W", "b")} for layer in layers],
    }


# ---------------------------------------------------------------- metrics


def evaluate(layers, x, y, threshold=VTH_TRAIN) -> dict[str, float]:
    logits, _ = forward(layers, x)
    argmax_acc = float((logits.argmax(axis=1) == y).mean())
    fires = logits > threshold
    fire_counts = fires.sum(axis=1)
    correct_only = fires[np.arange(len(y)), y] & (fire_counts == 1)
    return {
        "argmax_acc": argmax_acc,
        "exact_fire": float(correct_only.mean()),
        "no_fire": float((fire_counts == 0).mean()),
        "multi_fire": float((fire_counts > 1).mean()),
    }


def calibrate_threshold(layers, x, y) -> float:
    logits, _ = forward(layers, x)
    best_theta, best_rate = VTH_TRAIN, -1.0
    for theta in np.arange(0.8, 4.2, 0.05):
        fires = logits > theta
        counts = fires.sum(axis=1)
        rate = float((fires[np.arange(len(y)), y] & (counts == 1)).mean())
        if rate > best_rate or (rate == best_rate and abs(theta - VTH_TRAIN) < abs(best_theta - VTH_TRAIN)):
            best_theta, best_rate = float(theta), rate
    return best_theta


# ---------------------------------------------------------------- analog mapping


def quantize_e96(layers) -> list[dict[str, np.ndarray]]:
    """Snap every weight to w = RF / R with R in the E96 resistor series."""
    quantized = []
    decades = 10.0 ** np.arange(2, 9)
    series = np.sort(np.concatenate([E96 * d for d in decades]))
    for layer in layers:
        new_layer = {}
        for key in ("W", "b"):
            w = layer[key]
            wq = np.zeros_like(w)
            nz = np.abs(w) > 0
            resistance = RF / np.abs(w[nz])
            idx = np.searchsorted(series, resistance)
            idx = np.clip(idx, 1, len(series) - 1)
            lower = series[idx - 1]
            upper = series[idx]
            snapped = np.where(resistance - lower < upper - resistance, lower, upper)
            wq[nz] = np.sign(w[nz]) * (RF / snapped)
            new_layer[key] = wq.astype(np.float32)
        quantized.append(new_layer)
    return quantized


def prune(layers, threshold=PRUNE_T):
    masks = []
    for layer in layers:
        mask = {}
        for key in ("W", "b"):
            keep = (np.abs(layer[key]) >= threshold).astype(np.float32)
            layer[key] *= keep
            mask[key] = keep
        masks.append(mask)
    return masks


def sparsity_stats(layers) -> dict:
    total = sum(int(layer["W"].size + layer["b"].size) for layer in layers)
    nonzero = sum(
        int((layer["W"] != 0).sum() + (layer["b"] != 0).sum()) for layer in layers
    )
    return {"parameters_total": total, "parameters_nonzero": nonzero}


# ---------------------------------------------------------------- training


def run_epochs(layers, state, x, y, targets, epochs, lr_max, lr_min, masks, x_val, y_val, history):
    rng = np.random.default_rng(SEED + state["t"] + 1)
    steps = int(np.ceil(len(x) / BATCH))
    for epoch in range(epochs):
        lr = lr_min + 0.5 * (lr_max - lr_min) * (1 + np.cos(np.pi * epoch / max(epochs - 1, 1)))
        order = rng.permutation(len(x))
        epoch_loss = 0.0
        for step in range(steps):
            batch = order[step * BATCH : (step + 1) * BATCH]
            logits, cache = forward(layers, x[batch])
            loss, grad = bce_loss_and_grad(logits, targets[batch])
            grads = backward(layers, cache, grad)
            adamw_step(layers, grads, state, lr, masks)
            epoch_loss += loss
        val = evaluate(layers, x_val, y_val)
        history["loss"].append(epoch_loss / steps)
        history["val_argmax"].append(val["argmax_acc"])
        history["val_exact_fire"].append(val["exact_fire"])
        print(
            f"[train] epoch {len(history['loss']):3d} "
            f"loss {epoch_loss / steps:.4f} "
            f"val argmax {val['argmax_acc']:.4f} exact-fire {val['exact_fire']:.4f}"
        )


# ---------------------------------------------------------------- figures


def style_axis(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(GRID)
    ax.tick_params(colors=INK_2, labelsize=9)
    ax.grid(True, color=GRID, linewidth=0.6, alpha=0.6)
    ax.set_axisbelow(True)


def fig_training_curves(history, out_png: Path) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.6, 3.4))
    epochs = np.arange(1, len(history["loss"]) + 1)
    ax1.plot(epochs, history["loss"], color=C_BLUE, linewidth=2)
    ax1.set_xlabel("Época", color=INK)
    ax1.set_ylabel("Perda BCE", color=INK)
    ax1.set_title("Perda de treinamento", color=INK, fontsize=11)
    style_axis(ax1)
    ax2.plot(epochs, 100 * np.asarray(history["val_argmax"]), color=C_AQUA, linewidth=2,
             label="Argmax")
    ax2.plot(epochs, 100 * np.asarray(history["val_exact_fire"]), color=C_VIOLET,
             linewidth=2, label="Disparo exato")
    ax2.set_xlabel("Época", color=INK)
    ax2.set_ylabel("Acurácia de validação (%)", color=INK)
    ax2.set_title("Acurácia de validação", color=INK, fontsize=11)
    ax2.legend(frameon=False, fontsize=9, labelcolor=INK)
    style_axis(ax2)
    if len(epochs) > EPOCHS:
        for ax in (ax1, ax2):
            ax.axvline(EPOCHS + 0.5, color=C_RED, linewidth=1, linestyle="--", alpha=0.7)
    fig.tight_layout()
    fig.savefig(out_png, dpi=200, facecolor="white")
    plt.close(fig)


def fig_digit_samples(raw_images, features, labels, out_png: Path) -> None:
    picks = [int(np.argmax(labels == digit)) for digit in range(10)]
    fig, axes = plt.subplots(2, 10, figsize=(9.5, 2.3))
    for column, pick in enumerate(picks):
        axes[0][column].imshow(raw_images[pick], cmap="gray_r")
        axes[1][column].imshow(features[pick].reshape(8, 8), cmap="gray_r")
        for row in (0, 1):
            axes[row][column].set_xticks([])
            axes[row][column].set_yticks([])
            for spine in axes[row][column].spines.values():
                spine.set_color(GRID)
        axes[0][column].set_title(str(int(labels[pick])), fontsize=9, color=INK)
    axes[0][0].set_ylabel("28×28", fontsize=8, color=INK_2)
    axes[1][0].set_ylabel("8×8", fontsize=8, color=INK_2)
    fig.suptitle("Entrada da rede: MNIST reamostrado para 64 tensões (0 a 1 V)",
                 fontsize=10, color=INK)
    fig.tight_layout()
    fig.savefig(out_png, dpi=200, facecolor="white")
    plt.close(fig)


def fig_confusion(layers, x, y, out_png: Path) -> None:
    logits, _ = forward(layers, x)
    pred = logits.argmax(axis=1)
    matrix = np.zeros((10, 10), dtype=int)
    for truth, guess in zip(y, pred, strict=False):
        matrix[truth][guess] += 1
    fig, ax = plt.subplots(figsize=(5.4, 4.6))
    with_floor = np.log10(matrix + 1)
    ax.imshow(with_floor, cmap="Blues")
    for i in range(10):
        for j in range(10):
            if matrix[i][j]:
                bright = with_floor[i][j] > 0.7 * with_floor.max()
                ax.text(j, i, str(matrix[i][j]), ha="center", va="center",
                        fontsize=7, color="white" if bright else INK)
    ax.set_xticks(range(10))
    ax.set_yticks(range(10))
    ax.set_xlabel("Dígito previsto (maior saída)", color=INK)
    ax.set_ylabel("Dígito verdadeiro", color=INK)
    ax.set_title("Matriz de confusão no conjunto de teste", color=INK, fontsize=11)
    ax.tick_params(colors=INK_2, labelsize=9)
    fig.tight_layout()
    fig.savefig(out_png, dpi=200, facecolor="white")
    plt.close(fig)


def fig_resistors(layers, out_png: Path) -> None:
    values = []
    for layer in layers:
        for key in ("W", "b"):
            w = layer[key]
            nz = np.abs(w) > 0
            values.append(RF / np.abs(w[nz]))
    resistances = np.concatenate(values)
    fig, ax = plt.subplots(figsize=(6.8, 3.2))
    bins = np.logspace(np.log10(resistances.min() * 0.8), np.log10(resistances.max() * 1.2), 40)
    ax.hist(resistances, bins=bins, color=C_BLUE, edgecolor="white", linewidth=0.4)
    ax.set_xscale("log")
    ax.set_xlabel("Resistência de entrada $R_i = R_f/|w|$ (Ω), série E96", color=INK)
    ax.set_ylabel("Quantidade", color=INK)
    ax.set_title(f"Distribuição dos {len(resistances)} resistores de peso "
                 f"($R_f$ = 100 kΩ)", color=INK, fontsize=11)
    style_axis(ax)
    fig.tight_layout()
    fig.savefig(out_png, dpi=200, facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- export


def export_weights(layers, meta, out_path: Path) -> None:
    payload = {
        "meta": meta,
        "layers": [
            {
                "W": [[round(float(v), 8) for v in row] for row in layer["W"]],
                "b": [round(float(v), 8) for v in layer["b"]],
            }
            for layer in layers
        ],
    }
    out_path.write_text(json.dumps(payload))


def export_test_vectors(layers, x_test, y_test, theta, out_path: Path, per_class=2) -> None:
    logits, _ = forward(layers, x_test)
    pred = logits.argmax(axis=1)
    fires = logits > theta
    counts = fires.sum(axis=1)
    vectors = []
    for repeat in range(per_class):
        for digit in range(10):
            candidates = np.flatnonzero(
                (y_test == digit) & (pred == digit) & (counts == 1) & fires[:, digit]
            )
            index = int(candidates[repeat])
            vectors.append(
                {
                    "label": int(digit),
                    "index": index,
                    "pixels": [round(float(v), 6) for v in x_test[index]],
                    "logits": [round(float(v), 6) for v in logits[index]],
                }
            )
    out_path.write_text(json.dumps({"threshold": theta, "vsat": VSAT, "vectors": vectors}))


# ---------------------------------------------------------------- entry point


def build(output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    data_dir = output / "data"
    ensure_mnist(data_dir)

    train_images = read_idx_images(data_dir / MNIST_FILES["train_images"])
    train_labels = read_idx_labels(data_dir / MNIST_FILES["train_labels"])
    test_images = read_idx_images(data_dir / MNIST_FILES["test_images"])
    test_labels = read_idx_labels(data_dir / MNIST_FILES["test_labels"])

    x_all = downsample_8x8(train_images)
    x_test = downsample_8x8(test_images)
    rng = np.random.default_rng(SEED)
    order = rng.permutation(len(x_all))
    val_count = 5000
    val_idx, train_idx = order[:val_count], order[val_count:]
    x_train, y_train = x_all[train_idx], train_labels[train_idx]
    x_val, y_val = x_all[val_idx], train_labels[val_idx]
    targets = np.eye(10, dtype=np.float32)[y_train]

    layers = init_params(rng)
    state = init_adam(layers)
    history = {"loss": [], "val_argmax": [], "val_exact_fire": []}

    print(f"[train] dense phase: {EPOCHS} epochs, sizes {LAYER_SIZES}")
    run_epochs(layers, state, x_train, y_train, targets, EPOCHS, LR_MAX, LR_MIN,
               None, x_val, y_val, history)

    masks = prune(layers, PRUNE_T)
    stats_after_prune = sparsity_stats(layers)
    print(f"[prune] |w| < {PRUNE_T} removed -> {stats_after_prune}")
    print(f"[train] fine-tune phase: {FINETUNE_EPOCHS} epochs with pruning mask")
    run_epochs(layers, state, x_train, y_train, targets, FINETUNE_EPOCHS,
               LR_MAX / 6, LR_MIN / 3, masks, x_val, y_val, history)

    layers = quantize_e96(layers)
    theta = calibrate_threshold(layers, x_val, y_val)
    val_metrics = evaluate(layers, x_val, y_val, theta)
    test_metrics = evaluate(layers, x_test, test_labels, theta)
    stats = sparsity_stats(layers)
    print(f"[final] threshold {theta:.2f} V, val {val_metrics}, test {test_metrics}")

    meta = {
        "layer_sizes": LAYER_SIZES,
        "vsat": VSAT,
        "threshold": theta,
        "rf_ohms": RF,
        "prune_threshold": PRUNE_T,
        "seed": SEED,
        "epochs_dense": EPOCHS,
        "epochs_finetune": FINETUNE_EPOCHS,
        "val_metrics": val_metrics,
        "test_metrics": test_metrics,
        **stats,
    }
    weights_path = output / "analog_mlp_weights.json"
    vectors_path = output / "spice_test_vectors.json"
    export_weights(layers, meta, weights_path)
    export_test_vectors(layers, x_test, test_labels, theta, vectors_path)

    images = report_images_dir()
    fig_training_curves(history, images / "curvas_treinamento.png")
    fig_digit_samples(test_images, x_test, test_labels, images / "amostras_digitos.png")
    fig_confusion(layers, x_test, test_labels, images / "matriz_confusao.png")
    fig_resistors(layers, images / "histograma_resistores.png")

    metrics_path = output / "metrics.json"
    metrics_path.write_text(json.dumps(meta, indent=2))
    return {
        "weights": weights_path,
        "test_vectors": vectors_path,
        "metrics": metrics_path,
    }


if __name__ == "__main__":
    print(build(Path(__file__).parent))
