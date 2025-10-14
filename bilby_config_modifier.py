import re
import ast
import math
import pickle
import subprocess
import numpy as np
import configargparse
from pycbc.conversions import mass1_from_mtotal_q, mass2_from_mtotal_q

def parse_inclination(value):
    try:
        return eval(value, {'pi': math.pi})
    except Exception:
        raise configargparse.ArgumentTypeError(f'Inclination must be a number or expression like "pi/3", got: {value}')

# ---- Parse config.ini and extract label & outdir ----
parser = configargparse.ArgParser()
parser.add_argument('--total_mass',
                    type=float,
                    choices=[200, 250, 300, 350, 400, 450, 500],
                    default=300,
                    help='Total mass of the binary system (default: 300).')
parser.add_argument('--mass_ratio',
                    type=float,
                    choices=[1, 2, 3, 4, 5],
                    default=4,
                    help='Mass ratio of the binary system (default: 4).')
parser.add_argument('--spin',
                    type=float,
                    choices=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                    default=0.7,
                    help='Spin of the binary system (default: 0.7).')
parser.add_argument('--spin_1',
                    type=float,
                    choices=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                    help='Spin of the primary black hole (default: 0.7).')
parser.add_argument('--spin_2',
                    type=float,
                    choices=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                    help='Spin of the secondary black hole (default: 0.7).')
parser.add_argument('--inclination',
                    type=parse_inclination,
                    choices=[0, math.pi/6, math.pi/3, math.pi/2],
                    default=math.pi/3,
                    help='Inclination angle of the binary system (default: pi/3).')
parser.add_argument('--tilt_1',
                    type=float,
                    choices=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0],
                    default=0.2,
                    help='Tilt of the primary black hole (default: 0.2).')
parser.add_argument('--tilt_2',
                    type=float,
                    choices=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0],
                    default=0.8,
                    help='Tilt of the secondary black hole (default: 0.8).')
parser.add_argument('--snr_target',
                    type=float,
                    choices=[10, 20, 30, 40, 50, 60, 70, 75, 80, 90, 100],
                    default=75,
                    help='Target SNR for the injection (default: 75).')

parser.add_argument('--config_file',
                    nargs='+',
                    default=['10', '13', '20'],
                    help='List of configuration files (default: [10, 13, 20]).')
parser.add_argument('--n_live',
                    type=int,
                    default=1000,
                    help='Number of live points for the sampler (default: 1000).')
parser.add_argument('--partition',
                    type=str,
                    default='sciama4.q',
                    help='Scheduler partition for the run.')
parser.add_argument('label',
                    type=str,
                    help='Label for the run, used to identify the output files.')
parser.add_argument('outdir',
                    type=str,
                    help='Output directory for the run.')

args, unknown = parser.parse_known_args()

print(f'Label: {args.label}')
print(f'Output Directory: {args.outdir}')
print(f'Scheduler Partition: {args.partition}')
print(f"Live Points: {args.n_live}")
print(args.config_file)

# --- Build config path ---
CONFIG_FILES = [f'bilby_configs/config_{name}Hz.ini' for name in args.config_file]

# ---- Update injection parameters in config files ----
for config_path, freq in zip(CONFIG_FILES, args.config_file):
    with open(config_path, 'r') as file:
        original_content = file.read()

    # ---- Update the injection parameters ----
    match = re.search(r'injection-dict=(\{.*?\})', original_content)
    injection_dict_str = match.group(1)
    injection_dict = ast.literal_eval(injection_dict_str)
    
    mass_1 = mass1_from_mtotal_q(args.total_mass, args.mass_ratio)
    mass_2 = mass2_from_mtotal_q(args.total_mass, args.mass_ratio)
    if args.spin_1:
        spin_1 = args.spin_1
    else:
        spin_1 = args.spin
    
    if args.spin_2:
        spin_2 = args.spin_2
    else:
        spin_2 = args.spin

    injection_dict['mass_1'] = mass_1
    injection_dict['mass_2'] = mass_2
    injection_dict['a_1'] = spin_1
    injection_dict['a_2'] = spin_2
    injection_dict['theta_jn'] = args.inclination
    injection_dict['tilt_1'] = args.tilt_1
    injection_dict['tilt_2'] = args.tilt_2

    new_content = original_content.replace(injection_dict_str, str(injection_dict))

    # ---- Update the label and outdir ----
    new_label = f'{args.label}_{freq}'
    new_content = re.sub(r'^label\s*=\s*\S+', f'label={new_label}', new_content, flags=re.MULTILINE)
    new_content = re.sub(r'^outdir\s*=\s*\S+', f'outdir=./analysis_results/{args.outdir}', new_content, flags=re.MULTILINE)
    new_content = re.sub(r'^scheduler-args=partition\s*=\s*.*', f'scheduler-args=partition={args.partition}', new_content, flags=re.MULTILINE)
    new_content = re.sub(r'\bnlive\s*=\s*\d+', f'nlive={args.n_live}', new_content, flags=re.MULTILINE)

    with open(config_path, 'w') as file:
        file.write(new_content)
    print(f'Modified: {config_path}')

# ---- Run bilby_pipe ----
for config_path in CONFIG_FILES:
    print(f"Running: bilby_pipe {config_path}")
    subprocess.run(["bilby_pipe", config_path], check=True)

# ---- Compute new Luminosity distance from SNR ----
with open(f"./analysis_results/{args.outdir}/data/{args.label}_{args.config_file[0]}_data0_1126259642-413_generation_data_dump.pickle".format(args.label), "rb") as file:
    data = pickle.load(file)

snr_squared = sum(ifo.meta_data["matched_filter_SNR"]**2 for ifo in data.interferometers)
snr_current = np.real(snr_squared**0.5)

lum_dist = data.meta_data['injection_parameters']['luminosity_distance']

scaling_factor = snr_current / args.snr_target
new_lum_dist = lum_dist * scaling_factor

print(f"Current SNR: {snr_current}, \nTarget SNR: {args.snr_target}, \nScaling factor: {scaling_factor}, \nOld luminosity distance: {lum_dist}, \nNew luminosity distance: {new_lum_dist}")

# --- Modify .ini file with updated Luminosity distance ----
for config_path in CONFIG_FILES:
    with open(config_path, "r") as file:
        original_content = file.read()

    match = re.search(r'injection-dict=(\{.*?\})', original_content)
    injection_dict_str = match.group(1)
    injection_dict = ast.literal_eval(injection_dict_str)

    injection_dict['luminosity_distance'] = new_lum_dist

    new_content = original_content.replace(injection_dict_str, str(injection_dict))

    with open(config_path, "w") as file:
        file.write(new_content)
    print(f"Modified: {config_path}")