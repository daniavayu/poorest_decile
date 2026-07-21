from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_CSV = SCRIPT_DIR / "bottom10percent_output.csv"
OUTPUT_PLOT = SCRIPT_DIR / "left_behind_plot.png"
OUTPUT_GAP_PLOT = SCRIPT_DIR / "left_behind_gap_plot.png"
FOCUS_DECILES = [1, 5, 10]
DECILE_LABELS = {
    1: "Poorest decile",
    5: "Middle decile",
    10: "Top decile",
}
DECILE_COLORS = {
    1: "#D81B60",
    5: "#1EB910",
    10: "#2F42ED",
}


def build_growth_index(summary: pd.DataFrame) -> pd.DataFrame:
    focus = summary[summary["decile"].isin(FOCUS_DECILES)].copy()
    baseline = (
        focus.sort_values("year")
        .groupby("decile", as_index=False)
        .first()[["decile", "welf"]]
        .rename(columns={"welf": "baseline_welf"})
    )
    focus = focus.merge(baseline, on="decile", how="left")
    focus["welf_index"] = focus["welf"] / focus["baseline_welf"] * 100
    return focus


def make_plot(summary: pd.DataFrame, output_path: Path) -> None:
    focus = build_growth_index(summary)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.8))
    ax_left, ax_right = axes

    for decile in FOCUS_DECILES:
        subset = focus[focus["decile"] == decile]
        label = DECILE_LABELS[decile]
        color = DECILE_COLORS[decile]
        ax_left.plot(subset["year"], subset["welf_index"], linewidth=2.2, color=color, label=label)
        ax_right.plot(subset["year"], subset["share"], linewidth=2.2, color=color, label=label)

    ax_left.set_title("Income growth index (1981 = 100)")
    ax_left.set_xlabel("")
    ax_left.set_ylabel("Index")
    ax_left.grid(axis="y", alpha=0.25)

    ax_right.set_title("Share of global welfare")
    ax_right.set_xlabel("")
    ax_right.set_ylabel("Percent")
    ax_right.grid(axis="y", alpha=0.25)

    years = sorted(focus["year"].unique())
    if years:
        ticks = list(range(int(min(years)), int(max(years)) + 1, 5))
        ax_left.set_xticks(ticks)
        ax_right.set_xticks(ticks)

    handles, labels = ax_left.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False)
    fig.suptitle("The poorest decile improves, but remains far behind", fontsize=14)
    fig.tight_layout(rect=(0, 0.07, 1, 0.95))
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def build_gap_table(summary: pd.DataFrame) -> pd.DataFrame:
    pivoted = summary.pivot(index="year", columns="decile", values="welf").reset_index()
    pivoted["middle_to_poorest"] = pivoted[5] / pivoted[1]
    pivoted["top_to_poorest"] = pivoted[10] / pivoted[1]
    return pivoted


def make_gap_plot(summary: pd.DataFrame, output_path: Path) -> None:
    gap = build_gap_table(summary)

    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    ax.plot(
        gap["year"],
        gap["middle_to_poorest"],
        linewidth=2.3,
        color=DECILE_COLORS[5],
        label="Middle decile / poorest decile",
    )
    ax.plot(
        gap["year"],
        gap["top_to_poorest"],
        linewidth=2.3,
        color=DECILE_COLORS[10],
        label="Top decile / poorest decile",
    )

    years = sorted(gap["year"].unique())
    if years:
        ax.set_xticks(list(range(int(min(years)), int(max(years)) + 1, 5)))

    ax.set_title("How far behind the poorest decile remains")
    ax.set_xlabel("")
    ax.set_ylabel("Welfare ratio")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(loc="upper right", frameon=False)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    summary = pd.read_csv(INPUT_CSV)
    make_plot(summary, OUTPUT_PLOT)
    make_gap_plot(summary, OUTPUT_GAP_PLOT)
    print(f"Plot saved to: {OUTPUT_PLOT}")
    print(f"Gap plot saved to: {OUTPUT_GAP_PLOT}")


if __name__ == "__main__":
    main()