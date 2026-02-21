import os
import f90nml
from isca import IscaCodeBase, DiagTable, Experiment, GFDL_BASE
import datetime
import sys 

def get_field(n):
    base = {
            "atmos_mod": "sphum_age",
            "longname": "sphum times",
            "units": "sec (kg/kg)",
            "numerical_representation": "grid",
            "hole_filling": "off",
            "advect_vert": "finite_volume_parabolic",
            "robert_filter": "on",
            "profile_type": ["fixed", "surface_value=0.0"]
        }
    base["atmos_mod"] += f"_{n+1}"
    base["longname"] += f" {n+1}-th moment "
    return base

def write_ft(name,n_moments):
    base_dir = os.path.dirname(os.path.realpath(__file__))
    # a CodeBase can be a directory on the computer,
    # useful for iterative development
    add_dir = "/src/extra/model/isca/"
    field_table_dir = GFDL_BASE + add_dir

    sphum ={
            "atmos_mod": "sphum",
            "longname": "specific humidity",
            "units": "kg/kg",
            "numerical_representation": "grid",
            "hole_filling": "off",
            "advect_vert": "finite_volume_parabolic",
            "robert_filter": "on",
            "profile_type": ["fixed", "surface_value=0.0"]
            }
        
    
    # Define the file name without an extension
    output_file = field_table_dir + name

    # Open the file in write mode
    with open(output_file, 'w') as file:
        # Write sphum tracer
        file.write(f'"TRACER",')
        for key, value in sphum.items():
            if type(value) == str:
                file.write(f'"{key}", "{value}"\n')
            elif type(value) == list:
                file.write(f'"{key}", "{value[0]}", "{value[1]}"\n')
        file.write('/ \n')

         
        for ind in range(n_moments):
            field = get_field(ind)
            file.write(f'"TRACER",')
            for key, value in field.items():
                if type(value) == str:
                    file.write(f'"{key}", "{value}"\n')
                elif type(value) == list:
                    file.write(f'"{key}", "{value[0]}", "{value[1]}"\n')
            file.write('/ \n')

class WaterVaporAgeExperiment(Experiment):
    
    def __init__(self, config_dict):
        self.compile = config_dict.get('compile', False)
        self.horizontal_resolution = config_dict.get('horizontal_resolution')   
        self.vertical_resolution = config_dict.get('vertical_resolution', 45)
        self.run_type = config_dict.get('run_type')
        self.n_moments = config_dict.get('n_moments', 2)
        self.rad_type = config_dict.get('rad_type', 'rrtm')
        self.ncores = config_dict.get('ncores', 16)
        self.fixed_sst = config_dict.get('fixed_sst', False)
        self.delta_sst = config_dict.get('delta_sst', None)
        self.original_dt = config_dict.get('dt_atm', 720)
        self.base_dir = os.path.dirname(os.path.realpath(__file__))
        self.resolution = self.horizontal_resolution, self.vertical_resolution
        self.exp_name_suffix = config_dict.get('exp_name_suffix', "")
        self.start_dir = "/home/philbou/projects/def-rfajber/philbou/wva_exp/"
        self.input_dir = f"{self.start_dir}input/"
        
        self.cb = IscaCodeBase.from_directory(GFDL_BASE)
        if self.compile:
            self.cb.compile(debug = False)
        
        self.exp_name = self.create_exp_name()
        super().__init__(self.exp_name, codebase=self.cb)
        
        
    def create_exp_name(self):
        if self.fixed_sst:
            delta_sst_name = f"sst_m{abs(self.delta_sst)}_" if self.delta_sst < 0 else f"sst_{self.delta_sst}_"
        else:
            delta_sst_name = ""
        return f"{self.run_type}_{self.horizontal_resolution}_{delta_sst_name}{self.n_moments}moments_{self.rad_type}{self.exp_name_suffix}"

    def setup(self):
        """
        Set up the experiment by writing the field table, setting input files, diag table, namelist, and resolution.
        """
        self.log_description()
    
        write_ft("field_table", self.n_moments) 
        print(f"{datetime.datetime.now()} :field table written for {self.n_moments} moments",file=sys.stdout, flush=True)
    
        self.set_input_files()
        print(f"{datetime.datetime.now()} :input files set: {self.inputfiles}",file=sys.stdout, flush=True)
        
        self.diag_table = self.get_diag_table()
        print(f"{datetime.datetime.now()} :diag table set",file=sys.stdout, flush=True)
        
        self.namelist_name = self.set_namelist_from_file()
        print(f"{datetime.datetime.now()} :namelist set from file {self.namelist_name}",file=sys.stdout, flush=True)
        self.clear_rundir()
        
        self.set_resolution(*self.resolution)
        
        self.set_land()
        
        self.set_fixed_sst()
        
        print(self.namelist, file=sys.stdout, flush=True)

    def set_land(self):
        land_file = f'era_land_{self.horizontal_resolution.lower()}.nc'
        era_land_files = {
            "idealized_moist_phys_nml": {
                "land_file_name": f"INPUT/{land_file}"
            },
            "spectral_init_cond_nml": {
                "topog_file_name": f"{land_file}"
            }
        }
        if self.run_type == "realistic_continents":
            for nml, files in era_land_files.items():
                self.update_namelist({nml: files})
            self.inputfiles.append(os.path.join(self.input_dir,f'{land_file}'))
    
    def log_description(self):
            print(f"Experiment Name: {self.exp_name}", file=sys.stdout, flush=True)
            print(f"# of cpus: {self.ncores}", file=sys.stdout, flush=True)
            print(f"Horizontal Resolution: {self.horizontal_resolution}", file=sys.stdout, flush=True)
            print(f"Vertical Resolution: {self.vertical_resolution}", file=sys.stdout, flush=True)
            print(f"Timestep: {self.original_dt}", file=sys.stdout, flush=True)
            print(f"Run Type: {self.run_type}", file=sys.stdout, flush=True)
            print(f"Number of Moments: {self.n_moments}", file=sys.stdout, flush=True)
            print(f"Radiation Type: {self.rad_type}", file=sys.stdout, flush=True)
            print(f"Fixed SST: {self.fixed_sst}", file=sys.stdout, flush=True)
            if self.fixed_sst:
                print(f"Delta SST: {self.delta_sst}", file=sys.stdout, flush=True)
        
    def set_fixed_sst(self):
        sst_settings = {
                "mixed_layer_nml": {
                    "do_read_sst": True,
                    "do_sc_sst": True,
                    "sst_file": f"sst_clim_amip({self.delta_sst})",
                    "specify_sst_over_ocean_only": True
                }
            }
        if self.fixed_sst:
            for nml, settings in sst_settings.items():
                self.update_namelist({nml: settings})
            sst_file_name = f'sst_clim_amip({self.delta_sst}).nc'
            self.inputfiles.append(os.path.join(self.input_dir,f'{sst_file_name}'))
        
    def set_input_files(self):
        """ Get the input files for the experiment based on the run type and resolution. """
        
        input_files = [os.path.join(self.input_dir,'rrtm_input_files/ozone_1990.nc'), os.path.join(self.input_dir,'siconc_clim_amip.nc')]
        self.inputfiles = input_files

    def set_namelist_from_file(self):
        """ Set the namelist for the experiment based on the run type and resolution. """
        namelist_path = os.path.join(self.start_dir, f'namelist/namelist_{self.run_type}_{self.rad_type}.nml')
        self.namelist = f90nml.read(namelist_path)
        return namelist_path

    def get_diag_table(self) -> DiagTable:
        """ Create the diagnostic table for the experiment based on the number of moments and the fields to be diagnosed. """
        diag = DiagTable()
        diag.add_file('atmos_monthly', 6, 'hours', time_units='days')
        diag.add_field('dynamics', 'ps', time_avg=True)
        diag.add_field('dynamics', 'bk')
        diag.add_field('dynamics', 'pk')
        diag.add_field('atmosphere', 'precipitation', time_avg=True)
        diag.add_field('mixed_layer', 't_surf', time_avg=True)
        diag.add_field('mixed_layer', 'flux_lhe', time_avg=True)
        diag.add_field('mixed_layer', 'flux_t', time_avg=True)
        diag.add_field('mixed_layer', 'flux_oceanq', time_avg=True)
        diag.add_field('mixed_layer', 'corr_flux', time_avg=True)
        diag.add_field('mixed_layer', 'albedo', time_avg=True)

        diag.add_field('dynamics', 'sphum', time_avg=True)
        diag.add_field('dynamics', 'ucomp', time_avg=True)
        diag.add_field('dynamics', 'vcomp', time_avg=True)
        diag.add_field('dynamics', 'omega', time_avg=True)
        diag.add_field('dynamics', 'wspd', time_avg=True)
        diag.add_field('dynamics', 'height', time_avg=True)
        diag.add_field('dynamics', 'temp', time_avg=True)
        diag.add_field('dynamics', 'vor', time_avg=True)
        diag.add_field('dynamics', 'div', time_avg=True)
        
        for ind in range(self.n_moments):
            name = f"sphum_age_{ind+1}"
            diag.add_field('dynamics', name, time_avg=True)

        diag.add_field('atmosphere', 'cape', time_avg=True)
        diag.add_field('atmosphere', 'dt_qg_convection', time_avg=True)
        diag.add_field('atmosphere', 'dt_qg_condensation', time_avg=True)
        diag.add_field('atmosphere', 'dt_sink', time_avg=True)
        diag.add_field('atmosphere', 'dt_tracer', time_avg=True)
        diag.add_field('atmosphere', 'dt_q', time_avg=True)
        diag.add_field('atmosphere', 'dt_tracer_diff', time_avg=True)
        diag.add_field('atmosphere', 'dt_qg_diffusion', time_avg=True)
        diag.add_field('atmosphere', 'rh', time_avg=True)
        diag.add_field('atmosphere', 'condensation_rain', time_avg=True)
        diag.add_field('atmosphere', 'convection_rain', time_avg=True)
        
        if self.rad_type == "rrtm":
            diag.add_field('rrtm_radiation', 'olr', time_avg=True)
            diag.add_field('rrtm_radiation', 'toa_sw', time_avg=True)
            diag.add_field('rrtm_radiation', 'tdt_rad', time_avg=True)
            diag.add_field('rrtm_radiation', 'tdt_sw', time_avg=True)
            diag.add_field('rrtm_radiation', 'tdt_lw', time_avg=True)
            diag.add_field('rrtm_radiation', 'flux_sw', time_avg=True)
            diag.add_field('rrtm_radiation', 'flux_lw', time_avg=True)

        return diag
    
    def setup_albedo_region(self, albedo_choice, albedo_cntr_lat, albedo_wdth_lat, albedo_cntr_lon, albedo_wdth_lon, higher_albedo, albedo_value):
        """ Update the namelist to set up a region of higher albedo in some region. """
        self.update_namelist({
            'mixed_layer_nml': {  
                'albedo_choice' : albedo_choice, 
                'albedo_cntr_lat' : albedo_cntr_lat,
                'albedo_wdth_lat' : albedo_wdth_lat,
                'albedo_cntr_lon' : albedo_cntr_lon,
                'albedo_wdth_lon' : albedo_wdth_lon,
                'higher_albedo' : higher_albedo,
                'albedo_value' : albedo_value}})
    
    def run_experiment_variable_timestep(self, n_start_month, n_end_month,spinup_exp_name = None,other_restart_file=None):
        """ Runs the experiment from n_start_month to n_end_month, starting with original_dt and halving the timestep if the model crashes, 
        until min_dt is reached. If spinup_exp_name is provided, it will use the restart files from that experiment for the first month. """
        
        MIN_DT = 30
        
        if spinup_exp_name is None:
            spinup_exp_name = self.exp_name
            
        if n_start_month != 1:  
            restart = True
        else: restart= False
        
        self.elapsed_time_log = []
        
        dt = self.original_dt
        if other_restart_file is None:
            res_file = f"/home/philbou/scratch/isca_data/{spinup_exp_name}/restarts/res{n_start_month-1:04d}.tar.gz"
        else:
            res_file = other_restart_file
            restart = True
            
        elapsed_time = self.run(n_start_month, num_cores=self.ncores, overwrite_data=True,use_restart=restart, restart_file=res_file)
        self.log_month_result(n_start_month,dt,elapsed_time)
        self.write_description_file()
        current_n = n_start_month + 1
        while current_n < n_end_month:
            try:
                for i in range(current_n , n_end_month):
                    if current_n ==0: restart = False
                    else: restart = True
                    elapsed_time = self.run(i, num_cores=self.ncores, overwrite_data=True )
                    self.log_month_result(i, dt, elapsed_time)
                    current_n+=1
            except:
                if dt/2 < MIN_DT:
                    print(f"{datetime.datetime.now()} : dt too small ({dt/2}), cannot proceed with month {i}", file=sys.stdout, flush=True)
                    raise RuntimeError(f"dt too small ({dt/2}), cannot proceed with month {i}")   
                else:   
                    self.log_dt_change(dt, dt/2)
                    dt = dt/2
                    self.update_timestep_nml(dt)
                    # Run for 2 months at the smaller dt
                    success = False
                    # if first month did not work
                    if current_n == n_start_month: 
                        print(f"{datetime.datetime.now()} : Crashed at first month, PICK A SMALLER DT", file=sys.stdout, flush=True)
                        raise RuntimeError(f"Crashed at first month, PICK A SMALLER DT")  # Let it crash, you fool
                    # any other month
                    else: 
                        success = False
                        while success == False:
                            try:
                                # run for 2 months
                                for j in range(current_n,current_n + 2):
                                    elapsed_time = self.run(j, num_cores=self.ncores, overwrite_data=True)
                                    self.log_month_result(j, dt, elapsed_time)
                                    current_n+=1
                                success = True
                            except:
                                if dt/2 < MIN_DT:
                                    print(f"{datetime.datetime.now()} : dt too small ({dt/2}), cannot continue month {i}", file=sys.stdout, flush=True)
                                    raise RuntimeError(f"dt too small ({dt/2}), cannot continue month {i}")  
                                self.log_dt_change(dt, dt/2)
                                dt = dt/2
                                self.update_timestep_nml(dt)
                        self.log_dt_change(dt, self.original_dt)
                        dt = self.original_dt
                        self.update_timestep_nml(dt)
                        
        average_elapsed_time = sum(self.elapsed_time_log) / len(self.elapsed_time_log) if self.elapsed_time_log else 0
        print(f"{datetime.datetime.now()} : Experiment completed. Average elapsed time per month: {average_elapsed_time:.2f} hours", file=sys.stdout, flush=True)
        
    def run(self, i, restart_file=None, use_restart=True, multi_node=False, num_cores=8, overwrite_data=False, 
            save_run=False, run_idb=False, nice_score=0, mpirun_opts=''):
        t0 = datetime.datetime.now()
        super().run(i, restart_file=restart_file, use_restart=use_restart, multi_node=multi_node, num_cores=num_cores, 
                    overwrite_data=overwrite_data, save_run=save_run, run_idb=run_idb, nice_score=nice_score, mpirun_opts=mpirun_opts)
        t1 = datetime.datetime.now()
        elapsed_time = (t1 - t0).total_seconds() / 60.0**2  # hours
        self.elapsed_time_log.append(elapsed_time)
        return elapsed_time
    
    def log_month_result(self, month, dt, elapsed_time):
        print(f"{datetime.datetime.now()} : month {month} completed at dt = {dt}, in {elapsed_time:.2f} hours", file=sys.stdout, flush=True)
        
    def log_dt_change(self, dt_init, dt_final):
        print(f"{datetime.datetime.now()} : dt updated from {dt_init} to {dt_final}",file=sys.stdout, flush=True)
        
    def update_timestep_nml(self, dt):
        self.update_namelist({'main_nml' : {'dt_atmos' : dt}})
        print(f"{datetime.datetime.now()} : namelist updated to dt = {dt}",file=sys.stdout, flush=True) 
        
    def write_description_file(self):
        description_path = os.path.join(self.datadir, "experiment_description.txt")
        with open(description_path, "w") as f:
            f.write(f"Experiment Name: {self.exp_name}\n")
            f.write(f"Horizontal Resolution: {self.horizontal_resolution}\n")
            f.write(f"Vertical Resolution: {self.vertical_resolution}\n")
            f.write(f"Run Type: {self.run_type}\n")
            f.write(f"Number of Moments: {self.n_moments}\n") 
            f.write(f"Radiation Type: {self.rad_type}\n")
            f.write(f"Fixed SST: {self.fixed_sst}\n")
            if self.fixed_sst:
                f.write(f"Delta SST: {self.delta_sst}\n") 
