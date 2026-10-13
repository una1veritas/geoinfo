'''
Created on 2026/10/13

@author: sin
'''
import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt

def extract_2d_slice(pcd_path, z_target, thickness=0.1):
    """
    3D点群ファイルから指定した高さ(z_target)付近の点を切り出し、2D(X, Y)点列を取得する
    
    :param pcd_path: .ply, .pcd, .las 等の点群ファイルパス
    :param z_target: スライスしたいZ座標の中心値
    :param thickness: スライスの厚み（z_target ± thickness/2 の範囲を抽出）
    :return: (N, 2) の NumPy 配列 (X, Y 座標)
    """
    # 1. 点群データの読み込み (.ply, .pcd などに対応)
    pcd = o3d.io.read_point_cloud(pcd_path)
    points = np.asarray(pcd.points)  # shape: (N, 3) -> [x, y, z]

    # 2. Z軸方向のスライス範囲を指定してフィルタリング
    z_min = z_target - (thickness / 2.0)
    z_max = z_target + (thickness / 2.0)
    
    mask = (points[:, 2] >= z_min) & (points[:, 2] <= z_max)
    sliced_points_3d = points[mask]

    # 3. Z座標を落として 2D (X, Y) 点列にする
    points_2d = sliced_points_3d[:, :2]
    
    return points_2d

# --- 実行と可視化の例 ---
if __name__ == '__main__':
    # ※お手持ちの .ply や .pcd ファイルのパスを指定してください
    # Open3Dのサンプルデータをダウンロードして試す場合：
    # dataset = o3d.data.PCDPointCloud()
    # pcd_path = dataset.path
    
    pcd_path = "sample_data.ply"  
    
    # 例えば Z = 1.2m の位置で 厚み 5cm (0.05m) の断面を取得
    points_2d = extract_2d_slice(pcd_path, z_target=1.2, thickness=0.05)

    print(f"抽出された2D点数: {len(points_2d)}")

    # 2Dスライスの簡易プロット
    plt.figure(figsize=(8, 8))
    plt.scatter(points_2d[:, 0], points_2d[:, 1], s=1, c='blue')
    plt.title("Extracted 2D Slice (X-Y Plane)")
    plt.xlabel("X [m]")
    plt.ylabel("Y [m]")
    plt.axis('equal')
    plt.grid(True)
    plt.show()
