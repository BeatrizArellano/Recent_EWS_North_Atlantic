"""
This script generates netcdf files storing the Pearson correlation coefficients
between 0-100m temperatures from the EN4 dataset and each bivalve record.
"""

import numpy as np
import os
import pandas as pd
from scipy import stats
import xarray as xr
import sys
sys.path.append('../../lib/')
from regimeshifts import ews

def get_corr_array(ds,point_ts,name_var,detrend=False,bW=35):
    """
    Computes spatial correlations between a time-series and a dataset
    """
    def get_corr(ts,point_ts,detrend,bW):
        """
        Estimates the Pearson correlation coefficient between a particular time-series
        and the one corresponding to a grid-point over the spatial domain.
        """
        if np.isnan(ts[0]): # If the point is not part of the domain
            return np.array([np.nan,np.nan])
        else:
            if detrend == True:
                ts = ews.Ews(ts).gaussian_det(bW=bW).res[0].values
            pearson = stats.pearsonr(ts, point_ts)
            ## Returns [pearson_r,p_value]
            return np.array([pearson[0], pearson[1]])
    
    dims = list(ds.dims)
    dims.remove('time')
    ### In order to use apply_ufunc the dimensions need to be stacked and grouped
    ds_stacked = ds.stack({'gridPoint':dims}).groupby('gridPoint')
    if detrend == True:
        point_ts =  ews.Ews(point_ts).gaussian_det(bW=bW).res.iloc[:, 0].values
    else:
        point_ts =  point_ts.values
    corr_array = xr.apply_ufunc(get_corr, ds_stacked, input_core_dims=[['time']],output_core_dims=[["corr"]],
                              output_sizes={"corr": 2}, kwargs={'point_ts':point_ts,'detrend':detrend,'bW':bW})  
    
    corr_array = corr_array.unstack('gridPoint')    
    if not isinstance(corr_array,xr.Dataset):
        corr_array = corr_array.to_dataset()
    corr_array['pearson_r'] = corr_array[name_var][0]
    corr_array['p_value'] = corr_array[name_var][1]
    corr_array = corr_array.drop(name_var)    
    #corr_array = corr_array.drop_dims('nv')
    return corr_array



### Reading selected records
#data_path = 'output/sel_recent_rec_data.csv'
data_path = 'output/sel_records_data.csv'
sel_rec = pd.read_csv(data_path, index_col=0)
sel_rec = sel_rec.drop('FG_JEM_d13C', axis=1)

### EN4 dataset

#start_year = 1950
start_year = 1960

en4_file = '../../../datasets/EN4/EN.4.2.2.analyses.g10/*.nc'
en4 = xr.open_mfdataset(en4_file,combine='by_coords')
en4 = en4.sel(time=(en4.time.dt.year>=start_year),depth=slice(*[0,100]))
en4 = en4.assign_coords(lon=(((en4.lon + 180) % 360) - 180))
en4 = en4.sortby(en4.lon)
en4_atl = en4.sel(lon =slice(*[-130,40]), lat = slice(*[-40,80])) ## 

## Averaging the first 100m
en4_avg_depth = en4_atl.temperature.mean(dim='depth').to_dataset()
en4_ann = en4_avg_depth.resample(time='A').mean().load()


bW = 35
store_path = 'output/spatial_correlations/'

for rec_id in sel_rec.columns:
    print(rec_id)
    rec_sliced = sel_rec[rec_id][sel_rec[rec_id].index>=start_year].dropna().sort_index()
    if len(rec_sliced) > 17:
        final_year = rec_sliced.last_valid_index()
        en4_temp = en4_ann.sel(time=(en4_ann.time.dt.year.isin(np.arange(start_year,final_year+1)))).load()
        en4_temp = en4_temp.temperature
        ## Spatial correlations
        print("\t Estimating spatial correlations")
        atl_corr_det = get_corr_array(en4_temp,rec_sliced,'temperature',detrend=True,bW=bW)
        print('\t Saving the netcdf file')
        filename = store_path+f'EN4_{rec_id}_{bW}_bW_{start_year}.nc'
        if os.path.isfile(filename):
            os.remove(filename)
        atl_corr_det.to_netcdf(filename)
        del en4_temp, rec_sliced


