デジタル地図の情報を使うプロジェクトのレポジトリ

geograph --- Open Street Map を CSV に変換したファイルを読み込みポイントをノード，道路を辺とするグラフを作製，また GPS の軌跡を読み込み操作する C++ (2x)プログラム．Geohash のバイナリー拡張版の自家製 C++ ライブラリ bingeohash.h を含む． 
openstreetmap/OSMReader --- .osm 形式の地図ファイルを geograph で扱える CSV 形式 (.geo) に変換する Python3.x プログラム. 
Geohash --- Python で書いた Geohash を扱うプログラムのコード．
myTracks --- iアプリでログをとった GPS 軌跡データ .gpx を CSV ファイルに変換する Python プログラム．geograph で使う場合は -mjd オプションで日付時刻を MJD 日と秒の表示にする．
