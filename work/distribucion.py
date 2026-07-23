import math
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

SCRIPT_DIR = Path(__file__).resolve().parent

# =================== OBJETIVO =====================
# Replicar el estilo de grafico "Daily income per capita" (Our World in Data)
# usando la metodologia propuesta por el jefe (equivalente Stata):
#
#   keep if inlist(year,2015,2026)
#   egen qt = xtile(avg_welfare), weight(pop) by(year) n(1000)
#   collapse avg_welfare [aw=pop], by(year qt)
#
# En vez de una densidad KDE, la curva se construye a partir de los propios
# 1000 cuantiles poblacionales (bins de igual masa de poblacion).
# ====================================================

INPUT_CSV = SCRIPT_DIR / "prepared_daniel_input.csv"
YEARS = [2000, 2015, 2026]
N_QUANTILES = 1000
POVERTY_LINE = 3.0  # linea de pobreza internacional (2021 PPP)

df = pd.read_csv(INPUT_CSV)


def assign_weighted_xtile(group: pd.DataFrame, n: int = N_QUANTILES) -> pd.DataFrame:
	"""
	Ordena por welf, acumula la poblacion y asigna cada fila al cuantil (1..n)
	segun en que fraccion de la poblacion acumulada cae.
	"""
	ordered = group.sort_values('welf').copy()
	total_pop = ordered['pop'].sum()
	cum_share = ordered['pop'].cumsum() / total_pop
	ordered['qt'] = cum_share.apply(lambda s: min(n, max(1, math.ceil(s * n))))
	return ordered


def build_quantile_table(data: pd.DataFrame, years: list[int], n: int = N_QUANTILES) -> pd.DataFrame:
	"""
	Devuelve una fila por (year, qt) con el bienestar promedio ponderado.
	"""
	filtered = data[data['year'].isin(years)].copy()
	with_qt = pd.concat(
		[assign_weighted_xtile(group, n) for _, group in filtered.groupby('year')],
		ignore_index=True,
	)
	collapsed = (
		with_qt.groupby(['year', 'qt'])
		.apply(lambda x: np.average(x['welf'], weights=x['pop']), include_groups=False)
		.reset_index(name='welf')
		.sort_values(['year', 'qt'])
		.reset_index(drop=True)
	)
	return collapsed


def density_from_quantiles(welf_sorted: np.ndarray, n: int = N_QUANTILES, smooth_window: int = 15) -> np.ndarray:
	"""
	Convierte los 1000 puntos de igual masa poblacional (1/n cada uno) en una
	curva de densidad: como cada paso de cuantil representa siempre 1/n de la
	poblacion, la densidad local es (1/n) dividido entre cuanto "espacio" de
	ingreso (en log10) ocupa ese paso. Se suaviza con una media movil para
	evitar el ruido propio de trabajar con puntos discretos.
	"""
	log_welf = np.log10(welf_sorted)
	local_width = np.gradient(log_welf)  # ancho en log10(welf) por cada 1/n de poblacion
	density = (1.0 / n) / local_width

	if smooth_window > 1:
		kernel = np.ones(smooth_window) / smooth_window
		density = np.convolve(density, kernel, mode='same')

	return density


def style_axis(ax: plt.Axes) -> None:
	ax.set_xscale('log')
	ax.set_xlim(0.2, 200)
	ax.set_ylim(bottom=0)
	ticks = [0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200]
	ax.set_xticks(ticks)
	ax.set_xticklabels([f"${t:g}" for t in ticks])
	ax.set_yticks([])
	for spine in ["top", "right", "left"]:
		ax.spines[spine].set_visible(False)
	ax.axvline(POVERTY_LINE, color="#999999", linestyle=":", linewidth=1.2)
	ax.text(POVERTY_LINE, ax.get_ylim()[1] * 0.85, "International\nPoverty Line",
			rotation=90, ha='right', va='top', fontsize=9, color="#777777")


def make_density_plot(quantile_table: pd.DataFrame, year: int, output_path: str) -> None:
	subset = quantile_table[quantile_table['year'] == year].sort_values('qt')
	welf_sorted = subset['welf'].to_numpy()
	density = density_from_quantiles(welf_sorted)

	fig, ax = plt.subplots(figsize=(11, 6.5))
	ax.fill_between(welf_sorted, density, color="#C6304B", alpha=0.9, linewidth=0)
	style_axis(ax)

	ax.set_xlabel("Daily income per capita\n(in international-$ in 2021 PPP prices; log axis)", fontsize=11)
	ax.set_title(f"Daily income per capita\n(in international-$ in 2021 PPP prices; log axis)\n\n{year}",
				 fontsize=14, fontweight='bold')

	plt.tight_layout()
	fig.savefig(output_path, dpi=300, bbox_inches='tight')
	plt.close(fig)
	print(f"Grafico guardado: {output_path}")


def make_combined_plot(quantile_table: pd.DataFrame, years: list[int], output_path: str) -> None:
	colors = {2000: "#2F42ED", 2015: "#1EB910", 2026: "#D81B60"}

	fig, ax = plt.subplots(figsize=(11, 6.5))
	for year in years:
		subset = quantile_table[quantile_table['year'] == year].sort_values('qt')
		welf_sorted = subset['welf'].to_numpy()
		density = density_from_quantiles(welf_sorted)
		color = colors.get(year, None)
		ax.fill_between(welf_sorted, density, color=color, alpha=0.35, linewidth=0, label=str(year))
		ax.plot(welf_sorted, density, color=color, linewidth=1.8, alpha=0.9)

	style_axis(ax)
	ax.set_xlabel("Daily income per capita\n(in international-$ in 2021 PPP prices; log axis)", fontsize=11)
	ax.set_title("Daily income per capita: how the distribution shifted\n(2000, 2015, 2026 overlaid)",
				 fontsize=14, fontweight='bold')
	ax.legend(loc='upper right', frameon=False, title="Year")

	plt.tight_layout()
	fig.savefig(output_path, dpi=300, bbox_inches='tight')
	plt.close(fig)
	print(f"Grafico guardado: {output_path}")


# 1. keep if inlist(year, ...) + 2. egen qt = xtile(...) + 3. collapse ... by(year qt)
quantile_table = build_quantile_table(df, YEARS, N_QUANTILES)

OUTPUT_CSV = SCRIPT_DIR / "distribution_quantile_table.csv"
quantile_table.to_csv(OUTPUT_CSV, index=False)
print(f"Tabla de cuantiles guardada: {OUTPUT_CSV}")
print(quantile_table.head())
print(quantile_table.tail())

for year in YEARS:
	make_density_plot(quantile_table, year, SCRIPT_DIR / f"distribution_density_{year}.png")

make_combined_plot(quantile_table, YEARS, SCRIPT_DIR / "distribution_density_combined.png")


