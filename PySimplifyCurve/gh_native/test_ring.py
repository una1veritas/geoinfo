from gh_native.gh_native import ConvexHull
import matplotlib.pyplot as plt

# 1. 凸包オブジェクトの生成（Rust製、内部でRingArrayも自動生成されます）
cvx = ConvexHull(epsilon=0.0)

# 2. 点を次々に追加（add -> remove_concave がRust側で超高速に連動します）
epsilon = 1.0
xy = [ (0,0), (0.1, -0.1), (-0.2, 0.1), (-0.1, -0.1), (-0.1, -0.2), (0.25, 0.5), \
      (0.8, 0.25), (1.0, 0.75), (1.4, 0.7), (1.5, 1.0), \
      (1.5, 2.75), (2, 2.75), (2.5, 3.2), \
      (3, 3.5), (3.2, 2), (3, 0.5),  \
      (3.25, 1.0), (3.25, -0.25), (3.5, 0.5), \
      (4, 1.25), (3.5, 1.5), (3, 1.25), (2, 1), (1.5, -0.0) \
]
for pt in xy:
    cvx.add(pt)

print(f"凸包の構成点数: {len(cvx.points)}")
polygon = cvx.polygon_points()
print(f'polygon = {polygon}')
# 4つの極大距離が一瞬で計算されて、Pythonのタプルとして返ってきます
fw, rt, bk, lt = cvx.peak_distances()
print(f"前方の極大距離: {fw}")
print(f"右側の極大距離: {rt}")
print(f"後方の極大距離: {bk}")
print(f"左側の極大距離: {lt}")

x, y = [ x for x, y in xy], [ y for x, y in xy]
polyx, polyy = [p[0] for p in polygon], [p[1] for p in polygon]

fig, ax = plt.subplots()
ax.plot(x, y, 'r.-', lw=2.0, alpha=0.35)
#ax.plot(drx, dry, 'b.-', lw=1) #, alpha=0.75)
plt_title = f'test_ring'
#ax.plot(rdpx, rdpy, 'b.-', lw=1) #, alpha=0.75)
#plt_title = f'RDP (simplify_coords), epsilon = {delta}, {len(xy)} points simplified to {len(simplified)} points'

if len(polygon) > 0 :
    # for polygon in polygons:
    px, py = [pt[0] for pt in polygon], [pt[1] for pt in polygon]
    ax.plot(px, py, 'g--', lw=1) #, alpha=0.75)

labels = [f"{i}" for i in range(len(xy))]
if True :
    for x, y, label in zip(x, y, labels):
        plt.annotate(
            label,          # The text to display
            (x, y),         # The point to annotate (xy)
            textcoords="offset points", # How to position the text
            xytext=(5, 2), # Distance from the point to the text (offset)
            ha='center'     # Horizontal alignment of the text
        )
fig = plt.gcf()
fig.set_size_inches(8, 8, forward=True) 
plt.legend(['Input points', 'simplified path', 'polygon_index path'],loc='best')
plt.title(plt_title)
ax.set_aspect('equal')
plt.show()
