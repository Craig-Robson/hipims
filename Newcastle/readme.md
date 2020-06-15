This folder contains data files to setup a flood model in Newcastle.
Input files include DEM(DEM2m.gz), a raster file indicating street cells(streetMask2m.asc.gz), rainfall rate(rain_source_data_1.csv) from rainfall model, rainfall mask(rain_mask_UO_radar.gz) indicating the position of each rainfall source point, and gauge position(gauges_pos.csv) for monitoring full time-scale water depth and velocity.
A python script (run_NCL_2m_MG.py) is used to setup and run hipims model. The number of GPUs can be changed in this script.
