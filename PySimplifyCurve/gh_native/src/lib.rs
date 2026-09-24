use pyo3::prelude::*;

#[pyclass]
pub struct RingArray {
    array: Vec<i32>,           // 凸包の頂点インデックス（polygon_index に相当）
    capacity: usize,          // 常に2のべき乗
    head: usize,
    tail: usize,
    length: usize,
    points: Vec<(f64, f64)>,  // 元の二次元平面上の点の座標リスト（self.points に相当）
}

#[pymethods]
impl RingArray {
    // 引数なし、または初期容量を指定して初期化
    #[pyo3(signature = (initcapacity=None))]
    #[new]
    fn new(initcapacity: Option<Py<PyAny>>) -> Self {
        let mut cap = 16;
        if let Some(obj) = initcapacity {
            let py = unsafe { Python::assume_attached() };
            if let Ok(val) = obj.bind(py).extract::<usize>() {
                if val > 16 {
                    cap = 1 << ((val - 1) as f64).log2().ceil() as usize;
                }
            }
        }

        RingArray {
            array: vec![0; cap],
            capacity: cap,
            head: 0,
            tail: 0,
            length: 0,
            points: Vec::new(), // 最初は空で初期化
        }
    }

    // 元の点の座標リストを一括でセットするメソッド（Python側の初期化時などに呼ぶ）
    fn set_points(&mut self, points: Vec<(f64, f64)>) {
        self.points = points;
    }

    fn __len__(&self) -> usize {
        self.length
    }

    fn clear(&mut self) {
        self.head = 0;
        self.tail = 0;
        self.length = 0;
    }

    // 末尾追加 (append)
    fn append(&mut self, elem: i32) {
        if self.length >= self.capacity {
            self.double_capacity();
        }
        self.array[self.tail] = elem;
        self.tail = (self.tail + 1) & (self.capacity - 1);
        self.length += 1;
    }

    // 先頭追加 (appendleft)
    fn appendleft(&mut self, elem: i32) {
        if self.length >= self.capacity {
            self.double_capacity();
        }
        self.head = (self.head + self.capacity - 1) & (self.capacity - 1);
        self.array[self.head] = elem;
        self.length += 1;
    }

    // 末尾削除 (pop)
    fn pop(&mut self) -> PyResult<i32> {
        if self.length > 0 {
            self.tail = (self.tail + self.capacity - 1) & (self.capacity - 1);
            self.length -= 1;
            Ok(self.array[self.tail])
        } else {
            Err(pyo3::exceptions::PyValueError::new_err("tried pop to empty queue"))
        }
    }

    // 先頭削除 (popleft)
    fn popleft(&mut self) -> PyResult<i32> {
        if self.length > 0 {
            let val = self.array[self.head];
            self.head = (self.head + 1) & (self.capacity - 1);
            self.length -= 1;
            Ok(val)
        } else {
            Err(pyo3::exceptions::PyValueError::new_err("tried pop to empty queue"))
        }
    }

    // ランダムアクセス (buf[index])
    fn __getitem__(&self, index: isize) -> i32 {
        let idx = if index < 0 {
            (self.length as isize + (index % self.length as isize)) as usize
        } else {
            (index as usize) % self.length
        };
        let pos = (self.head + idx) & (self.capacity - 1);
        self.array[pos]
    }

    // 1. 【完全特殊化版】辺のベクトルと軸ベクトルの内積を用いた最速二分探索
    // Python側の search_upper_bound(self, lb, ub, paraxis) と完全に一致します
    fn search_upper_bound(
        &self,
        mut lb: isize,
        mut ub: isize,
        paraxis: (f64, f64)
    ) -> Option<usize> {
        if self.length == 0 { return None; }
        let n = self.length as isize;

        if lb >= n {
            lb = lb % n;
        }
        if lb > ub {
            ub = (ub % n) + n;
        }

        while lb < ub {
            let mix = lb + ((ub - lb) >> 1);
            
            // mix と mix+1 の論理インデックスから元の点のインデックスを引く
            let idx_curr = self.__getitem__(mix) as usize;
            let idx_next = self.__getitem__(mix + 1) as usize;
            
            // それぞれの座標を取得
            let pt_curr = self.points[idx_curr];
            let pt_next = self.points[idx_next];
            
            // 辺ベクトルを計算：vec(self_points[...mix], self_points[...mix+1])
            let vec_x = pt_next.0 - pt_curr.0;
            let vec_y = pt_next.1 - pt_curr.1;
            
            // 軸ベクトル paraxis との内積（dot_product）を計算
            let dot = paraxis.0 * vec_x + paraxis.1 * vec_y;

            if dot < 0.0 {
                lb = mix + 1;
            } else {
                ub = mix;
            }
        }

        Some((ub % n) as usize)
    }

    // 2. 特殊化三分探索（軸に沿った最遠点（内積最大）を求める）
    fn ternary_search_max_projection(&self, p0: (f64, f64), v: (f64, f64)) -> Option<usize> {
        if self.length == 0 { return None; }
        let n = self.length;
        if n == 1 { return Some(0); }

        let evfunc = |logical_idx: isize| -> f64 {
            let pt_idx = self.__getitem__(logical_idx) as usize;
            let pt = self.points[pt_idx];
            let dx = pt.0 - p0.0;
            let dy = pt.1 - p0.1;
            dx * v.0 + dy * v.1
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
}

impl RingArray {
    fn double_capacity(&mut self) {
        let old_cap = self.capacity;
        self.array.resize(old_cap * 2, 0);
        if self.tail <= self.head {
            for ix in 0..self.tail {
                self.array[old_cap + ix] = self.array[ix];
            }
            self.tail += old_cap;
        }
        self.capacity <<= 1;
    }
}

#[pymodule]
fn gh_native(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<RingArray>()?;
    Ok(())
}
