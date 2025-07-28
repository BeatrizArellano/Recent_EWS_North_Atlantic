"""
This script generates netcdf files storing the AR(1) trends for SSTs from HadISST and EN4 datasets
"""

import numpy as np
import pandas as pd
import xarray as xr
import sys
sys.path.append('../../lib/')
from regimeshifts import ews


def get_ews_array(ds,name_var,bW=35,wL=50):
    """
    Estimates the AR(1) and variance trends measured with
    the Kendall Tau coefficient over the spatial domain
    """
    def get_ews(ts,bW=35,wL=50):
        """
        Estimates AR(1) and variance trends for a particular time-series
        corresponding to a grid-point over the spatial domain.
        """
        if np.isnan(ts[0]): # If the point is not part of the domain
            return np.array([np.nan,np.nan])
        else:
            ar1_kv = ews.Ews(ts).ar1(detrend=True, bW=bW, wL=wL).kendall
            var_kv = ews.Ews(ts).var(detrend=True, bW=bW, wL=wL).kendall
            return np.array([ar1_kv, var_kv])
    
    dims = list(ds.dims)
    dims.remove('time')
    ### In order to use apply_ufunc the dimensions need to be stacked and grouped
    ds_stacked = ds.stack({'gridPoint':dims}).groupby('gridPoint')
    ews_array = xr.apply_ufunc(get_ews, ds_stacked, input_core_dims=[['time']],output_core_dims=[["ews"]],
                              output_sizes={"ews": 2}, kwargs={'bW':bW,'wL':wL})
    

    ews_array = ews_array.unstack('gridPoint')
    if not isinstance(ews_array,xr.Dataset):
        ews_array = ews_array.to_dataset()
    ews_array['ar1'] = ews_array[name_var][0]
    ews_array['variance'] = ews_array[name_var][1]
    ews_array = ews_array.drop(name_var)    
    return ews_array



store_path = 'output/ews_maps/'

bW = 35
wL = 50
years = [1920,2023]

print('Getting annually averaged surface temperatures on the EN4 dataset (first 100m)') 
en4_file = '../../../datasets/EN4/EN.4.2.2.analyses.g10/*.nc'
en4 = xr.open_mfdataset(en4_file,combine='by_coords')
en4_full = en4.sel(depth=slice(*[0,100]))
en4_full = en4_full.assign_coords(lon=(((en4.lon + 180) % 360) - 180))
en4_full = en4_full.sortby(en4_full.lon).sel(time=(en4_full.time.dt.year>=years[0])&(en4_full.time.dt.year<=years[1]))
en4_full = en4_full.where(en4_full.temperature>=-2)
en4_avg_depth_full = en4_full.temperature.mean(dim='depth')
en4_ann_full = en4_avg_depth_full.resample(time='A').mean().load().to_dataset() ## Annual avg
print('\t Estimating the Kendall tau values on the EN4 dataset')
en4_ews = get_ews_array(en4_ann_full,'temperature',bW=bW,wL=wL) ##Gets the Kendall coefficients for trends in AR(1) and variance 
print('\t Saving the netcdf files')
en4_ann_full.to_netcdf(store_path+f'sst_glob_ann_EN4_{years[0]}_{years[1]}.nc')
en4_ews.to_netcdf(store_path+f'sst_glob_ews_EN4_{years[0]}_{years[1]}_{wL}_{bW}.nc')


    
print('Getting annually averaged surface temperatures on the HADISST dataset')
### Reading SSTs from the HADISST dataset
hadisst_file = '../../../datasets/HADISST/HadISST_sst.nc'
hadisst = xr.open_mfdataset(hadisst_file)

hadisst = hadisst.sortby(hadisst.latitude).sel(time=(hadisst['time.year']>=years[0])&(hadisst['time.year']<=years[1]))
hadisst = hadisst.drop('time_bnds')
hadisst = hadisst.where(hadisst.sst>=-2)
hadisst_ann = hadisst.resample(time='A', skipna=True).mean().load()
print('\t Estimating the Kendall tau values on the HADISST dataset')
hadisst_ews = get_ews_array(hadisst_ann,'sst',bW=35,wL=50) ##Gets the Kendall coefficients for trends in AR(1) and variance from the HADISST dataset
print('\t Saving the netcdf files')
hadisst_ews.to_netcdf(store_path+f'sst_glob_ews_HADISST_{years[0]}_{years[1]}.nc')