import pandas as pd
import numpy as np
from scipy.interpolate import griddata
import rasterio, sys
from rasterio.transform import from_origin
from pyproj import Transformer

zone2epsgMap = {
	7: 3154,
	8: 3155,
	9: 3156,
	10: 3157,
	11: 2955,
	12: 2956,
	13: 2957,
	14: 3158,
	15: 3159,
	16: 3160,
	17: 2958,
	18: 2959,
	19: 2960,
	20: 2961,
	21: 2962,
	22: 3761,
	23: 9711,
	24: 9713
}


def getUTMZone(longitude):
	return ((longitude + 180) // 6) +1

def getEpsgCode(lat, lon):
	zone = getUTMZone(lon)
	if zone < 7 or zone > 24:
		raise RuntimeError('UTM zone outside of bound')
	return zone2epsgMap.get(zone)



if len(sys.argv) < 2:
	print("Usage: python3 rasterize.py <file_path>")
	sys.exit(1)

# Step 1: Read the CSV file
csv_file_path = sys.argv[1]
df = pd.read_csv(csv_file_path)


longitudes = df['Longitude(NAD83)']
latitudes = df['Latitude(NAD83)']


#TODO make sure that all points are in the same zone
epsg_out = 0;
try:
	epsg_out = int(getEpsgCode(latitudes[0], longitudes[0]))
except Exception as err:
	print(err)

#print(epsg_out)

transformer = Transformer.from_crs("epsg:8254", "epsg:{}".format(epsg_out))

# Function to transform coordinates
def transform_coords(row):
	lon, lat = transformer.transform(row['Latitude(NAD83)'], row['Longitude(NAD83)'])
	return pd.Series({'x': lon, 'y': lat})


# Apply the transformation
df[['x', 'y']] = df.apply(transform_coords, axis=1)

#df.to_csv('job432_nad83(csrs)_utm9.csv', index=False)

x = df['x']
y = df['y']
z = df['ChartDatumHeight(LLWM)']


# Step 2: Create a grid for interpolation
grid_x, grid_y = np.meshgrid(np.linspace(x.min(), x.max(), 100), np.linspace(y.min(), y.max(), 100))

# Step 3: Interpolate the surface
grid_z = griddata((x, y), z, (grid_x, grid_y), method='linear')

## Step 4: Define the transform and create the GeoTIFF
#transform = from_origin(grid_x.min(), grid_y.max(), (grid_x.max() - grid_x.min()) / 100, (grid_y.max() - grid_y.min()) / 100)
#new_dataset = rasterio.open(
#	'test.tif',
#	'w',
#	driver='GTiff',
#	height=grid_z.shape[0],
#	width=grid_z.shape[1],
#	count=1,
#	dtype=grid_z.dtype,
#	crs='+proj=latlong',
#	transform=transform,
#)

#new_dataset.write(grid_z, 1)
#new_dataset.close()

#print(f"GeoTIFF saved")
