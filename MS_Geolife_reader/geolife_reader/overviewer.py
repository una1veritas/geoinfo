
import os
import glob
import pandas as pd

# ユーザーの環境に合わせてルートパスを設定してください
base_dir = '/Users/sin/Downloads/Geolife Trajectories 1.3/Data'

def analyze_geolife_points(root_path):
    file_stats = []
    
    # 全ユーザーの Trajectory フォルダ内の .plt ファイルを探索
    search_path = os.path.join(root_path, '*', 'Trajectory', '*.plt')
    plt_files = glob.glob(search_path)
    
    print(f"総ファイル数: {len(plt_files)} 個の解析を開始します...")
    
    for file_path in plt_files:
        # パスからユーザーIDとファイル名を取得
        parts = file_path.split(os.sep)
        user_id = parts[-3]  # '000' など
        file_name = parts[-1] # '20081103232153.plt' など
        
        try:
            with open(file_path, 'r', errors='ignore') as f:
                # 高速に行数をカウント
                row_count = sum(1 for _ in f)
                
            # 先頭6行はヘッダーなので、データ点数は row_count - 6
            data_points = max(0, row_count - 6)
            
            file_stats.append({
                'user_id': user_id,
                'file_name': file_name,
                'points': data_points,
                'path': file_path
            })
        except Exception as e:
            print(f"エラー（スキップします）: {file_name} - {e}")
            
    # データフレームに変換して統計を出す
    df = pd.DataFrame(file_stats)
    return df

if __name__ == '__main__':
    if not os.path.exists(base_dir):
        print(f"エラー: パスが見つかりません。設定を確認してください: {base_dir}")
    else:
        df_stats = analyze_geolife_points(base_dir)
        
        # --- 統計情報の表示 ---
        print("\n=== Geolife データ点数 統計 ===")
        print(f"総データ点数（全ファイル合計）: {df_stats['points'].sum():,} 点")
        print(f"1ファイルあたりの平均点数: {df_stats['points'].mean():.1f} 点")
        print(f"最大点数のファイル: {df_stats['points'].max():,} 点")
        print(f"最小点数のファイル: {df_stats['points'].min():,} 点")
        
        # --- 実験用に使いやすいファイルの抽出例 ---
        print("\n=== 論文実験用：おすすめファイル（点数が1,000〜5,000点）の例 ===")
        filtered_df = df_stats[(df_stats['points'] >= 1000) & (df_stats['points'] <= 5000)]
        print(f"条件にマッチしたファイル数: {len(filtered_df)} 個")
        
        # サンプルとして最初の5件を表示
        for idx, row in filtered_df.head(5).iterrows():
            print(f"User: {row['user_id']} | File: {row['file_name']} | 点数: {row['points']}点")
            
        # 結果をCSVに保存しておくと後でファイルを選びやすくなります
        df_stats.to_csv("geolife_file_summary.csv", index=False)
        print("\n全ファイルの集計結果を 'geolife_file_summary.csv' に保存しました。")
