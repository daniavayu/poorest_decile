This folder recreates Nishant's decile workflow using Daniel's source data.

Files:
- prepare_daniel_input.R: loads Daniel's Rda file, merges national population from PIP, and writes a prepared CSV with the columns expected by the Python workflow.
- bottom10percent_from_daniel.py: runs the decile aggregation and plot logic adapted from Nishant's Python script.

Expected flow:
1. Run prepare_daniel_input.R.
2. Run bottom10percent_from_daniel.py.

Outputs created in this folder:
- prepared_daniel_input.csv
- bottom10percent_output.csv
- bottom10percent_plot.png

Notes:
- The preparation step assigns each country-year bin a population weight equal to national population divided by the number of bins observed for that country-year.
- The R step stops if any country-year from Daniel's data cannot be matched to national population from PIP.