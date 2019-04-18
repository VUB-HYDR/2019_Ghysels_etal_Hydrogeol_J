# 2019_Ghysels_etal_Hydrogeol_J
Scripts used for the simulations of the two applications in Ghysels et al. (2019), Hydrogeol. J. 

## For users
This repository includes the scripts that are used to simulate the two applications described in Ghysels et al. (2019). These scripts are written in Python 2.7.

### 1. [run_model_riverbedK_realizations.py](./run_model_riverbedK_realizations.py) 
This script is used to produce the results of Application I effect of riverbed heterogeneity on river-aquifer exchange fluxes. It uses spatially distributed fields of riverbed K simulated in SGeMS as input for an existing groundwater flow model (MODFLOW). It uses [FloPy](httpsgithub.commodflowpyflopy) to change the model parameters. The model is run for each riverbed K realization and resulting river-aquifer exchange fluxes are extracted from the model's cell budget file.

### 2. [run_model_change_HFB.py](./run_model_change_HFB.py)
This script is used to produce the results of Application II effect of river bank seepage on river-aquifer exchange fluxes. It changes the parameters of the Horizontal-Flow Boundary (HFB) Package in a MODFLOW model in order to analyze the effect of lateral exchange fluxes through river banks.

### 3. [Figures](./Figures)
Scripts used to generate Figs. 8 and 9 from Ghysels et al. (2019). 

 - [targethist.py](./Figures/targethist.py) is used to plot the target histogram used in the SGS simulations. 
- [plot_k_cross_sections.py](./Figures/plot_k_cross_sections.py) is used to plot a cross-sectional view of ln Kv realizations simulated with SGS (in SGeMS).

## Versions
Version 0.1.0 - April 2019 

## License
This project is licensed under the MIT License. See also the  [LICENSE](./LICENSE.md) file.

## References
Ghysels G, Mutua S, Baya Veliz G & Huysmans M (2019). A modified approach for modelling river-aquifer interaction of gaining rivers in MODFLOW, including riverbed heterogeneity and river bank seepage. Hydrogeol. J. [https://doi.org/10.1007/s10040-019-01941-0](https://doi.org/10.1007/s10040-019-01941-0).