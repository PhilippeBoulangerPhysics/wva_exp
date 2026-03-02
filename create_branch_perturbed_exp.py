from water_vapor_age_experiment import WaterVaporAgeExperiment
import json
import os
import sys 

run_type = str(sys.argv[1])
rad_type = str(sys.argv[2])
n_restart_month = int(sys.argv[3])
magnitude = float(sys.argv[4])
n = int(sys.argv[5])
RT42_bool = sys.argv[6].lower() == "true"
print(f"Run type: {run_type}")
print(f"Radiation type: {rad_type}")
print(f"Restart month: {n_restart_month}")
print(f"Perturbation magnitude: {magnitude}")
print(f"Number of perturbed branches: {n}")
print(f"RT42 boolean: {RT42_bool}")
base_dir = "/home/philbou/projects/def-rfajber/philbou/wva_exp"
# Read config from JSON file
base_config_path = os.path.join(f"{base_dir}/config", f"config_{run_type}_{rad_type}.json")
with open(base_config_path, "r") as f:
        base_config_dict = json.load(f) 

comment = base_config_dict.get("comment", "")



if RT42_bool:
    base_config_dict["comment"] = " | RT42 input"
    base_config_dict["exp_name_suffix"] = "_RT42"
    base_config_dict["horizontal_resolution"] = "T42"
    base_config_dict["dt_atm"] = 720
    base_config_dict["fixed_sst"] = True
    
exp_object = WaterVaporAgeExperiment(base_config_dict)
config_dict = base_config_dict.copy()
if RT42_bool: 
        exp_object.exp_name = "RT42_sst_0_bucket"
        run_type = "RT42_sst_0_bucket"

for i in range(n):
        restart_file = f"/home/philbou/projects/def-rfajber/philbou/wva_exp/restarts/{exp_object.exp_name}/{n_restart_month:04d}/res{n_restart_month:04d}_{magnitude}_{i}.tar.gz"
        if not os.path.exists(restart_file):
                raise FileNotFoundError(f"Restart file does not exist: {restart_file}")
        config_dict["restart_file"] = restart_file
        config_dict["comment"] = base_config_dict["comment"] +  f" | Perturbed restart file: {restart_file}"
        config_dict["exp_name_suffix"] = base_config_dict["exp_name_suffix"] + f"_{magnitude}_{i}"
        output_config_path = os.path.join(f"{base_dir}/config/perturbed_branch", f"config_{run_type}_{rad_type}_{magnitude}_{i}.json")
        with open(output_config_path, "w") as f:
                json.dump(config_dict, f, indent=4)
