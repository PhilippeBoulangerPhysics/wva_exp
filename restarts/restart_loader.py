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
        self.output_dir_perturbed = f"{PROJECT_DIR}restarts/{self.experiment_name}/{self.month:04d}/restart_files/perturbed/{self.perturbation_magnitude}/"
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
    
    def create_tar_gz(self, output_file_name, files_dir, files_to_compress):
        """Create a tar.gz file from a list of files or directories."""
        output_file = os.path.join(self.output_dir, output_file_name)
        with tarfile.open(output_file, "w:gz") as tar:
            for file_name in files_to_compress:
                file_path = os.path.join(files_dir, file_name)
                tar.add(file_path, arcname=os.path.basename(file_path))
                
    def open_dataset(self,dataset_name):
        """Open the restart dataset for the given experiment and month."""
        dataset_path = os.path.join(self.output_dir_files, dataset_name)
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"{dataset_name} not found in {self.output_dir_files}")
        return xr.open_mfdataset(dataset_path)
    
    def perturb_temperature(self):
        """Perturb the temperature variable in the specified dataset."""
        atmosphere_ds = self.open_dataset("atmosphere.res.nc")
        if "tg" not in atmosphere_ds:
            raise KeyError("Temperature variable not found in atmosphere.res.nc")
        
        perturbation_value = self.get_perturbation_value(atmosphere_ds)
        atmosphere_ds["tg"] += perturbation_value
        perturbed_file_path = os.path.join(self.output_dir_perturbed, f"atmosphere.res.nc")
        atmosphere_ds.to_netcdf(perturbed_file_path)
        return perturbed_file_path
    
    def get_random_field(self,shape_like_array):
        data = np.random.normal(loc=0, scale=1, size=shape_like_array.shape)
        da = data * xr.ones_like(shape_like_array)   
        return da  
    
    def get_perturbation_value(self, dataset):
        """Calculate the perturbation value based on the dataset and magnitude."""
        shape_like_array = xr.ones_like(dataset["tg"])
        return self.perturbation_magnitude * self.get_random_field(shape_like_array)
    
    def save_perturbed_restart(self, perturbed_file_path):
        """Save the perturbed restart dataset."""
        for file_name in OUTPUT_FILENAME_LIST[1:]:
            file_path = os.path.join(self.output_dir_files, file_name)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"{file_name} not found in {self.output_dir_files}")
            os.system(f"cp {file_path} {self.output_dir_perturbed}")
            
        output_file_name = os.path.join(self.output_dir,perturbed_file_path)
        self.create_tar_gz(output_file_name, self.output_dir_perturbed, OUTPUT_FILENAME_LIST)
    
if __name__ == "__main__":
    experiment_name = str(sys.argv[1])
    month = int(sys.argv[2])
    perturbation_magnitude = float(sys.argv[3])
    restart_dataset = RestartDataset(experiment_name, month, perturbation_magnitude)
    restart_dataset.open_restart_dataset()
    restart_dataset.perturb_temperature()
    restart_dataset.save_perturbed_restart(f"res{month:04d}_{perturbation_magnitude}.tar.gz")