import os

import numpy as np
from field_table_write import write_ft
from run_exp import WaterVaporAgeExperiment
import f90nml
from isca import IscaCodeBase, DiagTable, Experiment, Namelist, GFDL_BASE
import datetime
import sys 


horizontal_resolution = "T85"
NCORES = 32
delta_sst = int(sys.argv[1])
n_start_month = int(sys.argv[2])

if delta_sst < 0:
        delta_sst_name = f"m{abs(delta_sst)}"
else:
        delta_sst_name = str(delta_sst)



exp_name = f"R{horizontal_resolution}_sst_{delta_sst_name}" #"real_T85_sst_spinup"

dt = 360
original_dt = 360
min_dt = 30

n_end_month = 720#361
if n_start_month != 1:  
    restart = True
else: restart= False
current_n = n_start_month + 1
n_end = 361


n_moments = 2

config_dict = {
    'n_moments': n_moments,
    'horizontal_resolution': horizontal_resolution,
    'run_type': 'run',
    'config_argument': '',
    'vertical_resolution': 45,
    'ncores': NCORES,
    'dt_atm': 720,
    'sponge': 150,
    'trayfric': -0.5,
    'delta_sst': delta_sst,
    'compile': False,
    "dt_atm": 720
}
                
exp = WaterVaporAgeExperiment(config_dict=config_dict)

exp.setup()

"""exp.update_namelist({
 "vert_turb_driver_nml":{
   "do_mellor_yamada"       : False, 
   "do_diffusivity"         : True,   
   "do_simple"              : True, 
   "constant_gust"          : 0.0, 
   "use_tau"                : False}})"""

exp.run_experiment_variable_timestep(n_start_month, n_end_month, original_dt, min_dt)