use pyo3::prelude::*;

#[pyclass]
pub struct RingArray {
    pub array: Vec<i32>,    // 外部（convex_hull）から中身を読めるように pub をつける
    pub capacity: usize,
    pub head: usize,
    pub tail: usize,
    pub length: usize,
}

#[pymethods]
impl RingArray {
    #[pyo3(signature = (initcapacity=None))]
    #[new]
    pub fn new(initcapacity: Option<Py<PyAny>>) -> Self {
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
        }
    }

    pub fn __len__(&self) -> usize { self.length }
    pub fn clear(&mut self) { self.head = 0; self.tail = 0; self.length = 0; }

    pub fn append(&mut self, elem: i32) {
        if self.length >= self.capacity { self.double_capacity(); }
        self.array[self.tail] = elem;
        self.tail = (self.tail + 1) & (self.capacity - 1);
        self.length += 1;
    }

    pub fn appendleft(&mut self, elem: i32) {
        if self.length >= self.capacity { self.double_capacity(); }
        self.head = (self.head + self.capacity - 1) & (self.capacity - 1);
        self.array[self.head] = elem;
        self.length += 1;
    }

    pub fn pop(&mut self) -> PyResult<i32> {
        if self.length > 0 {
            self.tail = (self.tail + self.capacity - 1) & (self.capacity - 1);
            self.length -= 1;
            Ok(self.array[self.tail])
        } else {
            Err(pyo3::exceptions::PyValueError::new_err("tried pop to empty queue"))
        }
    }

    pub fn popleft(&mut self) -> PyResult<i32> {
        if self.length > 0 {
            let val = self.array[self.head];
            self.head = (self.head + 1) & (self.capacity - 1);
            self.length -= 1;
            Ok(val)
        } else {
            Err(pyo3::exceptions::PyValueError::new_err("tried pop to empty queue"))
        }
    }

    pub fn __getitem__(&self, index: isize) -> i32 {
        let idx = if index < 0 {
            (self.length as isize + (index % self.length as isize)) as usize
        } else {
            (index as usize) % self.length
        };
        let pos = (self.head + idx) & (self.capacity - 1);
        self.array[pos]
    }
}

// 内部用の容量拡張（C-style の関数。外部に露出させない）
impl RingArray {
    fn double_capacity(&mut self) {
        let old_cap = self.capacity;
        self.array.resize(old_cap * 2, 0);
        if self.tail <= self.head {
            for ix in 0..self.tail { self.array[old_cap + ix] = self.array[ix]; }
            self.tail += old_cap;
        }
        self.capacity <<= 1;
    }
}
