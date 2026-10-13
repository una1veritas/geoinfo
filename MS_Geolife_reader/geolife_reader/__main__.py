import os, sys
import math
import statistics
from pyproj import Proj
import glob

def analyze_geolife_points(root_path):
    file_stats = []
    
    # 全ユーザーの Trajectory フォルダ内の .plt ファイルを探索
    search_path = os.path.join(root_path, '*', 'Trajectory', '*.plt')
    plt_files = glob.glob(search_path)
    
    print(f"総ファイル数: {len(plt_files)} 個の解析を開始します...")
    
    for file_path in plt_files:
        # パスからユーザーIDとファイル名を取得
        parts = file_path.split(os.sep)
        user_id = parts[-3]   # '000' など
        file_name = parts[-1]  # '20081103232153.plt' など
        
        tranpo_type = None
        labels_path = os.path.join(root_path, user_id, 'labels.txt')
        if os.path.exists(labels_path):
            try:
                with open(labels_path, 'r', encoding='utf-8', errors='ignore') as lf:
                    lines = lf.readlines()
                    if len(lines) > 1: # ヘッダー除外
                        tranpo_type = lines[1].strip().split()[-1]
            except Exception as le:
                print(f"labels.txt 読み込みエラー: {le}")

        try:
            lats, lons, t_secs = [], [], []
            
            with open(file_path, 'r', errors='ignore') as f:
                for _ in range(6):  # 先頭6行ヘッダースキップ
                    next(f)
                
                for line in f:
                    arr = line.strip().split(',')
                    if len(arr) < 7:
                        continue
                    lats.append(float(arr[0]))
                    lons.append(float(arr[1]))
                    # 第5列(シリアル値: 1日=1.0) を秒単位に変換 (高速化のポイント)
                    t_secs.append(float(arr[4]) * 86400.0)
            
            row_count = len(lats)
            if row_count < 2:
                continue

            # バウンディングボックスと中心座標
            min_lat, max_lat = min(lats), max(lats)
            min_lon, max_lon = min(lons), max(lons)
            bbox = [min_lat, max_lat, min_lon, max_lon]
            
            center_lat = sum(lats) / row_count
            center_lon = sum(lons) / row_count
            
            proj = Proj(proj='aeqd', lon_0=center_lon, lat_0=center_lat, datum='WGS84')
            x0, y0 = proj(min_lon, min_lat)
            x1, y1 = proj(max_lon, max_lat)
            
            width = round(x1 - x0, 1)
            height = round(y1 - y0, 1)
            
            # --- 点間差分（時間間隔・距離・速度）の計算 ---
            dts = []      # 時間差 (sec)
            dists = []    # 距離 (m)
            speeds = []   # 速度 (km/h)
            
            # 全点のプロジェクション座標を一括変換
            xs, ys = proj(lons, lats)
            
            for i in range(1, row_count):
                dt = t_secs[i] - t_secs[i-1]
                dist = math.hypot(xs[i] - xs[i-1], ys[i] - ys[i-1])
                
                dts.append(dt)
                dists.append(dist)
                
                if dt > 0:
                    # m/s -> km/h 変換
                    speeds.append((dist / dt) * 3.6)

            # 統計量の算出
            dt_median = round(statistics.median(dts), 2) if dts else 0
            dt_mean = round(statistics.mean(dts), 2) if dts else 0
            total_time_min = round((t_secs[-1] - t_secs[0]) / 60.0, 1) # 所要時間(分)
            speed_mean = round(statistics.mean(speeds), 2) if speeds else 0
            speed_max = round(max(speeds), 2) if speeds else 0
            
            file_stats.append({
                'user_id': user_id,
                'tranpo_type': tranpo_type,
                'file_name': file_name,
                'points': row_count,
                'bbox': bbox,
                'width': width,
                'height': height,
                'manhattan': round(width + height, 1),
                'total_time_min': total_time_min,   # 総所要時間（分）
                'dt_median_sec': dt_median,         # 点間間隔の中央値（秒）★重要
                'dt_mean_sec': dt_mean,             # 点間間隔の平均（秒）
                'speed_mean_kmh': speed_mean,       # 平均速度 (km/h)
                'speed_max_kmh': speed_max,         # 最大速度 (km/h)
                'path': file_path,
            })
            
        except Exception as e:
            print(f"エラー（スキップします）: {file_name} -> {e}")
            
    return file_stats

if __name__ == '__main__':
    params = dict()
    for argval in sys.argv[1:]:
        if argval == '--analyze' :
            params['analyze'] = True          
        if argval == '--convert' :
            params['convert'] = True          
            
    lats = []
    lons = []

    if 'analyze' in params and params['analyze'] :
        stats = analyze_geolife_points('/Volumes/Media_SSD/Downloads/Dataset/Geolife Trajectories 1.3/Data')
        filtered_stats = [
            item for item in stats
            if item['manhattan'] <= 50000
            and item['dt_median_sec'] <= 5.0
            and item['speed_mean_kmh'] <= 8.0
            and item['tranpo_type'] != 'bus'
            and item['tranpo_type'] != 'tax'            
        ]
        filtered_stats.sort(key=lambda elem: elem['points'], reverse=True)  # 点数で降順にソート
        for ea in filtered_stats[:12]:
            print(ea)
    elif 'convert' in params and params['convert'] :
        dir_id = '141'
        dirname = f'/Volumes/Media_SSD/Downloads/Dataset/Geolife Trajectories 1.3/Data/{dir_id}/Trajectory'
        pltname = '20111008083033.plt'
        path = os.path.join(dirname, pltname)
        with open(path, 'r') as infile:
            for ln, l in enumerate(infile, start=1):
                if ln < 7:
                    continue
                arr = l.strip().split(',')
                lat = float(arr[0])
                lon = float(arr[1])
                lats.append(lat)
                lons.append(lon)
                # print(f'{ln}: lat = {lat}, lon = {lon}') # 必要に応じて
                
        # 中心座標を計算
        center_lon = sum(lons) / len(lons)
        center_lat = sum(lats) / len(lats)
        print(f'center coordinate (longitude, latitude) = ({center_lon}, {center_lat})')
        
        # 正距方位図法で直交座標に投影
        proj = Proj(proj='aeqd', lon_0=center_lon, lat_0=center_lat, datum='WGS84')
        
        with open(f"../{dir_id}-{pltname.split('.')[0]}.csv", 'w') as outfile:
            for lat, lon in zip(lats, lons):
                x, y = proj(lon, lat)
                outfile.write(f'{x},{y}\n')
            
    print('finished.')

