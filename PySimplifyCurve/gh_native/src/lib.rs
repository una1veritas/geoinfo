use pyo3::prelude::*;

// 1. 外部ファイル（子モジュール）を宣言して引き込む
mod ring_array;
mod convex_hull;
mod grow_hull;

// 2. Pythonから直接 import できるように登録する
#[pymodule]
fn gh_native(m: &Bound<'_, PyModule>) -> PyResult<()> {
	// ConvexHull クラスの登録など（既存のコード）
    m.add_class::<convex_hull::ConvexHull>()?;
    m.add_class::<ring_array::RingArray>()?;
    
    // グローバル関数 grow_hull の登録
    m.add_function(wrap_pyfunction!(grow_hull::grow_hull, m)?)?;
    
    Ok(())
}
