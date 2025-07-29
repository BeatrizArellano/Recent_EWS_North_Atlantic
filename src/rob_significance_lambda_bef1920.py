"""
Assessing the significance of the measured trend in lambda before 1920 for different combinations of bandwidth and window length
"""

import multiprocessing
import numpy as np
import os
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
    bW_vs = np.arange(5,max_bW,res)    
    wL_vs = np.arange(20,max_wL,res)
    pval_lambda = np.full([len(bW_vs),len(wL_vs)],np.nan)
    for i,b in enumerate(bW_vs):
        for j,w in enumerate(wL_vs): 
            #print('Lambda')
            sig_test_lambda = ts.significance(indicator='lambd',n=n, detrend=True,bW=b, wL=w,test=trend)
            pval_lambda[i][j] = sig_test_lambda.pvalue.iloc[0]
    return bW_vs, wL_vs, pval_lambda

def process_record(args):
    rec_name, ts_data, max_wL, max_bW, n = args
    print(f"Processing {rec_name} in PID {os.getpid()}")
    ts = ews.Ews(ts_data.dropna())
    bW_vs, wL_vs, plambd = significance_rob(ts, max_wL=max_wL, max_bW=max_bW, n=n)    
    np.save(f'output/significant_combinations/lambda_bW_vs_{rec_name}_bef1920.npy', bW_vs)
    np.save(f'output/significant_combinations/lambda_wL_vs_{rec_name}_bef1920.npy', wL_vs)
    np.save(f'output/significant_combinations/plambda_{rec_name}_bef1920.npy', plambd)
    return rec_name  # just to confirm which record completed

if __name__ == '__main__':
    ### Reading selected records
    data_path = 'output/sel_long_records_data.csv'
    records = pd.read_csv(data_path, index_col=0)
    
    start_year = 1750
    end_year = 1920
    
    sel_rec = ews.Ews(records[(records.index>=start_year)&(records.index<=end_year)])
    
    
    n =  2000
    ## Significance test
    max_wL = 0.8
    max_bW = 0.6

    total_cores = multiprocessing.cpu_count()
    n_cores = max(1, int(total_cores * 0.75))

    tasks = [(rec, sel_rec[rec], max_wL, max_bW, n) for rec in sel_rec.columns]

    with multiprocessing.Pool(processes=n_cores) as pool:
    #with multiprocessing.Pool(processes=len(sel_rec)) as pool:
        for rec in pool.imap_unordered(process_record, tasks):
            print(f"Finished processing: {rec}")
                                           
