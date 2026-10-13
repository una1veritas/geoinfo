import laspy
import numpy as np
import matplotlib.pyplot as plt

# 1. LAS ファイルの読み込み
las_path = "/Users/sin/Downloads/08NF2330.las"
print(f"Loading {las_path}...")
las = laspy.read(las_path)

# 座標（X: 東西方向[m], Y: 南北方向[m], Z: 標高[m]）を取得
x = las.x
y = las.y
z = las.z

print(f"総点数: {len(x):,} 点")
print(f"X範囲: {x.min():.2f} ~ {x.max():.2f}")
print(f"Y範囲: {y.min():.2f} ~ {y.max():.2f}")
print(f"Z範囲: {z.min():.2f} ~ {z.max():.2f}")

# 2. 断面（スライス）の位置を設定
# データの中央付近を通る Y 座標をターゲットにし、前後 10cm（厚み 0.2m）の範囲を切り出し
y_target = np.median(y)  # 必要に応じて任意の数値に調整可能
thickness = 0.2          # スライスの厚み [m]

mask = (y >= (y_target - thickness / 2.0)) & (y <= (y_target + thickness / 2.0))

slice_x = x[mask]
slice_z = z[mask]

# 3. X座標順（スキャン進行方向）にソートして、1次元の「2D順序点列」にする
sort_idx = np.argsort(slice_x)
profile_x = slice_x[sort_idx]
profile_z = slice_z[sort_idx]

# これが Grow-Hull / RDP 等に渡す入力点列 (N x 2 配列) です
points_2d = np.column_stack((profile_x, profile_z))

print(f"\n抽出された2D断面の点数: {len(points_2d):,} 点")

# 4. 断面の可視化プロット
plt.figure(figsize=(14, 5))
plt.scatter(profile_x, profile_z, s=3, c='red', alpha=0.7)
plt.title(f"Vertical Cross-section Profile (Y = {y_target:.2f} m)")
plt.xlabel("X [m] (Distance)")
plt.ylabel("Elevation Z [m]")
plt.grid(True)
plt.axis('equal')  # 建物の垂直壁や直角が歪まないように 1:1 表示
plt.tight_layout()
plt.show()

# 5. （オプション）アルゴリズム実験用に CSV や NumPy 配列で保存する場合
# np.savetxt("profile_2d.csv", points_2d, delimiter=",", header="X,Z", comments="")
