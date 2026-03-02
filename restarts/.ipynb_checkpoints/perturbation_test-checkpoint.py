import os
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np

exp_name = "RT42_sst_0_bucket"
month = 360
perturbation_magnitude = 0.1
ds_atm = xr.open_dataset(f"/home/philbou/projects/def-rfajber/philbou/wva_exp/restarts/{exp_name}/{month:04d}/restart_files/original/atmosphere.res.nc")
ds_atm_perturbed = xr.open_dataset(f"/home/philbou/projects/def-rfajber/philbou/wva_exp/restarts/{exp_name}/{month:04d}/restart_files/perturbed/{perturbation_magnitude}/atmosphere_0.res.nc")
ds_atm_perturbed_2 = xr.open_dataset(f"/home/philbou/projects/def-rfajber/philbou/wva_exp/restarts/{exp_name}/{month:04d}/restart_files/perturbed/{perturbation_magnitude}/atmosphere_1.res.nc")


fig,axs = plt.subplots(1,4,figsize=(24,6))
cb = axs[0].contourf(ds_atm["xaxis_2"], ds_atm["yaxis_2"], ds_atm["tg"][0,-1,:,:], cmap="viridis")
plt.colorbar(cb, ax=axs[0], orientation="vertical", label="Temperature (K)")
axs[0].set_title("Original Temperature")
axs[0].set_xlabel("Longitude")
axs[0].set_ylabel("Latitude")

cb = axs[1].contourf(ds_atm_perturbed["xaxis_2"], ds_atm_perturbed["yaxis_2"], ds_atm_perturbed["tg"][0,-1,:,:], cmap="viridis")
plt.colorbar(cb, ax=axs[1], orientation="vertical", label="Temperature (K)")
axs[1].set_title("Perturbed Temperature")
axs[1].set_xlabel("Longitude")
axs[1].set_ylabel("Latitude")

cb = axs[2].contourf(ds_atm["xaxis_2"], ds_atm["yaxis_2"], ds_atm_perturbed_2["tg"][0,-1,:,:] - ds_atm["tg"][0,-1,:,:], cmap="viridis")
plt.colorbar(cb, ax=axs[2], orientation="vertical", label="Temperature (K)")
axs[2].set_title("Temperature Perturbation")
axs[2].set_xlabel("Longitude")
axs[2].set_ylabel("Latitude")

cb = axs[3].contourf(ds_atm["xaxis_2"], ds_atm["yaxis_2"], ds_atm_perturbed_2["tg"][0,-1,:,:] - ds_atm_perturbed["tg"][0,-1,:,:], cmap="viridis")
plt.colorbar(cb, ax=axs[3], orientation="vertical", label="Temperature (K)")
axs[3].set_title("Temperature Perturbation 1 vs 2")
axs[3].set_xlabel("Longitude")
axs[3].set_ylabel("Latitude")
fig.suptitle(f"Temperature Perturbation in Restart Dataset at surface level (magnitude={perturbation_magnitude})", fontsize=16)
plt.tight_layout()
fig.savefig(f"/home/philbou/projects/def-rfajber/philbou/wva_exp/restarts/temperature_perturbation_{perturbation_magnitude}.png",dpi = 300)


ds_atm.close()
ds_atm_perturbed.close()
ds_atm_perturbed_2.close()

ds_atm_0 = xr.open_dataset("/home/philbou/scratch/isca_data/realistic_continents_T42_sst_0_2moments_rrtm_RT42_0.1_0/run0372/atmos_monthly.nc")
ds_atm_1 = xr.open_dataset("/home/philbou/scratch/isca_data/realistic_continents_T42_sst_0_2moments_rrtm_RT42_0.1_1/run0372/atmos_monthly.nc")

snapshot_0 = ds_atm_0["precipitation"].isel(time=0)
snapshot_1 = ds_atm_1["precipitation"].isel(time=0)

fig,axs = plt.subplots(1,3,figsize=(18,6))
lev = np.linspace(0,0.001,21)
cb = axs[0].contourf(ds_atm_0["lon"], ds_atm_0["lat"], snapshot_0, cmap="viridis",levels = lev)
plt.colorbar(cb, ax=axs[0], orientation="vertical", label=f"Precipitation ({snapshot_0.units})")
axs[0].set_title("Perturbation 0: Precipitation")
axs[0].set_xlabel("Longitude")
axs[0].set_ylabel("Latitude")   

cb = axs[1].contourf(ds_atm_1["lon"], ds_atm_1["lat"], snapshot_1, cmap="viridis",levels = lev)
plt.colorbar(cb, ax=axs[1], orientation="vertical", label=f"Precipitation ({snapshot_1.units})")
axs[1].set_title("Perturbation 1: Precipitation")
axs[1].set_xlabel("Longitude")
axs[1].set_ylabel("Latitude")   

cb = axs[2].contourf(ds_atm_0["lon"], ds_atm_0["lat"], snapshot_1 - snapshot_0, cmap="coolwarm",levels = np.linspace(-0.0005,0.0005,21),extend = "both")
plt.colorbar(cb, ax=axs[2], orientation="vertical", label=f"Precipitation ({snapshot_1.units})")
axs[2].set_title("Perturbation 1 vs 0: Precipitation Difference")
axs[2].set_xlabel("Longitude")
axs[2].set_ylabel("Latitude")
fig.suptitle(f"Precipitation Perturbation in Restart Dataset at surface level (magnitude={perturbation_magnitude})", fontsize=16)
plt.tight_layout()
fig.savefig(f"/home/philbou/projects/def-rfajber/philbou/wva_exp/restarts/precipitation_perturbation_{perturbation_magnitude}.png",dpi = 300)

ds_atm_0.close()
ds_atm_1.close()

ds_atm_56 = xr.open_dataset("/home/philbou/scratch/isca_data/realistic_continents_T85_2moments_rrtm_qflux_0.1_5/run0056/atmos_monthly.nc")

snapshot_56 = ds_atm_56.isel(time=0)
monthly_mean_56 = ds_atm_56.mean(dim="time")

fig,axs = plt.subplots(1,2,figsize=(12,6))
lev = np.linspace(0,0.001,21)
cb = axs[0].contourf(ds_atm_0["lon"], ds_atm_0["lat"], snapshot_56["precipitation"], cmap="viridis",levels = lev)
plt.colorbar(cb, ax=axs[0], orientation="vertical", label=f"Precipitation ({snapshot_56['precipitation'].units})")
axs[0].set_title("snapshot of month 56 (1year after pertuebed and 5->20 ml): Precipitation")
axs[0].set_xlabel("Longitude")
axs[0].set_ylabel("Latitude")   

cb = axs[1].contourf(ds_atm_56["lon"], ds_atm_56["lat"], monthly_mean_56["precipitation"], cmap="viridis",levels = lev)
plt.colorbar(cb, ax=axs[1], orientation="vertical", label=f"Precipitation ({snapshot_56['precipitation'].units})")
axs[1].set_title("monthly mean of month 56 (1year after pertuebed and 5->20 ml): Precipitation")
axs[1].set_xlabel("Longitude")
axs[1].set_ylabel("Latitude")   

fig.suptitle(f"Precipitation Perturbation in Restart Dataset at surface level (magnitude={perturbation_magnitude})", fontsize=16)
plt.tight_layout()
fig.savefig(f"/home/philbou/projects/def-rfajber/philbou/wva_exp/restarts/precipitation_post_perturbation_{perturbation_magnitude}.png",dpi = 300)