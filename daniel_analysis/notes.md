1) La data de Daniel es basicamente cada pais, cada ano y 1000 bins. 
Es una tabla con code, year, quintile, welb_b, pop. Es para cada ano posible. 

2) Luego, se trae la poblacion desde PIP. Esta es por pais, por ano (1981 a 2026), y el total.

3) Luego se merge estos dos datasets usando el pais y el ano. 

Nishant methodology: 

For each year, the global income distribution is constructed from the underlying bins in the dataset, where each observation represents an average income level (welf) and the corresponding population (pop). Observations are implicitly ranked from the lowest to the highest income, and population weights are used to divide the global population into ten equally sized groups (deciles). Thus, each decile represents approximately 10% of the world's population in a given year, rather than 10% of the observations. After assigning each bin to a population-weighted decile using the xtile command, the average income of each decile is computed as a population-weighted mean. Finally, each decile's share of total income is calculated by dividing its average income by the sum of the average incomes across all ten deciles, allowing the evolution of the global income distribution and the relative income shares of different population groups to be analyzed over time.