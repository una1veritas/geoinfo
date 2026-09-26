import numpy as np
import matplotlib.pyplot as plt

def generate_fractal_greenland(seed=42):
    """
    グリーンランドの本物の輪郭をベースに、フラクタルノイズを合成して
    数万〜数十万点規模の『海岸線多角形データ列』をシミュレート生成する関数。
    (WGS84 経度・緯度座標系)
    """
    np.random.seed(seed)
    # グリーンランドの主要な特徴点（大まかなベース形状）
    base_lon = [-60, -73, -70, -60, -52, -45, -43, -35, -20, -12, -18, -30, -40, -50, -60]
    base_lat = [60,  68,  76,  78,  82,  83.6, 81,  75,  70,  65,  60,  61,  63,  61,  60]
    
    # 閉じた多角形にするため配列を調整
    lons, lats = np.array(base_lon), np.array(base_lat)
    
    # フラクタル（中間点再分割法）により、数万点まで海岸線の凸凹を増幅
    # イテレーション回数「11」で、約3万点（2^11倍以上）の超高密度データになります
    iterations = 11 
    roughness = 0.4
    
    for i in range(iterations):
        n = len(lons)
        new_lons = np.zeros(2 * n - 1)
        new_lats = np.zeros(2 * n - 1)
        
        new_lons[0::2] = lons
        new_lats[0::2] = lats
        
        # 中間点を計算し、そこにフラクタル（スケールに応じたランダム）な歪みを加える
        mid_lons = (lons[:-1] + lons[1:]) / 2
        mid_lats = (lats[:-1] + lats[1:]) / 2
        
        # 距離に応じたノイズ幅
        dist = np.sqrt((lons[:-1] - lons[1:])**2 + (lats[:-1] - lats[1:])**2)
        noise_lon = np.random.normal(0, dist * roughness)
        noise_lat = np.random.normal(0, dist * roughness)
        
        new_lons[1::2] = mid_lons + noise_lon
        new_lats[1::2] = mid_lats + noise_lat
        
        lons, lats = new_lons, new_lats

    # WGS84の範囲内にクリッピング
    lons = np.clip(lons, -180, 180)
    lats = np.clip(lats, -90, 90)
    
    # 経度・緯度のペア（多角形の点列データ）を返す
    return np.column_stack((lons, lats))

# １．数万点の海岸線データ（多角形の点列）を生成
greenland_polygon = generate_fractal_greenland()
print(f"データ点の数: {len(greenland_polygon):,} ポイント")
print("データのサンプル (経度, 緯度):\n", greenland_polygon[:5])

# ２．地図として描画して「見たことある感じ」を確かめる
plt.figure(figsize=(8, 10))
plt.plot(greenland_polygon[:, 0], greenland_polygon[:, 1], color='darkblue', linewidth=0.5)
plt.fill(greenland_polygon[:, 0], greenland_polygon[:, 1], color='lavender', alpha=0.5)

plt.title("WGS84 Coordinates: Greenland Coastline (Tens of thousands of points)", fontsize=12)
plt.xlabel("Longitude (経度)", fontsize=10)
plt.ylabel("Latitude (緯度)", fontsize=10)
plt.grid(True, linestyle='--', alpha=0.5)
plt.gca().set_aspect('equal', adjustable='box') # 経緯度直交（正距円筒図法）で描画
plt.show()
