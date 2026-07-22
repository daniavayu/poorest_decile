from __future__ import annotations

import argparse
import math
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

# =================== CONFIGURATION =====================
# Required input dataset columns: year, welfare level, and population weight
REQUIRED_COLUMNS = {"year", "welf", "pop"}
# Default input file name (prepared by prepare_daniel_input.R)
DEFAULT_INPUT_NAME = "prepared_daniel_input.csv"
# Deciles to plot and analyze (1=poorest, 10=richest)
TARGET_DECILES = [1, 2, 5, 10]
# Display labels for each decile in the plot legend
DECILE_LABELS = {
	1: "Poorest",
	2: "Next poorest",
	5: "Middle",
	10: "Top",
}
# Color scheme for each decile line in the plot
DECILE_COLORS = {
	1: "#2F42ED",
	2: "#D81B60",
	5: "#1EB910",
	10: "#F4D10D",
}


# ==================== FUNCTIONS ====================

def parse_args() -> argparse.Namespace:
	"""
	Parse command-line arguments.
	Allows users to override default input/output file paths.
	Usage: python script.py --input data.csv --output-csv results.csv --output-plot chart.png
	"""
	script_dir = Path(__file__).resolve().parent
	parser = argparse.ArgumentParser(
		description="Replicate Nishant's weighted-decile workflow using Daniel's prepared input."
	)
	parser.add_argument(
		"--input",
		type=Path,
		default=script_dir / DEFAULT_INPUT_NAME,
		help="Path to the prepared Daniel input CSV.",
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
	"""
	Load and validate the input dataset.
	Checks that required columns exist and removes rows with missing values.
	Returns only the columns needed: year, welfare level, and population.
	"""
	data = pd.read_csv(file_path)
	missing = REQUIRED_COLUMNS.difference(data.columns)
	if missing:
		missing_list = ", ".join(sorted(missing))
		raise ValueError(f"Missing required columns: {missing_list}")

	return data.loc[:, ["year", "welf", "pop"]].dropna().copy()


def assign_weighted_deciles(group: pd.DataFrame) -> pd.DataFrame:
	"""
	Assign population-weighted deciles within a single year.
	Logic: sort by welfare level, compute cumulative population share,
	and assign each observation to a decile based on where it falls in that cumulative distribution.
	This matches Nishant's Stata command: egen decile = xtile(welf), weight(pop) by(year) n(10)
	"""
	ordered = group.sort_values("welf").copy()
	total_pop = ordered["pop"].sum()
	if total_pop <= 0:
		raise ValueError("Population weights must sum to a positive value within each year.")

	# Cumulative population share: what fraction of the year's population is at or below this welfare level?
	cumulative_share = ordered["pop"].cumsum() / total_pop
	# Assign decile: ceil(cum_share * 10) gives 1-10 based on which 10% band the person falls into
	ordered["decile"] = cumulative_share.apply(
		lambda value: min(10, max(1, math.ceil(value * 10)))
	)
	return ordered


def build_decile_table(data: pd.DataFrame) -> pd.DataFrame:
	"""
	Build the core summary table of decile-level statistics.
	Steps:
	  1. Assign deciles separately for each year (so each year has its own 10% groups)
	  2. Compute population-weighted welfare for each observation
	  3. Aggregate by year and decile: sum weighted welfare and population
	  4. Derive decile-level welfare (weighted mean) and its share of the annual total
	  5. Add reference variables: tinc (annual total) and minc (annual mean)
	This replicates Nishant's Stata: collapse welf [aw=pop], by(year decile)
	"""
	# Step 1: Apply decile assignment to each year independently
	decile_frame = pd.concat(
		[assign_weighted_deciles(group) for _, group in data.groupby("year")],
		ignore_index=True,
	)
	
	# Step 2: Compute weighted welfare (welfare * population weight)
	decile_frame["weighted_welf"] = decile_frame["welf"] * decile_frame["pop"]

	# Step 3: Aggregate by year and decile
	summary = (
		decile_frame.groupby(["year", "decile"], as_index=False)
		.agg(weighted_welf_sum=("weighted_welf", "sum"), pop_sum=("pop", "sum"))
	)
	# Step 4: Derive decile-level welfare as population-weighted mean within the decile
	summary["welf"] = summary["weighted_welf_sum"] / summary["pop_sum"]
	summary = summary.drop(columns=["weighted_welf_sum", "pop_sum"])

	# Step 5: Add reference variables for each year
	# tinc = total income/welfare for the year (sum across all deciles)
	summary["tinc"] = summary.groupby("year")["welf"].transform("sum")
	# share = this decile's welfare as a percentage of the annual total
	summary["share"] = summary["welf"] / summary["tinc"] * 100
	# minc = mean welfare per decile for the year (for reference)
	summary["minc"] = summary.groupby("year")["welf"].transform("mean")
	return summary.sort_values(["year", "decile"]).reset_index(drop=True)


def make_plot(summary: pd.DataFrame, output_path: Path) -> None:
	"""
	Create a publication-quality chart showing welfare share over time for selected deciles.
	Design: deciles 1, 2, 5 use the left y-axis; decile 10 uses a right y-axis
	(because the top decile's share is so large it would compress the visualization otherwise).
	"""
	# Filter to only the deciles we want to display
	filtered = summary[summary["decile"].isin(TARGET_DECILES)].copy()
	fig, ax_left = plt.subplots(figsize=(11, 6))
	# Create a second y-axis for the top decile (right side of plot)
	ax_right = ax_left.twinx()

	# Plot each decile as a separate line
	for decile in TARGET_DECILES:
		subset = filtered[filtered["decile"] == decile]
		# Top decile uses right axis; others use left axis
		axis = ax_right if decile == 10 else ax_left
		axis.plot(
			subset["year"],
			subset["share"],
			marker="o",
			linewidth=2,
			color=DECILE_COLORS[decile],
			label=DECILE_LABELS[decile],
		)

	# Axis labels
	ax_left.set_xlabel("")
	ax_left.set_ylabel("Income share, bottom to middle deciles")
	ax_right.set_ylabel("Income share, top decile")

	# Set x-axis ticks at regular 3-year intervals
	years = filtered["year"].drop_duplicates().sort_values()
	if not years.empty:
		start_year = int(years.min())
		end_year = int(years.max())
		ax_left.set_xticks(list(range(start_year, end_year + 1, 3)))

	# Combine legends from both axes into a single legend at the bottom
	left_handles, left_labels = ax_left.get_legend_handles_labels()
	right_handles, right_labels = ax_right.get_legend_handles_labels()
	ax_left.legend(
		left_handles + right_handles,
		left_labels + right_labels,
		loc="lower center",
		ncol=5,
		frameon=False,
		fontsize=9,
	)
	ax_left.grid(axis="y", alpha=0.25)
	fig.tight_layout()
	fig.savefig(output_path, dpi=300, bbox_inches="tight")
	plt.close(fig)


def main() -> None:
	"""
	Main execution function: orchestrates the full workflow.
	  1. Parse command-line arguments
	  2. Load and validate the input dataset
	  3. Compute decile-level statistics
	  4. Export the results as CSV and PNG chart
	  5. Print confirmation messages
	"""
	args = parse_args()
	input_path = args.input.resolve()
	
	# Load the prepared input data (year, welf, pop)
	data = load_dataset(input_path)
	
	# Compute decile assignments and aggregate statistics
	summary = build_decile_table(data)

	# Ensure output directories exist
	args.output_csv.parent.mkdir(parents=True, exist_ok=True)
	args.output_plot.parent.mkdir(parents=True, exist_ok=True)
	
	# Export the summary table and visualization
	summary.to_csv(args.output_csv, index=False)
	make_plot(summary, args.output_plot)

	# Confirmation output
	print(f"Input used: {input_path}")
	print(f"CSV saved to: {args.output_csv}")
	print(f"Plot saved to: {args.output_plot}")


# Entry point: runs main() when script is executed directly
if __name__ == "__main__":
	main()
