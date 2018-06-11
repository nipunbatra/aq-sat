### Downloading data

1. MODIS data: use the wget link the mail
2. [AQ data for a city](download_aq_data.ipynb)

### Processing data

1. [Create a CSV corresponding to Lat/Long of different ground PM2.5 monitoring stations](station.csv)
2. Convert MODIS downloaded files for an year to a single file [10K](process_download_modis.py), [3K](process_download_modis_3k.py)
3. [Downsample PM2.5 AQ data](pm25-downsample.ipynb)
4. Merge the AQ and Satellite dataset [10K](creating-common-dataset-10k.ipynb), [3K](creating-common-dataset-3k.ipynb)

### Learning classifiers

1. Regression [10k](regression.ipynb), [3k](regression-3k.ipynb)


