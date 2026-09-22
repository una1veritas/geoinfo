'''
Created on 2026/07/09

@author: sin
'''

from ringarray import ringarray
from point2d import *

class ConvexHull(object):
    '''
    Convex Hull for simple polygon points by double ended queue
    '''
    def __init__(self, delta = 0.0):
        self.points = list() # index seq of Point2Ds considering
        self.polygon_index = ringarray(127)     # index seq in clockwise
        self.tolerance = delta
    
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
    
    def polygon_points(self):
        if len(self.polygon_index) == 0 :
            return []
        return [self.polygon_point(i) for i in range(len(self.polygon_index) + 1)]
    
    # test and add pt to points
    def add(self, pt, supress=False):
        #print(pt)
        if len(self) == 0 :
            self.points.append(pt)
            return True
        
        if supress and self.tolerance > 0.0 and distance(self.first_point(), pt) <= self.tolerance :
            self.points.append(pt)
            return True
        
        if len(self.polygon_index) == 0 :
            self.points.append(pt)
            self.polygon_index.append(0)
            self.polygon_index.append(len(self) - 1)
            return True
        if len(self.polygon_index) == 1 :
            self.points.add(pt)
            self.polygon_index.append(len(self) - 1)
            return True

        # axvec = vec(self.points[0], self.points[-1])
        # newvec = vec(self.points[0], pt)
        # if norm(axvec) > norm(newvec) :
        #     # pt getting nearer.
        #     return False
        
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

    
    def peak_distances(self):
        if len(self) <= 2 or len(self.polygon_index) <= 2 :
            return (0.0, 0.0, 0.0, 0.0)
        
        axis_first = self.points[0]
        axis_last = self.points[-1]
        axis = vec(axis_first, axis_last, unit=True)   #代表線単位ベクトル
        axis3 = perpvec(axis, clockwise=True)
        # print(f'axis = {axis}, axis3 = {axis3}')
        self_points = self.points
        self_polygon_index = self.polygon_index
        local_vec = vec
        
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
        # print(f'axis dot prod = {abs(dot_product(axis, vec(self[-1], self.polygon_point(fwpolyix))))}')
        
        # backward peak
        # print('back')        
        # find the first point from which edge projection on axis is positive or equals zero. 
        lb, ub = fwpolyix, fwpolyix + len(self.polygon_index) - 1
        while lb < ub :
            mix = lb + ((ub - lb) >> 1)
            #print(f'lb = {lb}, ub = {ub}, mix = {mix}, evfunc = {evfunc(mix)}')
            if dot_product(axis, local_vec(self_points[self_polygon_index[mix]], self_points[self_polygon_index[mix+1]])) < 0 :
                lb = mix + 1
            else:
                # evfunc(mix) >= value
                ub = mix        
        bkpolyix = ub
        #print(f'ub = {ub % self.length}')
        # bkpolyix = self.polygon_index.binary_search_upper_bound(fwpolyix, fwpolyix + len(self.polygon_index) - 1, \
        #                                                         value = 0, \
        #                                                         evfunc = lambda ix: dot_product(axis, vec(self.polygon_point(ix), self.polygon_point(ix+1))))
        # bkpolyix = self.binary_search_upper_bound(fwpolyix, fwpolyix + len(self.polygon_index) - 1, axis)
        # print(f'bkpolyix = {bkpolyix} (point {self.polygon_index[bkpolyix]}, {self.polygon_point(bkpolyix)} )')
        
        # right peak
        # print('right')
        # rtpolyix = self.polygon_index.binary_search_upper_bound(fwpolyix, bkpolyix, \
        #                                                         value = 0, \
        #                                                         evfunc = lambda ix: -dot_product(axis3, vec(self.polygon_point(ix), self.polygon_point(ix+1))))
        lb, ub = fwpolyix, bkpolyix
        while lb < ub :
            mix = lb + ((ub - lb) >> 1)
            #print(f'lb = {lb}, ub = {ub}, mix = {mix}, evfunc = {evfunc(mix)}')
            if -dot_product(axis3, local_vec(self_points[self_polygon_index[mix]], self_points[self_polygon_index[mix+1]])) < 0 :
                lb = mix + 1
            else:
                # evfunc(mix) >= value
                ub = mix        
        rtpolyix = ub
        # print(f'rtpolyix = {rtpolyix} (point {self.polygon_index[rtpolyix]}, {self.polygon_point(rtpolyix)} )')
        
        # left peak
        # print('left')
        lb, ub = bkpolyix, fwpolyix
        while lb < ub :
            mix = lb + ((ub - lb) >> 1)
            #print(f'lb = {lb}, ub = {ub}, mix = {mix}, evfunc = {evfunc(mix)}')
            if dot_product(axis3, local_vec(self_points[self_polygon_index[mix]], self_points[self_polygon_index[mix+1]])) < 0 :
                lb = mix + 1
            else:
                # evfunc(mix) >= value
                ub = mix        
        ltpolyix = ub
        # ltpolyix = self.polygon_index.binary_search_upper_bound(bkpolyix, fwpolyix, \
        #                                                         value = 0, \
        #                                                         evfunc = lambda ix: dot_product(axis3, vec(self.polygon_point(ix), self.polygon_point(ix+1))))
        #print(f'ltpolyix = {ltpolyix} (point {self.polygon_index[ltpolyix % len(self.polygon_index)]}, {self.polygon_point(ltpolyix)} )')

        #print(f'peaks = {self.polygon_index[fwpolyix]}, {self.polygon_index[rtpolyix]}, {self.polygon_index[bkpolyix]}, {self.polygon_index[ltpolyix]}')
        return (abs(dot_product(axis, local_vec(axis_last, self.polygon_point(fwpolyix)))), \
                abs(dot_product(axis3, local_vec(axis_first, self.polygon_point(rtpolyix)))), \
                abs(dot_product(vec_neg(axis), local_vec(axis_first, self.polygon_point(bkpolyix)))), \
                abs(dot_product(axis3, local_vec(axis_first, self.polygon_point(ltpolyix)))), )

        
