import os
from matplotlib import font_manager
import matplotlib.pyplot as plt

font_path = '../TimesNewRoman.ttf'
font_manager.fontManager.addfont(font_path)
prop = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = prop.get_name()
os.environ["GWPY_RCPARAMS"] = "False"
plt.style.use("../MATPLOTLIB.sty")

# Base file path to outdirs and data
FILE_PATH = "../analysis_results/{outdir}/final_result/{param}_{freq}_data0_1126259642-413_analysis_H1L1V1_result.json"

# Starting frequencies for injections
STARTING_FREQUENCIES = ['10', '13', '20']

# Dictionary keys for different starting frequencies
DICT_KEYS = ['f_22_10', 'f_22_13', 'f_22_20']

# Generic kwargs for legend
legend_kwargs = {
    "loc": "upper left", "frameon": True, "ncol": 1, "handler_map": None,
    "framealpha": 0.85, "facecolor": "w", "edgecolor": "w"
}

# Dictionary for commonly used colours in plots
color_map = {
    DICT_KEYS[0]: "#0072B2",
    DICT_KEYS[1]: "#009E73",
    DICT_KEYS[2]: "#E69F00",
}

# Dictionary for commonly used labels in plots
label_map = {
    DICT_KEYS[0]: r"$f_{22} = 10\, \mathrm{Hz}$",
    DICT_KEYS[1]: r"$f_{22} = 13\, \mathrm{Hz}$",
    DICT_KEYS[2]: r"$f_{22} = 20\, \mathrm{Hz}$",
}