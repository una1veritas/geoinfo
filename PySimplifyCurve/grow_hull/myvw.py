'''
Created on 2026/10/11

@author: sin
'''

import heapq

def triangle_area(p1, p2, p3):
    """3点 p1, p2, p3 がつくる三角形の面積を計算"""
    return 0.5 * abs(
        p1[0] * (p2[1] - p3[1]) +
        p2[0] * (p3[1] - p1[1]) +
        p3[0] * (p1[1] - p2[1])
    )

def vw_simplification(xy: list, threshold_area: float) -> list:
    """
    Visvalingam-Whyatt 簡略化アルゴリズム
    
    :param xy: (x, y) 座標のリスト [(x0, y0), (x1, y1), ...]
    :param threshold_area: 削除する最小三角形の面積閾値 Delta
    :return: 残った点のインデックスのリスト（昇順）
    """
    n = len(xy)
    if n <= 2:
        return list(range(n))

    # 双方向連結リスト構造を配列で表現 (prev_idx, next_idx)
    prev_node = [i - 1 for i in range(n)]
    next_node = [i + 1 for i in range(n)]
    prev_node[0] = None
    next_node[-1] = None

    # 各点の「有効面積 (Effective Area)」を計算
    areas = [float('inf')] * n
    for i in range(1, n - 1):
        areas[i] = triangle_area(xy[i - 1], xy[i], xy[i + 1])

    # 最小ヒープ構造で最小面積の点を管理: (面積, 点のインデックス)
    heap = [(areas[i], i) for i in range(1, n - 1)]
    heapq.heapify(heap)

    # 削除フラグ
    removed = [False] * n

    while heap:
        area, idx = heapq.heappop(heap)

        # 既に古い情報でヒープに残っていた場合や削除済みの場合はスキップ
        if removed[idx] or area != areas[idx]:
            continue

        # 最小面積が閾値を超えたら終了
        if area > threshold_area:
            break

        # 点 idx を削除対象に設定
        removed[idx] = True

        # 隣接ノードのリンクを更新
        p = prev_node[idx]
        nxt = next_node[idx]
        
        if p is not None:
            next_node[p] = nxt
        if nxt is not None:
            prev_node[nxt] = p

        # 削除された点の前後のノードの面積を再計算してヒープを更新
        # ※ Visvalingamの原著に従い、単調増加性を保つため前回の削除面積との max を取る
        if p is not None and prev_node[p] is not None:
            new_area = max(area, triangle_area(xy[prev_node[p]], xy[p], xy[nxt]))
            areas[p] = new_area
            heapq.heappush(heap, (new_area, p))

        if nxt is not None and next_node[nxt] is not None:
            new_area = max(area, triangle_area(xy[p], xy[nxt], xy[next_node[nxt]]))
            areas[nxt] = new_area
            heapq.heappush(heap, (new_area, nxt))

    # 残った点のインデックスを集約して返す
    result_indices = []
    curr = 0
    while curr is not None:
        result_indices.append(curr)
        curr = next_node[curr]

    return result_indices