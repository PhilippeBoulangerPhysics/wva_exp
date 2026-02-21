import os
import xarray as xr
import matplotlib.pyplot as plt
exp_name = "realistic_continents_T85_2moments_rrtm_qflux"
month = 12
perturbation_magnitude = 0.2
ds_atm = xr.open_dataset(f"/home/philbou/projects/def-rfajber/philbou/wva_exp/restarts/{exp_name}/{month:04d}/restart_files/original/atmosphere.res.nc")
ds_atm_perturbed = xr.open_dataset(f"/home/philbou/projects/def-rfajber/philbou/wva_exp/restarts/{exp_name}/{month:04d}/restart_files/perturbed/{perturbation_magnitude}/atmosphere.res.nc")

fig,axs = plt.subplots(1,3,figsize=(18,6))
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

cb = axs[2].contourf(ds_atm["xaxis_2"], ds_atm["yaxis_2"], ds_atm_perturbed["tg"][0,-1,:,:] - ds_atm["tg"][0,-1,:,:], cmap="viridis")
plt.colorbar(cb, ax=axs[2], orientation="vertical", label="Temperature (K)")
axs[2].set_title("Temperature Perturbation")
axs[2].set_xlabel("Longitude")
axs[2].set_ylabel("Latitude")
fig.suptitle(f"Temperature Perturbation in Restart Dataset at surface level (magnitude={perturbation_magnitude})", fontsize=16)
plt.tight_layout()
fig.savefig(f"/home/philbou/projects/def-rfajber/philbou/wva_exp/restarts/temperature_perturbation_{perturbation_magnitude}.png",dpi = 300)