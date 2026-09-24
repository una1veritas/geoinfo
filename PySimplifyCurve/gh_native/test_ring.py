import math
from gh_native.gh_native import RingArray

def run_verification():
    print("=== 1. 初期化と基本操作（追加・削除・ランダムアクセス）の検証 ===")
    # 引数なしで初期化（省略可能に修正したため RingArray() で動作します）
    ring = RingArray()
    
    # データの追加（Python側のテストメイン処理を再現）
    data = [9, 1, 3, -1, -5, 7, 7, 0, 11, -12, 99]
    for ea in data:
        if ea >= 0:
            ring.append(ea)
        else:
            ring.appendleft(ea)
            
    print(f"要素数 (len): {len(ring)}") # 11
    print(f"論理インデックス0の要素: {ring[0]}")
    print(f"論理インデックス1の要素: {ring[1]}")
    print(f"論理インデックス-1の要素: {ring[-1]}")
    
    print("\n先頭から5件 popleft します:")
    for _ in range(5):
        print(f"  popleft: {ring.popleft()}")
        
    print(f"現在の要素数: {len(ring)}")
    
    
    print("\n=== 2. 元の点座標のセット（set_points）の検証 ===")
    # テスト用の二次元平面上の点リスト（例：原点、右、上、左、下など）
    # インデックスに対応する座標を準備
    # 例として100要素分の適当な座標を生成、上記dataのインデックスが安全にアクセスできるようにする
    points = [(float(i), float(i * 2)) for i in range(100)]
    # 特殊な座標をいくつか上書き（内積の検証用）
    points[0] = (0.0, 0.0)   # 原点
    points[7] = (10.0, 0.0)  # 右側に遠い点
    points[11] = (0.0, 15.0) # 上側に遠い点
    
    # Rust側に元の点リストを一括セット
    ring.set_points(points)
    print("元の点リスト（points）のセットに成功しました。")
    
    
    print("\n=== 3. 特殊化二分探索（search_upper_bound）の検証 ===")
    # 現在の ring の中身を一度クリアし、検証用の凸包インデックスを模した列を作る
    ring.clear()
    ring.append(0)  # points[0] = (0, 0)
    ring.append(7)  # points[7] = (10, 0)  -> 辺ベクトルは (10, 0)
    ring.append(11) # points[11] = (0, 15) -> 辺ベクトルは (-10, 15)
    
    # 軸ベクトル（例: X軸の正の方向 (1.0, 0.0)）
    # 最初の辺 (0->7) との内積は 1.0 * 10 + 0.0 * 0 = 10 (>= 0)
    # 次の辺 (7->11) との内積は 1.0 * (-10) + 0.0 * 15 = -10 (< 0)
    paraxis = (1.0, 0.0)
    
    print(f"現在のデック（凸包）の長さ: {len(ring)}")
    print(f"論理インデックス0の点座標: {points[ring[0]]}")
    print(f"論理インデックス1の点座標: {points[ring[1]]}")
    print(f"論理インデックス2の点座標: {points[ring[2]]}")
    
    # あなたのコードと同等の条件で二分探索を実行
    # 内積が最初に 0 未満になる、あるいは境界となるインデックスを探す
    target_idx = ring.search_upper_bound(0, 2, paraxis)
    print(f"軸ベクトル {paraxis} に対する二分探索の結果（境界インデックス）: {target_idx}")

if __name__ == "__main__":
    ring = RingArray()
    data = [9, 1, 3, -1, -5, 7, 7, 0, 11, -12, 99]
    for ea in data:
        if ea >= 0 :
            ring.add(ea)
        else:
            ring.appendleft(ea)
        print('ring = ', ring)
        print()
    
    print(ring.popleft())
    print(ring.popleft())
    print(ring.popleft())
    print(ring.popleft())
    print(ring.popleft())
    print(ring)
    print('heads and tails ', ring[0], ring[1], ring[-1], ring[-2])
    while len(ring) > 0 :
        print(ring.pop())
        print(ring)
    #run_verification()

    exit(0)
    random.seed(1)
    ring = ringarray()
    for ringlen in range(1, 13):
        d = random.uniform(0, 2* pi)
        for e in strictly_increasing_sequence(0, 2 * pi, ringlen) :
            ring.append(round(10*sin(e), 1))
        print(ring)
        # --- Example Usage ---
        
        ix = ring.ternary_search_max(evfunc = lambda i: ring[i])
        print(f"The maximum element in the ring buffer is: ring[{ix}] = {ring[ix]}")
        # Output: The maximum element in the ring buffer is: 12
        
        ring.clear()
    print()