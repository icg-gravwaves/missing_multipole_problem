# The Missing Multipole Problem: Investigating biases from model starting frequency in gravitational-wave analyses -- Data Release
R. Ursell<sup>1</sup>, C. Hoy<sup>1</sup>, I. Harry<sup>1</sup>, L. K. Nuttall<sup>1</sup>

<sub>1. University of Portsmouth, Portsmouth, PO1 3FX, United Kingdom</sub>

This is the data release for the paper _"The Missing Multipole Problem: Investigating biases from model starting frequency in gravitational-wave analyses"_.  
Here we present the results obtained as part of this study, the configuration files used to produce them, and the plotting code used to generate the figures in the paper.

We encourage use of these data in future work. If you use the material provided here, please cite the paper using the reference:

        @article{
        }

---

# Dependencies
Our results were produced using **Python 3.10**.  To reproduce our results, the following Python packages are required:

## Gravitational-wave packages
- `bilby` – v2.2.2.1
- `lalsimulation` – v5.4.0  

In addition, Plotting notebooks can be run with the following Python packages:

## General packages
- `numpy` – v1.26.4
- `matplotlib` – v3.9.4  
- `scipy` – v1.13.1
- `pesummary` - v1.5.3

---

# Repository Structure
The repository is organized as follows:

- **[data](./data)** – All results, separated by run.
- **[bilby_configs](./bilby_configs)** – Example `config.ini` files used in the analyses.
- **[plots](./plots)** – Plots included in the paper, organized by type.
- **[plotting_notebooks](./plotting_notebooks)** – Jupyter notebooks that generate the paper's plots and the Mahalanobis recovery scores.

---

# License
The data is this repository is released under the MIT License. See [LICENSE](./LICENSE) for details.
