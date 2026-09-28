import os
import zipfile
import xml.etree.ElementTree as ET

# --- パス設定 ---
zip_dir = "/Users/sin/Downloads/FG-GML-kyushu_okinawa-ALL1-20260701-Z001"
zip_file = "FG-GML-362430-ALL-20250701.zip"
zip_path = os.path.join(zip_dir, zip_file)

NS = {
    'gml': 'http://www.opengis.net/gml/3.2',
    'fgd': 'http://xml.gsi.go.jp/mfd/2013/dataset'
}

city_dict = {}

# ----------------------------------------------------
# 1. ZIP内の全自治体コード・名称の取得
# ----------------------------------------------------
with zipfile.ZipFile(zip_path, 'r') as z:
    for filename in z.namelist():
        if filename.endswith(".xml") and not filename.startswith("fmdid"):
            with z.open(filename) as f:
                try:
                    tree = ET.parse(f)
                    root = tree.getroot()
                    
                    # XML内の全要素から admCode と name を全探索
                    for elem in root.iter():
                        code_val = None
                        name_val = None
                        
                        # 子要素の <fgd:admCode>
                        c_elem = elem.find('fgd:admCode', NS)
                        if c_elem is not None and c_elem.text:
                            code_val = c_elem.text
                        
                        # 属性の admCode
                        if not code_val:
                            code_val = elem.attrib.get('admCode') or elem.attrib.get('{http://xml.gsi.go.jp/mfd/2013/dataset}admCode')

                        # 名称
                        n_elem = elem.find('fgd:name', NS)
                        if n_elem is not None and n_elem.text:
                            name_val = n_elem.text

                        if code_val:
                            name_str = name_val if name_val else "名称なし"
                            if code_val not in city_dict or city_dict[code_val] == "名称なし":
                                city_dict[code_val] = name_str
                except Exception:
                    continue

print("=== 検出された自治体コード一覧 ===")
if city_dict:
    for code, name in sorted(city_dict.items()):
        print(f"  コード: {code}  ->  {name}")
else:
    print("  ※このメッシュ（362430）には自治体コード（admCode）タグが含まれていません。")
print("===================================\n")


# ----------------------------------------------------
# 2. 座標点列の抽出
# ----------------------------------------------------
# コード一覧が存在する場合はその第一要素、ない場合は全線を抽出対象にする
target_city_code = list(city_dict.keys())[0] if city_dict else None

results = []

with zipfile.ZipFile(zip_path, 'r') as z:
    for filename in z.namelist():
        # 行政区画、海岸線、水涯線などを対象
        if any(k in filename for k in ["Adm", "Cstline", "WL"]) and filename.endswith(".xml"):
            with z.open(filename) as f:
                try:
                    tree = ET.parse(f)
                    root = tree.getroot()

                    for elem in root:
                        # コードが存在し、かつ指定コードと異なる場合はスキップ
                        c_elem = elem.find('fgd:admCode', NS)
                        elem_code = c_elem.text if (c_elem is not None and c_elem.text) else elem.attrib.get('admCode')
                        
                        if target_city_code and elem_code and elem_code != target_city_code:
                            continue

                        # 座標（posList）を取得
                        pos_list_elem = elem.find('.//gml:posList', NS)
                        if pos_list_elem is not None and pos_list_elem.text:
                            tag_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                            type_elem = elem.find('fgd:type', NS)
                            bound_type = type_elem.text if type_elem is not None else tag_name
                            
                            # (経度, 緯度) の点列配列に変換
                            raw_coords = list(map(float, pos_list_elem.text.strip().split()))
                            coords = [(raw_coords[i+1], raw_coords[i]) for i in range(0, len(raw_coords), 2)]
                            
                            results.append({
                                "file": filename,
                                "type": bound_type,
                                "coords": coords
                            })
                except Exception:
                    continue

# ----------------------------------------------------
# 3. 抽出結果の表示
# ----------------------------------------------------
target_name = city_dict.get(target_city_code, "指定なし（メッシュ内全線分）") if target_city_code else "コード情報なし（全線分）"
print(f"【 抽出結果: {target_name} 】")
print(f" 抽出された線分要素数: {len(results)} 件\n")

for i, item in enumerate(results[:3]):
    print(f"--- 線分 {i+1} [ファイル: {item['file']} / 種別: {item['type']}] ---")
    print(f" 点数: {len(item['coords'])}")
    print(f" 先頭3点 (経度, 緯度): {item['coords'][:3]}\n")
