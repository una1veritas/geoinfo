'''
Created on 2026/07/09

@author: sin
'''

from ringarray import ringarray
from point2d import *
import matplotlib.pyplot as plt

class ConvexHull(object):
    '''
    Convex Hull for simple polygon points by double ended queue
    '''
    def __init__(self): #, delta = 0.0):
        self.points = list() # index seq of Point2Ds considering
        self.polygon_index = ringarray()     # index seq in clockwise
        #self.tolerance = delta
    
    def clear(self):
        self.points.clear()
        self.polygon_index.clear()
        
    def __len__(self):
        return len(self.points)
    
    def __str__(self):
        return f'ConvexHull({", ".join([ str(i)+":"+str(self[i]) for i in range(len(self))])} {[i for i in self.polygon_index]}'
    
    def __getitem__(self, index):
        return self.points[index]
    
    def point(self, index):
        return self.points[index]
    
    def first_point(self):
        return self.points[0]
    
    def last_point(self):
        return self.points[-1]
    
    def polygon_point(self, index):
        # to allow negative index, we use modulo len of polygon_index
        # python negative value -x modulo len equals len - x
        # return self.points[self.polygon_index[index % len(self.polygon_index)]]
        return self.points[self.polygon_index[index]]
    
    # as a debug utility 
    def polygon_points(self):
        if len(self.polygon_index) == 0 :
            return []
        return [self.polygon_point(i) for i in range(len(self.polygon_index) + 1)]
    
    def is_simple(self, pt):
        # outside pf the right front infinite line of the mouth
        return rhombus(self.polygon_point(1), self.polygon_point(0), pt) <= 0 or \
            rhombus(self.polygon_point(-1), self.polygon_point(0), pt) >= 0
        # outside of the left front infinite line of the mouth
    
    # 1 -- Outside the Angle (Reflex Sector), 
    # 0 -- Inside the angle & Outside the polygon
    # -1 -- Inside the angle & Inside the polygon
    def point_location(self, pt) :
        # polygon seq is in clock-wise
        if len(self.polygon_index) < 3 :
            return 1 # don't care
        
        if rhombus(self.polygon_point(1), self.polygon_point(0), pt) <= 0 :
            # right or front of the mouth
            return 1
        if rhombus(self.polygon_point(-1), self.polygon_point(0), pt) >= 0 :
            # outside of the left line of the mouth
            return 1
        
        # check whether the pt is inside or outside of the polygon
        # --- Binary Search Phase ---
        # We know 'pt' is strictly between ray(0->1) and ray(0->size-1)
        low = 1
        high = len(self.polygon_index) - 1
        
        while low + 1 < high:
            mid = (low + high)>>1
            # Check which side of the ray V0 -> Vmid the point lies on
            if rhombus(self.polygon_point(mid), self.polygon_point(0), pt) < 0:
                # Point is to the right of the mid ray -> search the right half
                high = mid
            else:
                # Point is to the left of the mid ray -> search the left half
                low = mid
                
        # --- Final Edge Check ---
        # The point is now trapped inside the single triangle triangle: V0, Vlow, Vhigh
        # We check if 'pt' is inside or outside the polygon edge Vlow -> Vhigh
        if rhombus(self.polygon_point(high), self.polygon_point(low), pt) <= 0:
            # It's to the right of the closing edge -> Outside the polygon
            return 0
        else:
            # It's to the left of the closing edge -> Inside the polygon
            return -1
    
    # check and add pt to points
    def add(self, pt):
        # print(pt)
        if len(self) == 0 :
            self.points.append(pt)
            return True
        
        if len(self.polygon_index) == 0 :
            self.points.append(pt)
            self.polygon_index.append(0)
            self.polygon_index.append(len(self) - 1)
            return True

        if len(self.polygon_index) == 1 :
            self.points.append(pt)
            self.polygon_index.append(len(self) - 1)
            return True
        
        # point[0]-point[1]-pt
        if rhombus(self.polygon_point(1), self.polygon_point(0), pt) <= 0 :
            self.points.append(pt)
            # right or front of the mouth
            self.polygon_index.append(self.polygon_index.popleft())
            self.polygon_index.appendleft(len(self) - 1)
        elif rhombus(self.polygon_point(-1), self.polygon_point(0), pt) >= 0 :
            self.points.append(pt)
            # outside of the left line of the mouth
            self.polygon_index.appendleft(len(self)-1)
        else:
            # inside the corner by pt; reject point and close convex-hull
            return False
        
        self.remove_concave()
        return True
        
    def remove_concave(self):
        # from tail
        #print(self.polygon_index)
        beak_ix = self.polygon_index.popleft()    # polygon_index is a ring sequence
        beak = self.point(beak_ix)
        
        #print(f'beak = {beak} ({beak_ix})')
        # anti-clockwise check and pop
        while len(self.polygon_index) > 2 :
            if rhombus(beak, self.polygon_point(-1), self.polygon_point(-2)) < 0 : 
                self.polygon_index.pop() # pop-out polygon_index[-1]
            else:
                break
        # from mouth, clock wise check and pop
        while len(self.polygon_index) > 2 :
            if rhombus(beak, self.polygon_point(0), self.polygon_point(1)) > 0 : 
                self.polygon_index.popleft() # pop-out polygon_index[0]
            else:
                break
        self.polygon_index.appendleft(beak_ix)
        #print(self.polygon_index)

    def ternary_search_max(self, axis_first, axis_last):        
        n = len(self.polygon_index)
        if n == 0 :
            return None
        elif n == 1:
            return 0
        
        local_vec = vec
        axis = local_vec(axis_first, axis_last, unit=True)
        self_points = self.points
        self_polygon_index = self.polygon_index
        low = 0
        high = n - 1
        # --- 最初に1回だけ：山がリングの裏側（中央が谷）にあるかチェックして正常化 ---
        # 3個以下のときは以下の処理をスキップ
        if high - low > 2:
            m1 = low + (high - low) // 3
            m2 = low + ((high - low) << 1) // 3
            if dot_product(axis, local_vec(axis_last, self_points[self_polygon_index[low]])) >= dot_product(axis, vec(axis_last, self_points[self_polygon_index[m1]])) \
            and dot_product(axis, local_vec(axis_last, self_points[self_polygon_index[m2]])) <= dot_product(axis, vec(axis_last, self_points[self_polygon_index[high]])) :
                # 山をおもて側に引きずり出す（最初の一発だけ有効）
                low = m2 + 1
                high = m1 + n - 1

        while high - low > 2:
            m1 = low + (high - low) // 3
            m2 = low + ((high - low)<<1) // 3
    
            # v_low = forward_projection(low) # arr[low]
            v_m1 = dot_product(axis, local_vec(axis_last, self_points[self_polygon_index[m1]]))
            v_m2 = dot_product(axis, local_vec(axis_last, self_points[self_polygon_index[m2]])) # arr[m2]
            # v_high = forward_projection(high) # arr[high]

            # print(f'ternary search: {high-low}, low={low}, m1={m1}, m2={m2}, high={high}, v_low={v_low}, {v_m1}, {v_m2}, v_high={v_high}')
            
            # 2. 通常の三分探索（標準ロジック）
            if v_m1 < v_m2:
                low = m1 + 1
                # print('case 3')
            elif v_m1 > v_m2:
                high = m2 - 1
                # print('case 4')      

            # 3. 平坦な山頂（プラトー）
            else:
                # 通常の平坦な山頂：両側を狭める
                low = m1 + 1
                high = m2 - 1
                # print('case 7')
    
            # 探索範囲は絞られる一方なので low, high は最大 2n 程度、
            # したがってわざわざ % を取って小さく維持する必要はない
        # print(f'low = {low}, low % n = {low % n}')
        # print(f'high - low = {high - low}')
        # low <= high が完全に維持されているため、引き算も range も100%安全！
        if high > low :
            # print(f'ternary search: brute force search between: low={low}, high={high}')
            maxix = low
            maxvec = local_vec(axis_last, self_points[self_polygon_index[maxix]])
            for i in range(low + 1, high + 1):
                # print(f'ternary search: {self[i]}:{evfunc(i)} > {self[maxix]}:{evfunc(maxix)}')
                if dot_product(axis, local_vec(axis_last, self_points[self_polygon_index[i]])) > dot_product(axis, maxvec):
                    maxix = i
                    maxvec = local_vec(axis_last, self_points[self_polygon_index[maxix]])
            return maxix % n

        return low % n

    def search_upper_bound(self, lb, ub, paraxis):        
        n = len(self.polygon_index)
        if lb >= n :
            lb %= n
        if lb > ub :
            ub = ub % n + n

        self_points = self.points
        self_polygon_index = self.polygon_index
        
        #print(f'search_upper_bound: lb = {lb}, ub = {ub}')
        while lb < ub :
            mix = lb + ((ub - lb) >> 1)
            #print(f'lb = {lb}, ub = {ub}, mix = {mix}, evfunc = {evfunc(mix)}')
            if dot_product(paraxis, vec(self_points[self_polygon_index[mix]], self_points[self_polygon_index[mix+1]])) < 0 :
                lb = mix + 1
            else:
                # evfunc(mix) >= value
                ub = mix
        
        #print(f'ub = {ub % self.length}')
        return ub % n

    
    def peak_distances(self):
        if len(self) <= 2 or len(self.polygon_index) <= 2 :
            return (0.0, 0.0, 0.0, 0.0)
        
        axis_first = self.points[0]
        axis_last = self.points[-1]
        axis = vec(axis_first, axis_last, unit=True)   #代表線単位ベクトル
        axis3 = perpvec(axis, clockwise=True)
        axis9 = vec_neg(axis3)
        # print(f'axis = {axis}, axis3 = {axis3}')
        
        # find peaks as indexes on polygon_index deque.
        # print(f'search peaks in [', end='')
        # for i in range(len(self.polygon_index)):
        #     print(f'{self.polygon_point(i)}', end=', ')
        # print(']')
        # self[-1] == self.polygon_point(0)

        #forward peak
        # print('forward')
        # fwpolyix = self.polygon_index.ternary_search_max(evfunc = lambda ix: dot_product(axis,vec(lastpt, self.polygon_point(ix))))
        fwpolyix = self.ternary_search_max(axis_first, axis_last)
        # print(f'fwpolyix = {fwpolyix} (point {self.polygon_index[fwpolyix]}, {self[self.polygon_index[fwpolyix]]} ), vec from self[-1] = {vec(self[-1], self.polygon_point(fwpolyix))}')
        
        # search the backward peak
        
        bkpolyix = self.search_upper_bound(fwpolyix, fwpolyix + len(self.polygon_index) - 1, axis)        
        # print(f'bkpolyix = {bkpolyix} (point {self.polygon_index[bkpolyix]}, {self.polygon_point(bkpolyix)} )')
        
        # search the right (3 o'clock) peak
        # print('right')
        
        rtpolyix = self.search_upper_bound(fwpolyix, bkpolyix, axis9)
        
        # search the left (9 o'clock) peak point
        # print('left')
        ltpolyix = self.search_upper_bound(bkpolyix, fwpolyix, axis3)
        #print(f'ltpolyix = {ltpolyix} (point {self.polygon_index[ltpolyix % len(self.polygon_index)]}, {self.polygon_point(ltpolyix)} )')

        #print(f'peaks = {self.polygon_index[fwpolyix]}, {self.polygon_index[rtpolyix]}, {self.polygon_index[bkpolyix]}, {self.polygon_index[ltpolyix]}')
        return (abs(dot_product(axis, vec(axis_last, self.polygon_point(fwpolyix)))), \
                abs(dot_product(axis3, vec(axis_first, self.polygon_point(rtpolyix)))), \
                abs(dot_product(vec_neg(axis), vec(axis_first, self.polygon_point(bkpolyix)))), \
                abs(dot_product(axis3, vec(axis_first, self.polygon_point(ltpolyix)))), )


if __name__ == '__main__':
    xy = [ 
        (0, 0), (0.4, 0), (0.2, 1), (0.5, 0.5), (0.4, 0.8), 
        (0.6, 0.3), (0.5, 0.8), (0.07, 0.4), (0.5, 0.0), 
    ]
    cvx = ConvexHull()
    for ix in range(0, len(xy)):
        p = xy[ix]
        inout = cvx.point_location(p)
        if inout == 1:
            cvx.add(p)
            print(cvx)
            continue
        
        if inout == -1:
            print(f'point {p} is inside the convex hull, skipped.')
            continue
        if inout == 0:
            print(f'point {p} is inside the angle, out side of convex hull, rejected.')
            break

    # 1. Extract X and Y coordinates for all input points
    all_x = [p[0] for p in xy]
    all_y = [p[1] for p in xy]
    
    # 2. Extract X and Y coordinates for the completed Convex Hull vertices
    # (Assuming your hull objects lets you iterate or fetch all current vertices)
    hull_points = [cvx.polygon_point(i) for i in range(len(cvx.polygon_index))]
    # Close the polygon loop for drawing by appending the first point to the end
    hull_points.append(hull_points[0]) 
    
    hull_x = [p[0] for p in hull_points]
    hull_y = [p[1] for p in hull_points]
    
    # 3. Create the Plot
    rejected_pt = xy[ix]
    
    plt.figure(figsize=(10, 8)) # ラベルが見やすくなるよう少し大きめに
    plt.scatter(all_x, all_y, color='gray', label='Input Points (xy)', zorder=2)
    plt.plot(hull_x, hull_y, color='blue', linestyle='-', linewidth=2, label='Convex Hull Perimeter', zorder=3)
    plt.scatter(hull_x[:-1], hull_y[:-1], color='red', s=50, label='Hull Vertices', zorder=4)
    plt.scatter(rejected_pt[0], rejected_pt[1], color='orange', marker='X', s=150, label='Rejected Point (0.25, 0.5)', zorder=5)
    
    # ----------------------------------------------------
    # 4. 【追加】点に番号のラベルを振る
    # ----------------------------------------------------
    # (A) すべての入力データ（xy）にインデックス番号を振る（黒い小さな文字）
    for idx, p in enumerate(xy):
        plt.annotate(
            str(idx), 
            (p[0], p[1]), 
            textcoords="offset points", 
            xytext=(5, 5),   # 点の右上に少しずらす
            ha='center', 
            fontsize=9, 
            color='black',
            alpha=0.6        # 邪魔にならないよう少し薄く
        )
    
    # (B) 凸包のデック（polygon_index）の並び順（0, 1, 2, ...）を赤文字で強調表示する
    for local_idx in range(len(cvx.polygon_index)):
        p = cvx.polygon_point(local_idx)
        plt.annotate(
            f"p({local_idx})", # p(0), p(1) と表示
            (p[0], p[1]), 
            textcoords="offset points", 
            xytext=(-15, -15), # 全体の番号と重ならないよう、左下にずらす
            ha='center', 
            fontsize=10, 
            fontweight='bold', # 太字
            color='red',       # 赤文字
            bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="red", alpha=0.7, lw=0.5) # 小さな枠線
        )
    # ----------------------------------------------------
    
    # --- 後半の装飾コード（そのまま） ---
    plt.title('Convex Hull and Point Location Visualization with Labels')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.show()
