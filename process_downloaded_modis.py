import numpy as np
import time
import calendar
import os
import glob
from pyhdf import SD
import pandas as pd

station = pd.read_csv("station.csv", index_col=0)



base_path = os.path.expanduser("~/modis_2016/")
fileList = glob.glob(f"{base_path}*.hdf")[:]
#loops through all files listed in the text file
out = []
for index, FILE_NAME in enumerate(fileList):
    FILE_NAME=FILE_NAME.strip()
    print(FILE_NAME)
    print(index*100.0/len(fileList))

    if '3K' in FILE_NAME: #then this is a 3km MODIS file
        print('This is a 3km MODIS file. Leaving... ')
        continue
        #saves all the SDS to be outputted to ASCII in a dictionary
        dataFields=dict([(1,'Optical_Depth_Land_And_Ocean'),(2,'Image_Optical_Depth_Land_And_Ocean'),(3,'Land_sea_Flag'),(4,'Land_Ocean_Quality_Flag')])
    # The name of the SDS to read
    elif 'L2' in FILE_NAME: #Same as above but for 10km MODIS file
        print('This is a 10km MODIS file. Saving... ')
        dataFields=dict([(1,'Deep_Blue_Aerosol_Optical_Depth_550_Land'),(2,'AOD_550_Dark_Target_Deep_Blue_Combined'),
                         (3,'AOD_550_Dark_Target_Deep_Blue_Combined_QA_Flag'), (4,'Aerosol_Cloud_Fraction_Land'),
                        (5, 'Image_Optical_Depth_Land_And_Ocean')])
    else:
        print('The file :',FILE_NAME, ' is not a valid MODIS file (or is named incorrectly). \n')
        continue
    try:
        # open the hdf file for reading
        hdf=SD.SD(FILE_NAME)
    except:
        print('Unable to open file: \n' + FILE_NAME + '\n Skipping...')
        continue

    # Get lat and lon info
    lat = hdf.select('Latitude')
    lat=(lat.get()).ravel()
    latitude = np.array(lat[:])
    lon = hdf.select('Longitude')
    lon=(lon.get()).ravel()
    longitude = np.array(lon[:])

    #Get the scan start time from the hdf file. This is in number of seconds since Jan 1, 1993
    scan_time=hdf.select('Scan_Start_Time')
    scan_time=(scan_time.get()).ravel()
    scan_time=scan_time[:]
    #get the date info from scan_time
    year=np.zeros(scan_time.shape[0])
    month=np.zeros(scan_time.shape[0])
    day=np.zeros(scan_time.shape[0])
    hour=np.zeros(scan_time.shape[0])
    min=np.zeros(scan_time.shape[0])
    sec=np.zeros(scan_time.shape[0])
    #Saves date info for each pixel to be saved later
    for i in range(scan_time.shape[0]):
        temp=time.gmtime(scan_time[i-1]+calendar.timegm(time.strptime('Dec 31, 1992 @ 23:59:59 UTC', '%b %d, %Y @ %H:%M:%S UTC')))
        year[i-1]=temp[0]
        month[i-1]=temp[1]
        day[i-1]=temp[2]
        hour[i-1]=temp[3]
        min[i-1]=temp[4]
        sec[i-1]=temp[5]

    #Begin saving to an output array
    end=8+len(dataFields)#this is the number of columns needed (based on number of SDS read)
    output=np.array(np.zeros((year.shape[0],end)))
    output[0:,0]=year[:]
    output[0:,1]=month[:]
    output[0:,2]=day[:]
    output[0:,3]=hour[:]
    output[0:,4]=min[:]
    output[0:,5]=sec[:]
    output[0:,6]=latitude[:]
    output[0:,7]=longitude[:]
    #list for the column titles
    tempOutput=[]
    tempOutput.append('Year')
    tempOutput.append('Month')
    tempOutput.append('Day')
    tempOutput.append('Hour')
    tempOutput.append('Minute')
    tempOutput.append('Second')
    tempOutput.append('Latitude')
    tempOutput.append('Longitude')
    #This for loop saves all of the SDS in the dictionary at the top (dependent on file type) to the array (with titles)
    for i in range(8,end):
        SDS_NAME=dataFields[(i-7)] # The name of the sds to read
        #get current SDS data, or exit program if the SDS is not found in the file
        try:
            sds=hdf.select(SDS_NAME)
        except:
            print('Sorry, your MODIS hdf file does not contain the SDS:',SDS_NAME,'. Please try again with the correct file type.')
            continue
        #get scale factor for current SDS
        attributes=sds.attributes()
        scale_factor=attributes['scale_factor']
        fillvalue=attributes['_FillValue']
        #get SDS data as a vector
        data=(sds.get()).ravel()
        data=np.array(data[:])
        #The next few lines change fillvalue to NaN so that we can multiply valid values by the scale factor, then back to fill values
        data=data.astype(float)
        data[data==float(fillvalue)]=np.nan
        data=data*scale_factor
        data[np.isnan(data)]=fillvalue
        #the SDS and SDS name are saved to arrays which will be written to the .txt file
        output[0:,i]=data
        tempOutput.append(SDS_NAME)
    #changes list to an array so it can be stacked
    tempOutput=np.asarray(tempOutput)
    #This stacks the titles on top of the data
    output=np.row_stack((tempOutput,output))
    #save the new array to a text file, which is the name of the HDF4 file .txt instead of .hdf
    df = pd.DataFrame(output[1:].astype('float'))
    df.columns = output[0]

    o = []
    for point_num, point in station.T.to_dict().items():

        t = df.iloc[((point['Latitude'] - df.Latitude).abs() + (
                point['Longitude'] - df.Longitude).abs()).sort_values().index].head(1)
        t["Location"] = point["Location"]
        t["Latitude"] = point["Latitude"]
        t["Longitude"] = point["Longitude"]
        o.append(t)
    out.append(pd.concat(o))
modis = pd.concat(out)
modis.to_csv("modis-2016-10k.csv")