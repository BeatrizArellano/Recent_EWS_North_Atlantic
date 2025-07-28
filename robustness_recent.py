import numpy as np
import pandas as pd
import sys
sys.path.append('../../lib')
from regimeshifts import ews


### Reading selected records
data_path = 'output/sel_recent_rec_data.csv'
sel_rec = pd.read_csv(data_path, index_col=0)


##########  Robustness analysis ######################
#### Estimating trends in Lag-1 Autocorrelation for different combinations of window length and bandwidth

start_year = 1920

sel_rec = ews.Ews(sel_rec[sel_rec.index>=start_year])
print(f'Performing the robustness analysis on {len(sel_rec.columns)} records')
robustness = sel_rec.robustness(indicators=['ar1'],min_wL=20,max_wL=0.8,min_bW=2,max_bW=0.6,res_bW=1,res_wL=1)

for rec_id in sel_rec.columns:
    print(f'Saving {rec_id} to csv.')
    robustness[rec_id]['ar1'].to_csv(f'output/rob_{rec_id}_{start_year}_today.csv')



