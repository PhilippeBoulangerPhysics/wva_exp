import xarray as xr
import os
import sys
import tarfile
import numpy as np

SCRATCH_DATA_PATH = "/home/philbou/scratch/isca_data/"
PROJECT_DIR = "/home/philbou/projects/def-rfajber/philbou/wva_exp/"
OUTPUT_FILENAME_LIST = ["atmosphere.res.nc","atmos_model.res",
                                           "mixed_layer.res.nc","spectral_dynamics.res.nc"]
        
class RestartDataset:
    def __init__(self, experiment_name : str, month : int, perturbation_magnitude : float):
        """ Create a RestartDataset instance for a specific experiment and month."""
        self.experiment_name = experiment_name
        self.month = month
        self.perturbation_magnitude = perturbation_magnitude
        self.create_saved_data_dir()
        self.move_restart_files_to_projects()
        
    def create_saved_data_dir(self):
        self.output_dir = f"{PROJECT_DIR}restarts/{self.experiment_name}/{self.month:04d}/"
        self.output_dir_perturbed = f"{self.output_dir}restart_files/perturbed/{self.perturbation_magnitude}/"
        self.output_dir_files = f"{self.output_dir}restart_files/original/"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.output_dir_perturbed, exist_ok=True)
        os.makedirs(self.output_dir_files, exist_ok=True)
        
    def move_restart_files_to_projects(self):
        """ Move restart files for the given experiment and month."""
        input_file_path = f"{SCRATCH_DATA_PATH}{self.experiment_name}/restarts/res{self.month:04d}.tar.gz"
        output_file_path = f"{self.output_dir}/res{self.month:04d}.tar.gz"
        os.system(f"cp {input_file_path} {output_file_path}")
        
    def open_restart_dataset(self):
        """ Open the restart dataset for the given experiment and month."""
        self.restart_file_path = f"{self.output_dir}/res{self.month:04d}.tar.gz"
        return os.system(f"tar -xzf {self.restart_file_path} -C {self.output_dir_files}")
    
    def create_tar_gz(self, output_file_name, files_dir, files_to_compress, arcname_map=None):
        """Create a tar.gz file from a list of files or directories."""
        output_file = os.path.join(self.output_dir, output_file_name)
        with tarfile.open(output_file, "w:gz") as tar:
            for file_name in files_to_compress:
                file_path = os.path.join(files_dir, file_name)
                if arcname_map and file_name in arcname_map:
                    arcname = arcname_map[file_name]
                else:
                    arcname = os.path.basename(file_path)
                tar.add(file_path, arcname=arcname)
                
    def open_dataset(self,dataset_name):
        """Open the restart dataset for the given experiment and month."""
        dataset_path = os.path.join(self.output_dir_files, dataset_name)
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"{dataset_name} not found in {self.output_dir_files}")
        return xr.open_mfdataset(dataset_path)
    
    def perturb_temperature(self,n):
        """Perturb the temperature variable in the specified dataset."""
        atmosphere_ds = self.open_dataset("atmosphere.res.nc")
        if "tg" not in atmosphere_ds:
            raise KeyError("Temperature variable not found in atmosphere.res.nc")
        for i in range(n):
            perturbation_value = self.get_perturbation_value(atmosphere_ds)
            atmosphere_ds["tg"] += perturbation_value
            perturbed_file_path = os.path.join(self.output_dir_perturbed, f"atmosphere_{i}.res.nc")
            # Preserve unlimited Time dimension and set _FillValue to None to prevent writing it
            encoding = {}
            for var in atmosphere_ds.data_vars:
                encoding[var] = atmosphere_ds[var].encoding.copy()
                encoding[var]['_FillValue'] = None
            for var in atmosphere_ds.coords:
                encoding[var] = atmosphere_ds[var].encoding.copy()
                encoding[var]['_FillValue'] = None
            atmosphere_ds.to_netcdf(perturbed_file_path, unlimited_dims=['Time'], encoding=encoding)
        return perturbed_file_path
    
    def get_random_field(self,shape_like_array):
        data = np.random.normal(loc=0, scale=1, size=shape_like_array.shape)
        da = data * xr.ones_like(shape_like_array)   
        return da  
    
    def get_perturbation_value(self, dataset):
        """Calculate the perturbation value based on the dataset and magnitude."""
        shape_like_array = xr.ones_like(dataset["tg"])
        return self.perturbation_magnitude * self.get_random_field(shape_like_array)
    
    def save_perturbed_restart(self,n,perturbed_file_path):
        """Save the perturbed restart dataset."""
        for file_name in OUTPUT_FILENAME_LIST[1:]:
            file_path = os.path.join(self.output_dir_files, file_name)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"{file_name} not found in {self.output_dir_files}")
            os.system(f"cp {file_path} {self.output_dir_perturbed}")
            
        for i in range(n):
            atmosphere_perturbed_file = f"atmosphere_{i}.res.nc"
            OUTPUT_FILENAME_LIST[0] = atmosphere_perturbed_file  
            output_file_name = os.path.join(self.output_dir,perturbed_file_path.replace(".tar.gz", f"_{i}.tar.gz"))
            # Map the perturbed atmosphere file to be stored as atmosphere.res.nc in the tar archive
            arcname_map = {atmosphere_perturbed_file: "atmosphere.res.nc"}
            self.create_tar_gz(output_file_name, self.output_dir_perturbed, OUTPUT_FILENAME_LIST, arcname_map=arcname_map)
    
if __name__ == "__main__":
    experiment_name = str(sys.argv[1])
    month = int(sys.argv[2])
    perturbation_magnitude = float(sys.argv[3])
    n = int(sys.argv[4])
    restart_dataset = RestartDataset(experiment_name, month, perturbation_magnitude)
    restart_dataset.open_restart_dataset()
    restart_dataset.perturb_temperature(n)
    restart_dataset.save_perturbed_restart(n,f"res{month:04d}_{perturbation_magnitude}.tar.gz")