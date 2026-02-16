#!/bin/bash
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=8 # Make sure ncores in the config file matches this (ncores=16 for 2 nodes * 8 tasks per node)
#SBATCH --time=0-01:00:00
#SBATCH --mem-per-cpu=2048M
#SBATCH --job-name=aquaplanet_grey
#SBATCH --output=/scratch/philbou/outerr/aquaplanet/%x-%j.out
#SBATCH --error=/scratch/philbou/outerr/aquaplanet/%x-%j.err
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

cd $GFDL_BASE/exp/test_cases/wv_age

python run_experiment.py aquaplanet grey $1 $2
