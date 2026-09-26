'''
Created on 2026/09/26

@author: sin
'''

import numpy as np

def generate_katorisenko_data(num_points=2000):
    """
    RDPを最悪計算量 O(N^2) に叩き落とすための『香取線香（渦巻き）』型の点列を生成。
    入力制限なしで O(N log N) を維持する Grow_Hull との圧倒的な差を視覚化できます。
    """
    # 中心に向かって巻いていく角度 theta
    # 点数が多くなるほど細かく密に巻く
    theta = np.linspace(0, 8 * np.pi, num_points)
    
    # アルキメデスの螺旋（外側から内側へ、徐々に半径 r が小さくなる）
    # RDPが「始点と終点の直線」を引いたとき、常に次の最大距離の点が「渦のカーブの途中」に偏るように設計
    r = 1000.0 * (1.0 - (theta / (8 * np.pi + 0.1)))
    
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    
    # 最後に1本の閉じた図形にする場合、中心の終点から外側の始点へ直線で戻して閉じる
    # （始点と終点が一致する閉じた折れ線にする）
    points = list(zip(x, y))
    # points.append(points[0]) # 完全に閉じさせる
    
    return [(float(p[0]), float(p[1])) for p in points]

if __name__ == '__main__':
    # --- 使い方 ---
    katori_points = generate_katorisenko_data(2400)
    katori_points = [(round(pt[0],4), round(pt[1], 4)) for pt in katori_points]
    print(f"香取線香の点数: {len(katori_points)}")
    with open(f'katori_{len(katori_points)}.csv', 'w') as outf :
        for pt in katori_points:
            outf.write(f'{pt[0]},{pt[1]}\n')
    print('finished.')

