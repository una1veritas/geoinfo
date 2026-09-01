'''
Created on 2025/07/24

@author: sin
'''

import pyproj
from pyproj.enums import WktVersion
import rdp
import shapefile

if __name__ == '__main__':
    
    fp_zip = r'N03-20230101_13_GML.zip'  # 東京都の行政区域ポリゴン
    fp_shp = r'polygon_rdp.shp'  # 出力ファイル
    fp_prj = r'polygon_rdp.prj'  # 出力ファイル
    sf_r = shapefile.Reader(fp_zip)
    sf_w = shapefile.Writer(fp_shp, shapeType=5)  # 5: ポリゴン
    
    poly = sf_r.shape(12)  # レコード12が新宿区
    coords = [coord for coord in poly.points]  # 頂点座標
    print(f'vertex={len(coords): >4}')  # 頂点数
    
    trans = pyproj.Transformer.from_crs(
        6668,  # 世界測地系2011（緯度経度）
        6677,  # 世界測地系2011の平面直角座標系第9系（m）
        always_xy=True
        )
    coords_trans = trans.transform(*list(zip(*coords)))  # 座標変換
    # for x, y in list(zip(*coords_trans)):
    #     print(x,y)
    
    list_epsilon = [0, 1, 5, 20, 100]  # ε リスト
    sf_w.field('epsilon', 'N')  # フィールド追加
    
    for epsilon in list_epsilon:
    
        # 間引き
        coords_rdp = rdp.rdp(
            list(zip(*coords_trans)),
            epsilon=epsilon
            )
    
        sf_w.poly([coords_rdp])  # ジオメトリ書き込み
        sf_w.record(epsilon)  # 属性書き込み
        print(f'epsilon={epsilon: >3}, vertex={len(coords_rdp): >4}')
    sf_w.close()
    
    # 座標系ファイル作成
    with open(fp_prj, 'w') as f:
        wkt = pyproj.CRS.from_epsg(6677).to_wkt(WktVersion.WKT1_GDAL)
        f.write(wkt)
