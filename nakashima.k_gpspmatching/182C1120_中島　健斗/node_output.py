import geopandas
import matplotlib.pyplot as plt
import momepy
import pandas as pd
import networkx as nx
from contextily import add_basemap
from libpysal import weights

fp=r"sample.geojson"
df = geopandas.read_file(fp)
remove=[]
for i, row in df.iterrows():
    if str(row[1])[:2] == "JR":
        remove.append(i)
        continue
    if str(row[3])[:2] != "No":
        remove.append(i)
        continue
df.drop(index=remove, inplace=True)

rivers = df
G = momepy.gdf_to_nx(rivers, approach="primal")
positions = {n: [n[0], n[1]] for n in list(G.nodes)}
# Plot
f, ax = plt.subplots(1, 2, figsize=(12, 6), sharex=True, sharey=True)
rivers.plot(color="k", ax=ax[0])
for i, facet in enumerate(ax):
    facet.set_title(("road", "Graph")[i])
    facet.axis("off")
nx.draw(G, positions, ax=ax[1], node_size=5)
print(G.nodes)
plt.show()


with open( 'similer.csv', mode='w') as outfile:
    for i in G.nodes:
        outfile.write(str(i)+"\n")