# Recent and early twentieth century destabilization of the subpolar North Atlantic recorded in bivalves

This repository contains the Python code used in the study "Recent and early twentieth century destabilization of the subpolar North Atlantic recorded in bivalves"

The visualisation code can be accessed in these Notebooks:

  - [Multidecadal variability of AR(1) and lambda](Multidecadal_variability_AR1_lambda.ipynb)
  - [Robustness and significance of trends before 1920](1920s_episode.ipynb)
  - [Robustness and significance of trends over recent decades](Recent_episode.ipynb)
  - [Spatial correlations with EN4 temperatures](Spatial_correlations.ipynb)
  - [Correlations with SPG temperatures and other indices](Corrs_SPG_temp.ipynb)

Robustness and significance for AR(1) and lambda trends were calculated using the python scripts within the [src](src) folder.


The Python module `ews`, which contains the functions used to assess changes in stability, significance, and robustness, is part of the [regimeshifts library](https://github.com/BeatrizArellano/regimeshifts), and can also be found in the [lib](lib/ews.py) folder.

#### Datasets

The full compilation of bivalve records is available on [Zenodo](https://doi.org/10.5281/zenodo.16564478). Please note that this dataset includes records constructed by different researchers. When using this data, ensure proper citation of the original authors for each record. The original sources are provided in the 'Reference' and 'Original Publication' columns of the metadata file.

The HadISST1 and EN4.2.2 datasets can be downloaded from the [Met Office Hadley Centre portal](https://www.metoffice.gov.uk/hadobs/).