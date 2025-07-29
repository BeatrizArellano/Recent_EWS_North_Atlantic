"""
Assessing the significance of the measured trend before 1920 for different combinations of bandwidth and window length
"""

import numpy as np
import pandas as pd
import sys
sys.path.append('../../lib')
from regimeshifts import ews



def significance_rob(ts,max_wL=0.8,max_bW=0.6,n=2000, res=5, trend='positive'):
    """
    Estimates the p-values associated to each combination of window length and
    bandwidth. 
    Parameters
    ------------
    ts: Pandas time-series
    max_wL: integer
            Maximum window length.
    max_bW: integer
            Maximum bandwidth.
    n: integer
       Number of surrogate series in the ensemble
    res: integer
        resolution of the significant values over the parameter space
    trend: string ('positive'|'negative')
        If a positive or negative trend is expected, the function estimates the
        p-value accordingly
            
    """
    max_bW = max_bW if max_bW > 1 else int(max_bW * len(ts.dropna()))
    max_wL = max_wL if max_wL > 1 else int(max_wL * len(ts.dropna()))
    bW_vs = np.arange(15,max_bW,res)    
    wL_vs = np.arange(20,max_wL,res)
    pval_ar1 = np.full([len(bW_vs),len(wL_vs)],np.nan)
    for i,b in enumerate(bW_vs):
        for j,w in enumerate(wL_vs): 
            print('AR(1)')
            sig_test_ar1 = ts.significance(indicator='ar1',n=n, detrend=True,bW=b, wL=w,test=trend)
            pval_ar1[i][j] = sig_test_ar1.pvalue
    return bW_vs, wL_vs, pval_ar1



### Reading selected records
data_path = 'output/sel_long_records_data.csv'
records = pd.read_csv(data_path, index_col=0)

start_year = 1750
end_year = 1920

sel_rec = ews.Ews(records[(records.index>=start_year)&(records.index<=end_year)])


n =  2000
## Significance test
for rec in sel_rec.columns:
    print(rec)
    ts = ews.Ews(sel_rec[rec].dropna())
    bW_vs, wL_vs, par1 = significance_rob(ts,max_wL=0.8,max_bW=0.6,n=n)
    np.save(f'output/significant_combinations/bW_vs_{rec}_bef1920.npy', bW_vs)
    np.save(f'output/significant_combinations/wL_vs_{rec}_bef1920.npy', wL_vs)
    np.save(f'output/significant_combinations/par1_{rec}_bef1920.npy', par1)
    del bW_vs, wL_vs, par1                            
                                           
