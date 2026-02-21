from water_vapor_age_experiment import WaterVaporAgeExperiment
import json
import os
import sys 

run_type = str(sys.argv[1])
rad_type = str(sys.argv[2])
n_start_month = int(sys.argv[3])
n_end_month = int(sys.argv[4])
base_dir = "/home/philbou/projects/def-rfajber/philbou/wva_exp"
# Read config from JSON file
config_path = os.path.join(f"{base_dir}/config", f"config_{run_type}_{rad_type}.json")
with open(config_path, "r") as f:
        config_dict = json.load(f) 

comment = config_dict.get("comment", "")

print(f"COMMENT: {comment}", file=sys.stdout, flush=True)

exp = WaterVaporAgeExperiment(config_dict)

exp.setup()

restart_file = config_dict.get("restart_file", None)

exp.run_experiment_variable_timestep(n_start_month, n_end_month,other_restart_file=restart_file)