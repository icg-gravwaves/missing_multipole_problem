import subprocess
import configargparse
from pathlib import Path

# ---- Configuration for the script ----

# --- Parse argument ---
parser = configargparse.ArgumentParser(description="Run bilby_pipe with selected config.")
parser.add_argument("--freq",
                    nargs='+',
                    default=["10", "13", "20"], 
                    help="Frequency to select the config file (default: 10, 13, 20).")
args, unknown = parser.parse_known_args()

CONFIG_FILES = [f"configs/config_{freq}Hz.ini" for freq in args.freq]

for config_path in CONFIG_FILES:
    # ---- Step 1: Parse config.ini and extract label & outdir ----
    parser = configargparse.ArgParser(default_config_files=[config_path])
    parser.add_argument('--label', type=str, required=True)
    parser.add_argument('--outdir', type=str, required=True)

    config_args, unknown = parser.parse_known_args()
    print(f"Label: {config_args.label}")
    print(f"Output directory: {config_args.outdir}")

    # ---- Step 2: Run bilby_pipe ----
    print(f"Running: bilby_pipe {config_path}")
    subprocess.run(["bilby_pipe", config_path], check=True)

    # ---- Step 3: Modify .sh scripts ----
    env_vars = """export LAL_DATA_PATH=/users/${USER}
    export HDF5_USE_FILE_LOCKING=False
    export OMP_NUM_THREADS=1
    export OMP_PROC_BIND=False
    """

    script_paths = list(Path(config_args.outdir).glob(f"submit/{config_args.label}_data0_*_H1L1V1.sh"))

    for script_path in script_paths:
        with open(script_path, "r") as file:
            original_content = file.read()

        lines = original_content.splitlines()
        new_content = "\n".join([lines[0], env_vars.rstrip()] + lines[1:])

        with open(script_path, "w") as file:
            file.write(new_content)
        print(f"Modified: {script_path}")

    # ---- Step 4: Submit master SLURM script ----
    master_slurm = Path(config_args.outdir) / "submit" / f"slurm_{config_args.label}_master.sh"

    print(f"Submitting job: sbatch {master_slurm}")
    subprocess.run(["sbatch", str(master_slurm)], check=True)