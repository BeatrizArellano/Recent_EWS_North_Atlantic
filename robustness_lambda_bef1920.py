"""
Script to assess the robustness of trends in Lambda
before 1920
"""

import numpy as np
import pandas as pd
import sys
sys.path.append('../../lib')
from regimeshifts import ews

### Reading selected records
data_path = 'output/sel_long_records_data.csv'
records = pd.read_csv(data_path, index_col=0)

##########  Robustness analysis ######################
#### Estimating trends in Lag-1 Autocorrelation for different combinations of window length and bandwidth

start_year = 1750
end_year = 1920

sel_rec = ews.Ews(records[(records.index>=start_year)&(records.index<=end_year)])
print(f'Performing the robustness analysis on {len(sel_rec.columns)} records')

robustness = sel_rec.robustness(indicators=['lambd'],min_wL=25,max_wL=0.8,min_bW=10,max_bW=0.6,res_bW=1,res_wL=1)

for rec_id in records.columns:
    print(f'Saving {rec_id} to csv.')
    robustness[rec_id]['lambd'].to_csv(f'output/rob_lambda_{rec_id}_{start_year}_{end_year}.csv')
