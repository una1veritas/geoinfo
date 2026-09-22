use pyo3::prelude::*;

#[pyclass]
pub struct RingArray {
    array: Vec<i32>,    // 元の点のインデックス（int32型）を格納する動的配列
    capacity: usize,   // 常に2のべき乗
    head: usize,
    tail: usize,
    length: usize,
}

#[pymethods]
impl RingArray {
    #[new]
    fn new(initcapacity: Option<Py<PyAny>>) -> Self {
        let mut cap = 16;
        if let Some(obj) = initcapacity {
            let py = unsafe { Python::assume_attached() };
            // PyObject(Py<PyAny>) から usize を安全に抽出する現代の書き方
            if let Ok(val) = obj.extract::<usize>(py) {
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
        }
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
        // 負のインデックスやPython特有の丸めに対応
        let idx = if index < 0 {
            (self.length as isize + (index % self.length as isize)) as usize
        } else {
            (index as usize) % self.length
        };
        let pos = (self.head + idx) & (self.capacity - 1);
        self.array[pos]
    }

    // --- ここから爆速の探索ロジック群 ---

    /// 二分探索（間接参照版）
    /// points: 元の二次元点のリスト [(x, y), ...]
    /// mode: 0ならX座標で比較、1ならY座標で比較（あるいは凸包の評価関数をここに内蔵させます）
    fn binary_search_upper_bound(
        &self, 
        mut lb: isize, 
        mut ub: isize, 
        value: f64, 
        points: Vec<(f64, f64)>,
        mode: i32
    ) -> Option<usize> {
        if self.length == 0 { return None; }
        
        if lb >= self.length as isize || ub < lb {
            lb = lb.rem_euclid(self.length as isize);
            ub = ub.rem_euclid(self.length as isize);
            if ub < lb { ub += self.length as isize; }
        }

        // 評価関数をクロージャ（インライン関数）として定義
        let evfunc = |logical_idx: isize| -> f64 {
            let pt_idx = self.__getitem__(logical_idx) as usize;
            let pt = points[pt_idx];
            if mode == 0 { pt.0 } else { pt.1 } // 0ならX, 1ならYを返す（実際は幾何計算に変更可能）
        };

        while lb < ub {
            let mix = lb + ((ub - lb) >> 1);
            if evfunc(mix) < value {
                lb = mix + 1;
            } else {
                ub = mix;
            }
        }
        Some((ub as usize) % self.length)
    }

    /// 三分探索（間接参照版）
    fn ternary_search_max(&self, points: Vec<(f64, f64)>, mode: i32) -> Option<usize> {
        if self.length == 0 { return None; }
        let n = self.length;
        if n == 1 { return Some(0); }

        // 内部評価関数：デックの論理インデックスから元の点を取り出し、その座標(値)を返す
        let evfunc = |logical_idx: isize| -> f64 {
            let pt_idx = self.__getitem__(logical_idx) as usize;
            let pt = points[pt_idx];
            if mode == 0 { pt.0 } else { pt.1 } // 必要に応じて凸包の外積計算等に差し替え
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

            if evfunc(m1) < evfunc(m2) {
                low = m1 + 1;
            } else if evfunc(m1) > evfunc(m2) {
                high = m2 - 1;
            } else {
                low = m1 + 1;
                high = m2 - 1;
            }
        }

        if high > low {
            let mut maxix = low;
            for i in (low + 1)..=high {
                if evfunc(i) > evfunc(maxix) {
                    maxix = i;
                }
            }
            return Some((maxix as usize) % n);
        }

        Some((low as usize) % n)
    }
}

// 内部用の容量拡張メソッド
impl RingArray {
    fn double_capacity(&mut self) {
        let old_cap = self.capacity;
        // 配列を2倍に拡張
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
