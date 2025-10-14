from config import FILE_PATH, color_map

import lal
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from matplotlib.ticker import FixedLocator
from bilby.core.result import read_in_result
from gwpy.frequencyseries import FrequencySeries
from pesummary.utils.samples_dict import MultiAnalysisSamplesDict
from pesummary.gw.conversions.spins import viewing_angle_from_inclination

from lalsimulation import (
    SimInspiralFD, SimInspiralCreateModeArray, SimInspiralModeArrayActivateMode,
    SimInspiralWaveformParamsInsertModeArray, NRSur7dq4
)

# Functions to load the recovery posteriors and the injection values from the .json files
def data_loader(loc, label, get_viewing_angle):
    data = MultiAnalysisSamplesDict.from_files(loc, disable_prior=True)
    injection_values = read_in_result(loc[label[0]]).injection_parameters
    if get_viewing_angle:
        for i in range(len(label)):
            data[label[i]]['viewing_angle'] = viewing_angle_from_inclination(data[label[i]]['theta_jn'])
        injection_values['viewing_angle'] = viewing_angle_from_inclination(injection_values['theta_jn'])
    return data, injection_values

def generate_filename(label, parent_file, param):
    result = {}
    for i in range(len(label)):
        result[label[i]] = FILE_PATH.format(outdir=parent_file, param=param, freq=label[i])
    return result

def load_data(parameter_list, label, parent_file, get_viewing_angle=True):
    data_dict = {}
    for param in parameter_list:
        loc = generate_filename(label, parent_file, param)
        data_dict[param] = data_loader(loc, label, get_viewing_angle=get_viewing_angle)

    return data_dict

# Functions to generate and display the Mahalanobis recovery scores
def generate_random_points_below_kde(data_nd, n_samples):
    kde = gaussian_kde(data_nd.T)
    return kde.resample(n_samples).T

def calculate_mahal_score(param_names, data_nd, injected_point, n_samples, sigma_multiplier, bias_label=''):
    accepted_samples = generate_random_points_below_kde(data_nd, n_samples)
    original_mean = np.mean(data_nd, axis=0)
    cov_matrix = np.cov(data_nd, rowvar=False)
    cov_inv = np.linalg.inv(cov_matrix)
    
    count_within_sigma = 0
    for shift_point in accepted_samples:
        shift_vector = shift_point - original_mean
        shifted_mean = original_mean + shift_vector

        diff = injected_point - shifted_mean
        mahal_dist = np.sqrt(diff.T @ cov_inv @ diff)

        if mahal_dist <= sigma_multiplier:
            count_within_sigma += 1

    mahal_recovery_score = count_within_sigma / n_samples

    return mahal_recovery_score

def create_mahal_recovery_score_dict(data, injected_values, param_groups, sigma_multiplier, num_loops=10000):
    mahal_recover_scores = {}
    labels = list(data.keys())

    for params in param_groups:
        if all(param in injected_values for param in params):
            injected_point = np.array([injected_values[param] for param in params])

            for label in labels:
                if all(param in data[label] for param in params):
                    data_label = np.array([data[label][param] for param in params]).T
                    mahal_score = calculate_mahal_score(
                        params, data_label, injected_point,
                        num_loops, sigma_multiplier, bias_label=label
                    )
                    mahal_recover_scores[f"{' vs '.join(params)} f_22_{label} Mahalanobis Recovery Score for {sigma_multiplier:.2f} sigma"] = mahal_score

    return mahal_recover_scores

def print_mahal_recovery_scores(results, name):
    print(f"{name}:")
    for i, (key, value) in enumerate(results.items()):
        if i == 0:
            num = key
        if key[:2] == num[:2]:
            print(f"{key}: {value}")
        else:
            print()
            print(f"{key}: {value}")
        num = key
    print()

# Functions to generate gravitational waveforms and their harmonic multipoles
def generate_frequency_domain_waveform(m1, m2, spin1, spin2, distance, inclination, phiRef, flow):
    """Generates frequency-domain gravitational waveforms."""
    hpf, hcf = SimInspiralFD(
        m1 * lal.MSUN_SI,           # Mass for object 1
        m2 * lal.MSUN_SI,           # Mass for object 2
        *spin1,                     # Spin components (x, y, z) for object 1
        *spin2,                     # Spin components (x, y, z) for object 2
        distance * 1e6 * lal.PC_SI, # Convert distance from Mpc to meters
        inclination,                # Inclination
        phiRef,                     # Orientation
        0.,                         # longascnodes
        0.,                         # eccentricity
        0.,                         # meanperano
        1. / 2048,                  # Frequency step df
        flow,                       # Flow
        1024,                       # Maximum frequency
        20.,                        # Reference frequency
        lal.CreateDict(),
        NRSur7dq4
    )
    
    return FrequencySeries(hpf.data.data, df=hpf.deltaF, f0=0.), FrequencySeries(hcf.data.data, df=hcf.deltaF, f0=0.)

def generate_harmonic_multipoles(m1, m2, spin1, spin2, distance, inclination, phiRef, flow, mode):
    LAL_parameters = lal.CreateDict()
    _mode_array = SimInspiralCreateModeArray()
    SimInspiralModeArrayActivateMode(_mode_array, mode[0], mode[1])
    SimInspiralWaveformParamsInsertModeArray(LAL_parameters, _mode_array)

    hpf, hcf = SimInspiralFD(
        m1 * lal.MSUN_SI,           # Mass for object 1
        m2 * lal.MSUN_SI,           # Mass for object 2
        *spin1,                     # Spin components (x, y, z) for object 1
        *spin2,                     # Spin components (x, y, z) for object 2
        distance * 1e6 * lal.PC_SI, # Convert distance from Mpc to meters
        inclination,                # Inclination
        phiRef,                     # Orientation
        0.,                         # longascnodes
        0.,                         # eccentricity
        0.,                         # meanperano
        1. / 1024,                  # Frequency step df
        flow,                       # Flow
        1024,                       # Maximum frequency
        40,                         # Reference frequency
        LAL_parameters,
        NRSur7dq4
    )
    
    return FrequencySeries(hpf.data.data, df=hpf.deltaF, f0=0.), FrequencySeries(hcf.data.data, df=hcf.deltaF, f0=0.)

def style_axis(ax):
    """Apply consistent styling to a matplotlib axis."""
    ax.tick_params(axis='both', colors='black')
    ax.xaxis.label.set_color('black')
    ax.yaxis.label.set_color('black')
    ax.title.set_color('black')
    ax.patch.set_alpha(0)
    for spine in ax.spines.values():
        spine.set_color('black')
    ax.grid(False)

def add_harmonic_lines(ax, harmonic_freqs):
    """Add vertical harmonic reference lines and tidy up tick locators."""
    for f in harmonic_freqs:
        ax.axvline(f, color='black', linestyle=":")
    ax.xaxis.set_major_locator(FixedLocator(harmonic_freqs + [100]))
    ax.xaxis.set_major_formatter(plt.ScalarFormatter())
    ax.xaxis.set_minor_locator(FixedLocator([]))


def plot_waveform(ax, waveform, multipole_dict, f_cut, dict_key, linestyle="-", mode_linestyle="--", plot_modes=None, multipole_colours=None):
    """Plot a full waveform and optionally its individual modes."""
    # Full waveform
    inds = np.argwhere(waveform.frequencies.value >= f_cut)
    ax.loglog(waveform.frequencies[inds], np.abs(waveform)[inds],
              color=color_map[dict_key], linestyle=linestyle)

    # Mode components
    harmonic_locators = [f_cut]
    if plot_modes and multipole_dict:
        for mode, show in plot_modes.items():
            if not show:
                continue
                           
            mode_data = multipole_dict[mode]
            freq = f_cut * (mode[0] / 2)
            inds = np.argwhere(mode_data.frequencies.value >= freq)
            ax.loglog(
                mode_data.frequencies[inds],
                np.abs(mode_data)[inds],
                color=(multipole_colours or {}).get(mode, color_map[dict_key]),
                linestyle=mode_linestyle,
                label=f"{mode} Multipole"
            )
            harmonic_locators.append(f_cut * (mode[0] / 2))
    
    return harmonic_locators