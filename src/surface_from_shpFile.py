import geopandas as gpd
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
import sys
import rasterio

# XXX shapefile needs to contain points in a projected coordinates system

if len(sys.argv) < 2:
	print("Usage: python3 grass.py <file_path>")
	sys.exit(1)

# Step 1: Read the shapefile
shapefile_path = sys.argv[1]
gdf = gpd.read_file(shapefile_path)

# Step 2: Extract coordinates
x = gdf.geometry.x
y = gdf.geometry.y
z = gdf['ChartDatum']  # Assuming 'z' is the column name for the z values

# Step 3: Create a grid for interpolation
grid_x, grid_y = np.meshgrid(np.linspace(x.min(), x.max(), 1000), np.linspace(y.min(), y.max(), 1000))

# Step 4: Interpolate the surface
grid_z = griddata((x, y), z, (grid_x, grid_y), method='linear')

# Step 5: Plot the surface
plt.figure(figsize=(10, 8))
plt.contourf(grid_x, grid_y, grid_z, levels=100, cmap='viridis')
plt.colorbar(label='Elevation')
#plt.scatter(x, y, c=z, edgecolor='k', cmap='viridis')
plt.title('Interpolated Surface')
plt.xlabel('X')
plt.ylabel('Y')
plt.show()

