import pygmt
import sys, csv
import numpy as np
import pandas as pd

if len(sys.argv) != 5:
	sys.stderr.write("Usage: python3 gen_map.py input_Data depth_column_name output_Filename Map_title\n")
	sys.exit(1)
	
inputFilePath = sys.argv[1]
columnName = sys.argv[2]
outputFilename = sys.argv[3]
mapTitle = sys.argv[4]


data = pd.read_csv(inputFilePath, delimiter=",", dtype=float, header=0)
print("[+] Read {} lines".format(len(data.index)))


minLat = data.min(axis=0)[0]
minLon = data.min(axis=0)[1]
maxLat = data.max(axis=0)[0]
maxLon = data.max(axis=0)[1]

depth = data[columnName]
cpt = pygmt.makecpt(cmap="rainbow", series=[min(depth), max(depth)])

fig = pygmt.Figure()
fig.basemap(region=[minLon - 0.005, maxLon + 0.005, minLat - 0.005, maxLat + 0.005], 
			frame=["a", "+t{}".format(mapTitle)],
			projection="M6i"
)
fig.coast(land="lightblue", water="lightblue")
fig.plot(x=data["longitude"], y=data["latitude"], style="c0.03c", fill=depth, cmap=True)
fig.colorbar(cmap=cpt, frame=["x+lDepth m", "y+lm"])

#fig.legend(box=True)
fig.image(
    imagefile="https://cidco.ca/themes/cidco/css/img/logo_cidco.png",
    position="jBR+w2+o0.2c",
    box=True,
)

with fig.inset(
	position="jBL",
	region=[round(minLon-0.3,3), round(maxLon+0.3,3), round(minLat-0.3,3), round(maxLat+0.3,3)],
	box="+gwhite+p1p",
	projection="M2c"
):
	fig.coast(shorelines="thinnest", land="green", water="lightblue")
	fig.plot(data=[[minLon, minLat, maxLon, maxLat]], style="r+s", pen="1p,red")

#fig.show()
fig.savefig("{}".format(outputFilename), crop=True, dpi=1200)


