'''
Created on 2026/09/28
@author: sin
'''

import os
import geopandas as gpd

def area():
    # 経度・緯度からメートル単位の座標系に変換して面積を計算する例
    fukuoka_city_projected = fukuoka_city_gdf.to_crs(epsg=6670)
    total_area_km2 = fukuoka_city_projected.geometry.area.sum() / 1000000
    print(f"福岡市の総面積: {total_area_km2:.2f} km²")

def big_area():
    # 面積（度単位の概算）が一定以上のポリゴンのみ抽出
    main_polygons = [ea for ea in all_boundaries if ea["geometry"].area > 0.0001]

def unite_polygon():
    # 福岡市東区の全ポリゴンを1つの MultiPolygon に融合
    united_geom = city_gdf.geometry.unary_union

def epsg(): # EPSG:6670（メートル単位）に投影変換
    city_gdf_m = city_gdf.to_crs(epsg=6670)
    
    # 各ポリゴンの面積（平方メートル）
    for geom in city_gdf_m.geometry.explode(index_parts=False):
        print(f"面積: {geom.area:.1f} m²")

def concatenate():
    # import geopandas as gpd
    # import os
    
    # 九州全県のGeoJSON（または全国GeoJSON）を読み込む
    # 国土数値情報から「九州各県」のGeoJSONをダウンロードして結合、または全国版を使用
    geojson_path = "N03-23_Kyushu_ALL.geojson" # 例: 九州全域のデータ
    gdf = gpd.read_file(geojson_path)
    
    # 1. 九州本島の県を指定して抽出（島嶼部を除外するため最大のポリゴンを取得）
    kyushu_gdf = gdf[gdf["N03_001"].isin(["福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県"])]
    
    # 2. 全行政境界を融合（溶接）して1つのMultiPolygonにする
    united_geom = kyushu_gdf.geometry.unary_union
    
    # 3. 融合結果の中から「最も面積が大きいポリゴン（＝九州本島）」を取り出す
    main_island_polygon = max(united_geom.geoms, key=lambda p: p.area)
    
    # 4. 単一ポリゴンの外周点列を取得
    coords = list(main_island_polygon.exterior.coords)
    
    print(f"=== 九州本島 単一外周ポリゴン ===")
    print(f"単一ポリゴンの頂点数: {len(coords):,} 点")

gml_dir = "/Users/sin/Downloads/N03-20230101_47_GML"
geojson_file = "N03-23_47_230101.geojson"
geojson_path = os.path.join(gml_dir, geojson_file)

# GeoJSON読み込み（福岡県全体のデータ）
gdf = gpd.read_file(geojson_path)


def get_boundaries(target_gdf):
    """GeoDataFrameからPolygon要素を分解して点列を取り出す関数"""
    exploded_gdf = target_gdf.explode(index_parts=False)
    boundaries = []
    
    for idx, row in exploded_gdf.iterrows():
        geom = row.geometry
        if geom is not None and geom.geom_type == 'Polygon':
            coords = list(geom.exterior.coords)
            boundaries.append({
                "city_code": row.get("N03_007", ""),
                "city_name": row.get("N03_004", "") or row.get("N03_001", ""),
                "point_count": len(coords),
                "coords": coords,
                "geometry": geom  # Shapelyオブジェクト（幾何計算用）
            })
    return boundaries


# ----------------------------------------------------
# 1. 福岡市全体（東区・博多区・中央区・南区・西区・城南区・早良区）
# ----------------------------------------------------
# N03_003 カラムが "福岡市" のものを抽出
fukuoka_city_gdf = gdf[gdf["N03_003"] == "石垣市"]
city_boundaries = get_boundaries(fukuoka_city_gdf)

print(f"【石垣市全体】抽出ポリゴン数: {len(city_boundaries)} 個")
for ea in sorted(city_boundaries, key = lambda e: e['point_count'], reverse=True)[:10]:  # 先頭3件表示
    print(f'  {ea["city_name"]}, 点数: {ea["point_count"]}, 先頭2点: {ea["coords"][:2]}')


# ----------------------------------------------------
# 2. 福岡県全体（すべての市町村・島嶼部を含む）
# ----------------------------------------------------
# N03_001 カラムが "福岡県" のものを抽出（ファイル内の全要素）
fukuoka_pref_gdf = gdf[gdf["N03_001"] == "沖縄県"]
pref_boundaries = get_boundaries(fukuoka_pref_gdf)

print(f"\n【沖縄県県全体】抽出ポリゴン数: {len(pref_boundaries)} 個")
for ea in sorted(pref_boundaries, key = lambda e: e['point_count'], reverse=True)[:10]:  # 先頭3件表示
    print(f'  {ea["city_name"]}, 点数: {ea["point_count"]}, 先頭2点: {ea["coords"][:2]}')
