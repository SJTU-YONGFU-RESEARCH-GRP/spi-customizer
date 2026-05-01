#!/usr/bin/env python3
"""
Generate the replay balance profile figure from the validation report.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


CORE_DIMENSIONS = ["mode", "role", "ss_polarity", "bit_order"]
BINARY_DIMENSIONS = [
    "clock_jitter_test",
    "default_data_enabled",
    "dma_support",
    "fifo_buffers",
    "interrupts",
    "multi_master",
    "waveform_capture",
]

IEEE_BLUE = "#1f77b4"
IEEE_ORANGE = "#ff7f0e"
IEEE_GREEN = "#2ca02c"
IEEE_RED = "#d62728"
IEEE_GRAY = "#7f7f7f"
IEEE_LIGHT_GRAY = "#d9d9d9"
IEEE_DARK = "#222222"


BalanceRow = Dict[str, object]


def parse_value_counts(raw: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        name, value = item.rsplit(":", 1)
        counts[name.strip()] = int(value.strip())
    return counts


def parse_balance_matrix(report_path: Path) -> Dict[str, BalanceRow]:
    rows: Dict[str, BalanceRow] = {}
    in_table = False

    for raw_line in report_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line == "## Balance Matrix (Modern Cases)":
            in_table = True
            continue
        if in_table and line.startswith("## "):
            break
        if not in_table or not line.startswith("|"):
            continue
        if re.match(r"^\|\s*-", line) or "Dimension" in line:
            continue

        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) != 5:
            continue

        dimension, value_counts, min_count, max_count, ratio = parts
        rows[dimension] = {
            "counts": parse_value_counts(value_counts),
            "min": int(min_count),
            "max": int(max_count),
            "ratio": float(ratio),
        }

    if not rows:
        raise ValueError(f"No balance matrix rows found in {report_path}")
    return rows


def label(text: str) -> str:
    replacements = {
        "ss": "SS",
        "dma": "DMA",
        "fifo": "FIFO",
        "lsb": "LSB",
        "msb": "MSB",
    }
    words = text.replace("_", " ").split()
    formatted = []
    for word in words:
        formatted.append(replacements.get(word.lower(), word.title()))
    return " ".join(formatted)


def apply_ieee_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8.5,
            "font.weight": "bold",
            "axes.labelweight": "bold",
            "axes.titleweight": "bold",
            "axes.edgecolor": IEEE_DARK,
            "axes.linewidth": 1.0,
            "xtick.color": IEEE_DARK,
            "ytick.color": IEEE_DARK,
            "figure.dpi": 160,
            "savefig.dpi": 300,
        }
    )


def draw_core_distribution(ax: plt.Axes, rows: Dict[str, BalanceRow]) -> None:
    names: List[str] = []
    counts: List[int] = []
    colors: List[str] = []
    palette = {
        "mode": IEEE_BLUE,
        "role": IEEE_GREEN,
        "ss_polarity": IEEE_ORANGE,
        "bit_order": IEEE_GRAY,
    }

    for dimension in CORE_DIMENSIONS:
        for value, count in rows[dimension]["counts"].items():
            names.append(f"{label(dimension)}: {label(value)}")
            counts.append(count)
            colors.append(palette[dimension])

    y_positions = list(range(len(names)))
    bars = ax.barh(y_positions, counts, color=colors, edgecolor=IEEE_DARK, linewidth=0.6)
    for bar, count in zip(bars, counts):
        ax.text(
            count + 1.0,
            bar.get_y() + bar.get_height() / 2.0,
            str(count),
            ha="left",
            va="center",
            fontsize=8,
            fontweight="bold",
        )

    ax.set_title("(a) Core protocol dimensions", loc="left")
    ax.set_xlabel("Cases")
    ax.set_yticks(y_positions)
    ax.set_yticklabels(names, fontweight="bold")
    ax.set_xlim(0, max(counts) * 1.18)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis="x", color=IEEE_LIGHT_GRAY, linestyle="-", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.invert_yaxis()


def draw_binary_options(ax: plt.Axes, rows: Dict[str, BalanceRow]) -> None:
    y_positions = list(range(len(BINARY_DIMENSIONS)))
    false_counts: List[int] = []
    true_counts: List[int] = []

    for dimension in BINARY_DIMENSIONS:
        counts = rows[dimension]["counts"]
        false_counts.append(int(counts.get("False", 0)))
        true_counts.append(int(counts.get("True", 0)))

    ax.barh(
        y_positions,
        false_counts,
        color=IEEE_LIGHT_GRAY,
        edgecolor=IEEE_DARK,
        linewidth=0.6,
        label="False",
    )
    ax.barh(
        y_positions,
        true_counts,
        left=false_counts,
        color=IEEE_BLUE,
        edgecolor=IEEE_DARK,
        linewidth=0.6,
        label="True",
    )

    for y, false_count, true_count in zip(y_positions, false_counts, true_counts):
        if false_count > 0:
            ax.text(
                false_count / 2.0,
                y,
                str(false_count),
                ha="center",
                va="center",
                fontsize=8,
                fontweight="bold",
            )
        if true_count > 0:
            ax.text(
                false_count + true_count / 2.0,
                y,
                str(true_count),
                ha="center",
                va="center",
                fontsize=8,
                color="white",
                fontweight="bold",
            )

    ax.set_title("(b) Binary option coverage", loc="left")
    ax.set_xlabel("Cases")
    ax.set_yticks(y_positions)
    ax.set_yticklabels([label(dimension) for dimension in BINARY_DIMENSIONS], fontweight="bold")
    ax.set_xlim(0, max(false_counts[i] + true_counts[i] for i in y_positions) * 1.03)
    ax.grid(axis="x", color=IEEE_LIGHT_GRAY, linestyle="-", linewidth=0.6)
    ax.legend(
        loc="center left",
        bbox_to_anchor=(1.02, 0.25),
        ncol=1,
        frameon=True,
        edgecolor=IEEE_DARK,
        prop={"weight": "bold", "size": 8},
    )
    ax.set_axisbelow(True)


def ratio_color(ratio: float) -> str:
    if ratio <= 1.5:
        return IEEE_BLUE
    if ratio <= 4.0:
        return IEEE_ORANGE
    return IEEE_RED


def draw_imbalance_ratio(ax: plt.Axes, rows: Dict[str, BalanceRow]) -> None:
    ordered = sorted(rows.items(), key=lambda item: float(item[1]["ratio"]))
    names = [label(name) for name, _ in ordered]
    ratios = [float(row["ratio"]) for _, row in ordered]
    colors = [ratio_color(ratio) for ratio in ratios]
    y_positions = list(range(len(ordered)))

    bars = ax.barh(y_positions, ratios, color=colors, edgecolor=IEEE_DARK, linewidth=0.6)
    for bar, ratio in zip(bars, ratios):
        ax.text(
            ratio + 0.25,
            bar.get_y() + bar.get_height() / 2.0,
            f"{ratio:.2f}x",
            ha="left",
            va="center",
            fontsize=8,
            fontweight="bold",
        )

    ax.axvline(1.5, color=IEEE_GRAY, linestyle="--", linewidth=0.9)
    ax.axvline(4.0, color=IEEE_GRAY, linestyle=":", linewidth=0.9)
    ax.set_title("(c) Max/min count ratio", loc="left")
    ax.set_xlabel("Ratio (log scale)")
    ax.set_yticks(y_positions)
    ax.set_yticklabels(names, fontweight="bold")
    ax.set_xscale("log")
    ax.set_xlim(0.9, max(ratios) * 1.5)
    ax.grid(axis="x", color=IEEE_LIGHT_GRAY, linestyle="-", linewidth=0.6)
    ax.set_axisbelow(True)


def generate_figure(report_path: Path, output_path: Path) -> None:
    rows = parse_balance_matrix(report_path)
    apply_ieee_style()

    fig = plt.figure(figsize=(7.4, 4.8))
    grid = fig.add_gridspec(
        2,
        2,
        width_ratios=[1.1, 1.0],
        height_ratios=[1.0, 1.0],
        hspace=0.55,
        wspace=0.95,
    )
    axes = [
        fig.add_subplot(grid[0, 0]),
        fig.add_subplot(grid[1, 0]),
        fig.add_subplot(grid[:, 1]),
    ]

    draw_core_distribution(axes[0], rows)
    draw_binary_options(axes[1], rows)
    draw_imbalance_ratio(axes[2], rows)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Generate replay balance profile figure.")
    parser.add_argument(
        "--report",
        type=Path,
        default=repo_root / "docs" / "SPI_REPLAY_VALIDATION_REPORT.md",
        help="Path to the replay validation report.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=repo_root / "idea2" / "figures" / "replay_balance_profile_v2.png",
        help="Output PNG path.",
    )
    args = parser.parse_args()

    generate_figure(args.report, args.output)


if __name__ == "__main__":
    main()
