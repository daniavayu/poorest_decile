use "C:\Users\wb562356\OneDrive - WBG\Documents\Research\Inequality\COVID19\CovidInequality\ReplicationFiles_WBER_April2026\02-inputdata\PIP\GlobalDist1000bins_1990_2026_20260324_2017_01_02_PROD.dta", clear

forval yr = `r(min)'/`r(max)' {
preserve
keep if `yr' == year
egen decile = xtile(welf), weight(pop) by(year) n(10)
collapse welf [aw=pop], by(year decile)
cap append using `datasofar'
tempfile datasofar
save `datasofar', replace
restore
}
use `datasofar', clear


bys year: egen tinc = total(welf)
gen share = welf/tinc * 100
bys year: egen minc = mean(welf)

tw connected share year if decile==1 || connected share year if decile==2 ||connected share year if decile==5 || connected share year if decile==10, yaxis(2) legend(order(1 "Poorest" 2 "Next poorest" 3 "Middle" 4 "Top") row(1) ring(1) pos(6)) ytitle("Income share, bottom to middle deciles") ytitle("Income share, top decile", axis(2)) xtitle("") xlabel(1990(3)2026)