from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


REQUIRED_COLUMNS = {"year", "welf", "pop"}
TARGET_DECILES = [1, 2, 5, 10]
DECILE_LABELS = {
    1: "Poorest",
    2: "Next poorest",
    5: "Middle",
    10: "Top",
}
DECILE_COLORS = {
    1: "#2F42ED",
    2: "#D81B60",
    5: "#1EB910",
    10: "#F4D10D",
}


def parse_args() -> argparse.Namespace:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Run Nishant's bottom-decile workflow using Daniel's prepared data."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=script_dir / "prepared_daniel_input.csv",
        help="Path to the prepared CSV generated from Daniel's source data.",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=script_dir / "bottom10percent_output.csv",
        help="Path for the decile-level output table.",
    )
    parser.add_argument(
        "--output-plot",
        type=Path,
        default=script_dir / "bottom10percent_plot.png",
        help="Path for the exported plot.",
    )
    return parser.parse_args()


def load_dataset(file_path: Path) -> pd.DataFrame:
    data = pd.read_csv(file_path)
    missing = REQUIRED_COLUMNS.difference(data.columns)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Missing required columns: {missing_list}")

    cleaned = data.loc[:, ["year", "welf", "pop"]].dropna().copy()
    if cleaned.empty:
        raise ValueError("The prepared input is empty after dropping missing values.")

    return cleaned


def assign_weighted_deciles(group: pd.DataFrame) -> pd.DataFrame:
    ordered = group.sort_values("welf").copy()
    total_pop = ordered["pop"].sum()
    if total_pop <= 0:
        raise ValueError("Population weights must sum to a positive value within each year.")

    cumulative_share = ordered["pop"].cumsum() / total_pop
    ordered["decile"] = cumulative_share.apply(
        lambda value: min(10, max(1, math.ceil(value * 10)))
    )
    return ordered


def build_decile_table(data: pd.DataFrame) -> pd.DataFrame:
    decile_frame = pd.concat(
        [assign_weighted_deciles(group) for _, group in data.groupby("year")],
        ignore_index=True,
    )
    decile_frame["weighted_welf"] = decile_frame["welf"] * decile_frame["pop"]

    summary = (
        decile_frame.groupby(["year", "decile"], as_index=False)
        .agg(weighted_welf_sum=("weighted_welf", "sum"), pop_sum=("pop", "sum"))
    )
    summary["welf"] = summary["weighted_welf_sum"] / summary["pop_sum"]
    summary = summary.drop(columns=["weighted_welf_sum", "pop_sum"])

    summary["tinc"] = summary.groupby("year")["welf"].transform("sum")
    summary["share"] = summary["welf"] / summary["tinc"] * 100
    summary["minc"] = summary.groupby("year")["welf"].transform("mean")
    return summary.sort_values(["year", "decile"]).reset_index(drop=True)


def make_plot(summary: pd.DataFrame, output_path: Path) -> None:
    filtered = summary[summary["decile"].isin(TARGET_DECILES)].copy()
    fig, ax_left = plt.subplots(figsize=(11, 6))
    ax_right = ax_left.twinx()

    for decile in TARGET_DECILES:
        subset = filtered[filtered["decile"] == decile]
        axis = ax_right if decile == 10 else ax_left
        axis.plot(
            subset["year"],
            subset["share"],
            marker="o",
            linewidth=2,
            color=DECILE_COLORS[decile],
            label=DECILE_LABELS[decile],
        )

    ax_left.set_xlabel("")
    ax_left.set_ylabel("Income share, bottom to middle deciles")
    ax_right.set_ylabel("Income share, top decile")

    years = filtered["year"].drop_duplicates().sort_values()
    if not years.empty:
        start_year = int(years.min())
        end_year = int(years.max())
        ax_left.set_xticks(list(range(start_year, end_year + 1, 3)))

    left_handles, left_labels = ax_left.get_legend_handles_labels()
    right_handles, right_labels = ax_right.get_legend_handles_labels()
    ax_left.legend(
        left_handles + right_handles,
        left_labels + right_labels,
        loc="lower center",
        ncol=4,
        frameon=False,
    )
    ax_left.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    args = parse_args()
    data = load_dataset(args.input)
    summary = build_decile_table(data)

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    args.output_plot.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.output_csv, index=False)
    make_plot(summary, args.output_plot)

    print(f"Input used: {args.input.resolve()}")
    print(f"CSV saved to: {args.output_csv.resolve()}")
    print(f"Plot saved to: {args.output_plot.resolve()}")


if __name__ == "__main__":
    main()