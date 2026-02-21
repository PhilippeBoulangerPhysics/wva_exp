#!/bin/bash
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=8 # Make sure ncores in the config file matches this (ncores=32 for 4 nodes * 8 tasks per node)
#SBATCH --time=5-00:00:00
#SBATCH --mem-per-cpu=3G
#SBATCH --job-name=realistic_continents_rrtm_qflux
#SBATCH --output=/scratch/philbou/outerr/realistic_continents/%x-%j.out
#SBATCH --error=/scratch/philbou/outerr/realistic_continents/%x-%j.err
#SBATCH --account=def-rfajber

# directory of the Isca source code 
export GFDL_BASE=/home/philbou/Isca 
# &quot;environment&quot; configuration for emps-gv4
export GFDL_ENV=narval.ifort
# temporary working directory used in running the model
export GFDL_WORK=/scratch/philbou/isca_work
# directory for storing model output
export GFDL_DATA=/scratch/philbou/isca_data

source /home/philbou/.bashrc 
conda activate isca_env

cd /home/philbou/projects/def-rfajber/philbou/wva_exp

python run_experiment.py realistic_continents rrtm $1 $2
