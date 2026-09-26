// rust 側での実装イメージ (src/lib.rs や対応するモジュール)
use pyo3::prelude::*;
use crate::convex_hull::ConvexHull; // 自作の ConvexHull

#[pyfunction]
#[pyo3(signature = (xy, epsilon, record_polygons = false))]
pub fn grow_hull(
    xy: Vec<(f64, f64)>,
    epsilon: f64,
    record_polygons: bool,
) -> (Vec<usize>, Option<Vec<Vec<(f64, f64)>>>) {
    let mut decpath: Vec<usize> = Vec::new();
    
    // ポリゴン記録用ベクタの初期化
    let mut polygons = if record_polygons {
        Some(Vec::new())
    } else {
        None
    };
    
    // 1. 最初の点を追加
    decpath.push(0);
    let mut cvx = ConvexHull::new();
	cvx.add(xy[0]);
	cvx.add(xy[1]);
    let mut start_ix = decpath[0];
    
    if let Some(ref mut polys) = polygons {
        polys.push(cvx.polygon_points());
    }
    
    //let mut ix = 1;
	for ix in 2..xy.len() {
        if cvx.add(xy[ix]) {
            let peak_dists = cvx.peak_distances();
            // 4つのピーク距離のタプル (d1, d2, d3, d4) の最大値が epsilon を超えるかチェック
            let max_dist = peak_dists.0.max(peak_dists.1).max(peak_dists.2).max(peak_dists.3);

            if max_dist > epsilon {
                // キャンセル処理（最後に追加した分を戻す）
                let last_ix = ix - 1;
                decpath.push(last_ix);
                cvx.clear();
                start_ix = last_ix;

                cvx.add(xy[start_ix]);
                cvx.add(xy[start_ix + 1]);

                if let Some(ref mut polys) = polygons {
                    polys.push(cvx.polygon_points());
                }
				
            //    ix += 1;
            //    continue;
            } else {	
	            if let Some(ref mut polys) = polygons {
	                if let Some(last_poly) = polys.last_mut() {
	                    *last_poly = cvx.polygon_points(); // 更新
	                }
	            }
            //ix += 1;
			}
        } else {
			// 却下された場合の処理
            let last_ix = ix - 1;
            decpath.push(last_ix);
            cvx.clear();
            start_ix = *decpath.last().unwrap();
            
            cvx.add(xy[start_ix]);
            cvx.add(xy[ix]);
            
            if let Some(ref mut polys) = polygons {
                polys.push(cvx.polygon_points());
            }
            //ix += 1;
            //continue;
        }
    }
	    
    if cvx.len() > 0 {
        // 最後の線分を追加
        let last_ix = start_ix + cvx.len() - 1;
        decpath.push(last_ix);
        
        if let Some(ref mut polys) = polygons {
            polys.push(cvx.polygon_points());
        }
    }    
    (decpath, polygons)
}