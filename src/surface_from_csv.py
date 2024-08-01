import pandas as pd
import numpy as np
from scipy.interpolate import griddata
import rasterio, sys, math
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



if len(sys.argv) < 3:
	print("Usage: python3 surface_from_csv.py <csv_file_path> <output_tiff_filePath> ")
	sys.exit(1)

# Step 1: Read the CSV file
csv_file_path = sys.argv[1]
output_tiff_filePath = sys.argv[2]
df = pd.read_csv(csv_file_path)


longitudes = df['Longitude(NAD83)']
latitudes = df['Latitude(NAD83)']


#TODO make sure that all points are in the same zone or make sure that points will be at the right pace even if not in same zone
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

x = df['x']
y = df['y']
z = df['ChartDatumHeight(LLWM)']


# 1m x 1m grid size
interpol_grid_size = int(math.sqrt((x.max() - x.min()) *(y.max() - y.min())))

# Step 2: Create a grid for interpolation
grid_x, grid_y = np.meshgrid(np.linspace(x.min(), x.max(), interpol_grid_size), np.linspace(y.min(), y.max(), interpol_grid_size))


# Step 3: Interpolate the surface
grid_z = griddata((x, y), z, (grid_x, grid_y), method='linear')
grid_z = grid_z[::-1]


pixel_size_x = (x.max() - x.min()) / interpol_grid_size
pixel_size_y = (y.max() - y.min()) / interpol_grid_size

transform = from_origin(grid_x.min(), grid_y.max(), pixel_size_x, pixel_size_y)


with rasterio.open(
	output_tiff_filePath,
	'w',
	driver='GTiff',
	height=interpol_grid_size,
	width=interpol_grid_size,
	count=1,
	dtype=grid_z.dtype,
	crs=f"EPSG:{epsg_out}",
	transform=transform,
) as dst:
	dst.write(grid_z, 1)


print("done")
