use pyo3::prelude::*;
use crate::ring_array::RingArray;

// point2d.py のロジックを Rust 内のインライン関数（超高速）として再現
#[inline]
fn rhombus(a: (f64, f64), b: (f64, f64), c: (f64, f64)) -> f64 {
    (c.0 - b.0) * (a.1 - b.1) - (c.1 - b.1) * (a.0 - b.0)
}

#[inline]
fn dot_product(va: (f64, f64), vb: (f64, f64)) -> f64 {
    va.0 * vb.0 + va.1 * vb.1
}

/*#[inline]
fn distance(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((b.0 - a.0).powi(2) + (b.1 - a.1).powi(2)).sqrt()
}
*/

#[pyclass]
pub struct ConvexHull {
    #[pyo3(get)]
    pub points: Vec<(f64, f64)>,      // input seq of Point2Ds considering
    //#[pyo3(get)]
    pub polygon_index: RingArray,     // index seq of polygon in clockwise
//    #[pyo3(get, set)]
//    pub tolerance: f64,
}

#[pymethods]
impl ConvexHull {
    //#[pyo3(signature = (epsilon = 0.0))]
    #[new]
    pub fn new(/* epsilon: f64*/) -> Self {
        ConvexHull {
            points: Vec::new(),
			//polygon_index: RingArray::new(Some(pyo3::Py::new(unsafe { Python::assume_attached() }, 127).unwrap())),
			polygon_index: RingArray::new(None),
//            tolerance: epsilon,
        }
    }

    pub fn clear(&mut self) {
        self.points.clear();
        self.polygon_index.clear();
    }

	// 変更後: pub fn len(&self) -> usize を用意し、Python用にも公開するなら属性をつける
	#[pyo3(name = "__len__")]
	pub fn len(&self) -> usize {
        self.points.len()
    }

//	# as a debug utility 
	pub fn polygon_points(&self) -> Vec<(f64, f64)> {
		if self.polygon_index.length == 0 {
		    return Vec::new();
		}
		let mut result = Vec::new(); // 結果を格納する空の箱を用意
		for i in 0..=(self.polygon_index.length as isize) {
			let pt_idx = self.polygon_index.__getitem__(i) as usize;
			result.push(self.points[pt_idx]);
		}
		result
	}
		
    // 1. 点の追加ロジック (add) の完全移植
    #[pyo3(signature = (pt))]
    pub fn add(&mut self, pt: (f64, f64)) -> bool {
        let n_points = self.points.len();
        if n_points == 0 {
            self.points.push(pt);
            return true;
        }

        let n_poly = self.polygon_index.length;
        if n_poly == 0 {
            self.points.push(pt);
            self.polygon_index.append(0);
            self.polygon_index.append((self.points.len() - 1) as i32);
            return true;
        }
        if n_poly == 1 {
            self.points.push(pt);
            self.polygon_index.append((self.points.len() - 1) as i32);
            return true;
        }

        // 頂点座標の間接参照をヘルパー関数的に解決
        let poly_p0 = self.points[self.polygon_index.__getitem__(0) as usize];
        let poly_p1 = self.points[self.polygon_index.__getitem__(1) as usize];
        let poly_p_minus1 = self.points[self.polygon_index.__getitem__(-1) as usize];

        if rhombus(poly_p1, poly_p0, pt) <= 0.0 {
            self.points.push(pt);
            let popped = self.polygon_index.popleft().unwrap();
            self.polygon_index.append(popped);
            self.polygon_index.appendleft((self.points.len() - 1) as i32);
        } else if rhombus(poly_p_minus1, poly_p0, pt) >= 0.0 {
            self.points.push(pt);
            self.polygon_index.appendleft((self.points.len() - 1) as i32);
        } else {
            return false;
        }

        self.remove_concave();
        true
    }

    // 2. 凹点の削除ロジック (remove_concave) の完全移植
    pub fn remove_concave(&mut self) {
        if self.polygon_index.length == 0 { return; }
        
        let beak_ix = self.polygon_index.popleft().unwrap();
        let beak = self.points[beak_ix as usize];

        // 反時計回りのチェックと pop
        while self.polygon_index.length > 2 {
            let p_minus1 = self.points[self.polygon_index.__getitem__(-1) as usize];
            let p_minus2 = self.points[self.polygon_index.__getitem__(-2) as usize];
            if rhombus(beak, p_minus1, p_minus2) < 0.0 {
                let _ = self.polygon_index.pop();
            } else {
                break;
            }
        }

        // 時計回りのチェックと popleft
        while self.polygon_index.length > 2 {
            let p0 = self.points[self.polygon_index.__getitem__(0) as usize];
            let p1 = self.points[self.polygon_index.__getitem__(1) as usize];
            if rhombus(beak, p0, p1) > 0.0 {
                let _ = self.polygon_index.popleft();
            } else {
                break;
            }
        }

        self.polygon_index.appendleft(beak_ix);
    }

    // 3. 特殊化二分探索 (辺ベクトル版)
    pub fn search_upper_bound(&self, mut lb: isize, mut ub: isize, paraxis: (f64, f64)) -> Option<usize> {
        if self.polygon_index.length == 0 { return None; }
        let n = self.polygon_index.length as isize;

        if lb >= n { lb = lb % n; }
        if lb > ub { ub = (ub % n) + n; }

        while lb < ub {
            let mix = lb + ((ub - lb) >> 1);
            let idx_curr = self.polygon_index.__getitem__(mix) as usize;
            let idx_next = self.polygon_index.__getitem__(mix + 1) as usize;
            
            let vec_x = self.points[idx_next].0 - self.points[idx_curr].0;
            let vec_y = self.points[idx_next].1 - self.points[idx_curr].1;
            
            if dot_product(paraxis, (vec_x, vec_y)) < 0.0 {
                lb = mix + 1;
            } else {
                ub = mix;
            }
        }
        Some((ub % n) as usize)
    }

    // 4. 特殊化三分探索
    pub fn ternary_search_max(&self, axis_first: (f64, f64), axis_last: (f64, f64)) -> Option<usize> {
        if self.polygon_index.length == 0 { return None; }
        let n = self.polygon_index.length;
        if n == 1 { return Some(0); }

        // axis ベクトルの計算を内部でインライン化 (unit=True)
        let mut dx = axis_last.0 - axis_first.0;
        let mut dy = axis_last.1 - axis_first.1;
        if dx != 0.0 || dy != 0.0 {
            let l = (dx*dx + dy*dy).sqrt();
            dx /= l;
            dy /= l;
        }
        let axis = (dx, dy);

        let evfunc = |logical_idx: isize| -> f64 {
            let pt_idx = self.polygon_index.__getitem__(logical_idx) as usize;
            let pt = self.points[pt_idx];
            let v_x = pt.0 - axis_last.0;
            let v_y = pt.1 - axis_last.1;
            dot_product(axis, (v_x, v_y))
        };

        let mut low = 0isize;
        let mut high = (n - 1) as isize;

        if high - low > 2 {
            let m1 = low + (high - low) / 3;
            let m2 = low + ((high - low) << 1) / 3;
            if evfunc(low) >= evfunc(m1) && evfunc(m2) <= evfunc(high) {
                low = m2 + 1;
                high = m1 + (n as isize) - 1;
            }
        }

        while high - low > 2 {
            let m1 = low + (high - low) / 3;
            let m2 = low + ((high - low) << 1) / 3;

            if evfunc(m1) < evfunc(m2) { low = m1 + 1; } 
            else if evfunc(m1) > evfunc(m2) { high = m2 - 1; } 
            else { low = m1 + 1; high = m2 - 1; }
        }

        if high > low {
            let mut maxix = low;
            for i in (low + 1)..=high {
                if evfunc(i) > evfunc(maxix) { maxix = i; }
            }
            return Some((maxix as usize) % n);
        }
        Some((low as usize) % n)
    }
	
	pub fn peak_distances(&self) -> (f64, f64, f64, f64) {
	    if self.points.len() <= 2 || self.polygon_index.length <= 2 {
	        return (0.0, 0.0, 0.0, 0.0);
	    }
		
		let axis_first = self.points[0];
		let axis_last = self.points[self.points.len() - 1]; // self.points[-1] に相当

		// axis の単位ベクトル化 (unit=True)
		let mut dx = axis_last.0 - axis_first.0;
		let mut dy = axis_last.1 - axis_first.1;
		let l = (dx * dx + dy * dy).sqrt();
		if l != 0.0 { dx /= l; dy /= l; }
		let axis = (dx, dy);

		// 垂直ベクトル群の計算 (perpvec, vec_neg をインライン化)
		let axis3 = (axis.1, -axis.0); // 90度時計回り回転
		let axis9 = (-axis3.0, -axis3.1); // 反転
		
		let fwpolyix = self.ternary_search_max(axis_first, axis_last).unwrap() as isize;

		let n_poly = self.polygon_index.length as isize;
		let bkpolyix = self.search_upper_bound(fwpolyix, fwpolyix + n_poly - 1, axis).unwrap() as isize;        

		let rtpolyix = self.search_upper_bound(fwpolyix, bkpolyix, axis9).unwrap() as isize;
		let ltpolyix = self.search_upper_bound(bkpolyix, fwpolyix, axis3).unwrap() as isize;
		
		// 各ピークの実際の座標を間接参照で一括取得 (self.polygon_point に相当)
		let pt_fw = self.points[self.polygon_index.__getitem__(fwpolyix) as usize];
		let pt_rt = self.points[self.polygon_index.__getitem__(rtpolyix) as usize];
		let pt_bk = self.points[self.polygon_index.__getitem__(bkpolyix) as usize];
		let pt_lt = self.points[self.polygon_index.__getitem__(ltpolyix) as usize];

		// 計算して4つのタプルとしてそのまま返す（セミコロンなしでreturn省略）
		(
		    (axis.0 * (pt_fw.0 - axis_last.0) + axis.1 * (pt_fw.1 - axis_last.1)).abs(),
		    (axis3.0 * (pt_rt.0 - axis_first.0) + axis3.1 * (pt_rt.1 - axis_first.1)).abs(),
		    ((-axis.0) * (pt_bk.0 - axis_first.0) + (-axis.1) * (pt_bk.1 - axis_first.1)).abs(),
		    (axis3.0 * (pt_lt.0 - axis_first.0) + axis3.1 * (pt_lt.1 - axis_first.1)).abs(),
		)
	}

}