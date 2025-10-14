# The Missing Multipole Problem: Investigating biases from model starting frequency in gravitational-wave analyses -- Data Release
This is the data release for the paper _"The Missing Multipole Problem: Investigating biases from model starting frequency in gravitational-wave analyses"_.  
Here we present the results obtained as part of this study, the configuration files used to produce them, and the plotting code used to generate the figures in the paper.

---

# Dependencies
Our results and graphs were produced using **Python 3.10**.  
To reproduce our results or run the Jupyter notebooks in [plotting_notebooks](./plotting_notebooks/), the following Python packages are required:

## Gravitational-wave packages
- `bilby` – vX.XX  
- `lal` – vX.XX  
- `lalsimulation` – vX.XX  
- `gwpy` – vX.XX  
- `pesummary` – vX.XX  

## General packages
- `numpy` – vX.XX  
- `matplotlib` – vX.XX  
- `scipy` – vX.XX  
- `configargparse` – vX.XX

---

# Repository Structure
The repository is organized as follows:

- **[analysis_results](./analysis_results)** – All results, separated by run.
- **[bilby_configs](./bilby_configs)** – Example `config.ini` files used in the analyses. The actual config files for each analysis can be found in the corresponding subdirectory of [analysis_results](./analysis_results).
- **[plots](./plots)** – All plots included in the paper, organized by type.
- **[plotting_notebooks](./plotting_notebooks)** – Jupyter notebooks that generate the paper's plots and the Mahalanobis recovery scores.

---

# License
This work is released under the MIT License. See [LICENSE](./LICENSE) for details.
